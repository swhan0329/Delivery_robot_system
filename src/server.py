import time
import traceback, sys
import random
from sys import *
import socket
import cv2
import numpy as np
import pygame
import time
import keyboard
import json
import queue
from threading import Thread
import csv
import pickle
import os.path

import pyqtgraph as pg
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from route_Priority_0206 import *
from decision_utils import makeFullyConnectedGraph, address_validator
from WSClientAPI import *

from Detection_green import *


form_class = uic.loadUiType("./resource/GUI.ui")[0]


class ThreadedCamera(object):
    def __init__(self, source=0):

        self.capture = cv2.VideoCapture(source)

        self.thread = Thread(target=self.update, args=())
        self.thread.daemon = True
        self.thread.start()

        self.status = False
        self.frame = None

    def update(self):
        while True:
            if self.capture.isOpened():
                (self.status, self.frame) = self.capture.read()

    def grab_frame(self):
        if self.status:
            return self.frame
        return None


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    progress
        `int` indicating % progress

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(int)


class Worker(QRunnable):
    '''
    Worker thread

    Inherits from QRunnable to handler worker thread setup, signals and wrap-up.

    :param callback: The function callback to run on this worker thread. Supplied args and
                     kwargs will be passed through to the runner.
    :type callback: function
    :param args: Arguments to pass to the callback function
    :param kwargs: Keywords to pass to the callback function

    '''

    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()

        # Store constructor arguments (re-used for processing)
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        self.signals = WorkerSignals()

        # Add the callback to our kwargs
        self.kwargs['progress_callback'] = self.signals.progress

    @pyqtSlot()
    def run(self):
        '''
        Initialise the runner function with passed args, kwargs.
        '''

        # Retrieve args/kwargs here; and fire processing using them
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()  # Done


class MainWindow(QMainWindow, form_class):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.setupUi(self)
        #######initialize#######
        # todo
        self.network_status = 0


        # done
        #self.total_package_delivered__num = 0
        self.total_complete_order_num = 0
        self.maintenance_mode_value = 0

        self.current_state = 0
        self.next_delivery_address_num = 0

        self.distance_num = 0
        self.next_red_num = 0
        self.next_blue_num = 0
        self.next_green_num = 0
        self.image = np.ones((5,5,1))
        self._prev_list_len = 0
        self.red_num = 26
        self.blue_num = 26
        self.green_num = 26

        if os.path.isfile('_data_log.pickle'):
            print("load log data from pickle")
            with open('_data_log.pickle', 'rb') as handle:
                [self.y1, self.y2, self.y3, self.battery_num, self.routeDecision] = pickle.load(handle)

        else:
            print("there is no pickle file, fresh start")
            self.y1 = [0]
            self.y2 = [0]
            self.y3 = [0]
            self.battery_num = 100
            path, cost = makeFullyConnectedGraph()
            self.routeDecision = RouteDecision(path, cost)

        #####graph initialize#####
        hbox1 = QHBoxLayout()
        self.pw1 = pg.PlotWidget(title="Accumulated order per time")
        self.pw1.setLabel('left', 'The number of items')
        self.pw1.setLabel('bottom', 'Time', units='s')
        self.pw1.showGrid(x=True, y=True)  # show the grid
        hbox1.addWidget(self.pw1)
        self.graph1.setLayout(hbox1)
        hbox2 = QHBoxLayout()
        self.pw2 = pg.PlotWidget(title="Backlog(time to done) per order")
        self.pw2.setLabel('left', 'Time', units='s')
        self.pw2.setLabel('bottom', 'Item')
        self.pw2.showGrid(x=True, y=True)  # show the grid
        hbox2.addWidget(self.pw2)
        self.graph2.setLayout(hbox2)
        hbox3 = QHBoxLayout()
        self.pw3 = pg.PlotWidget(title="Rest order number per time")
        self.pw3.setLabel('left', 'The number of items')
        self.pw3.setLabel('bottom', 'Time', units='s')
        self.pw3.showGrid(x=True, y=True)  # show the grid
        hbox3.addWidget(self.pw3)
        self.graph3.setLayout(hbox3)

        self.x = [0]

        self.x_bar = [0]

        self.start_button.pressed.connect(self._main_program)

        self.threadpool = QThreadPool()
        print("Multithreading with maximum %d threads" % self.threadpool.maxThreadCount())

        self.timer = QTimer()
        self.timer.setInterval(500)
        self.timer.timeout.connect(self.recurring_updater)
        self.timer.start()

        self.counter = 0

        self.debug = False
        self.show()

        # For client <- worker connection
        self.ctrl_port_1 = 8011
        self.ctrconn = self.init_socket(self.ctrl_port_1)
        self.ctrconn.setblocking(0)

        # For client -> worker connection
        self.ctrl_port_2 = 8091
        self.ConnectTo_ctrl = '128.237.173.74'  # controller(DY's laptop) ip

        # For client -> rasbpi connection
        self.pi_port = 8089
        self.ConnectTo = '172.26.226.16'  # rasbpi ip

        # initial setting
        width = 640
        height = 480
        stream_link = "http://rpi-9.wifi.local.cmu.edu:3030/video_feed"
        self.streamer = ThreadedCamera(stream_link)
        pygame.init()

    def update_maintenance_mode(self):
        if self.maintenance_mode_value:
            self.maintenance_mode_status.setText("On")
            self.maintenance_mode_status.setFont(QtGui.QFont("Gulim", 25, QtGui.QFont.Bold))
            self.maintenance_mode_status.setStyleSheet('color: blue')
        else:
            self.maintenance_mode_status.setText("Off")
            self.maintenance_mode_status.setFont(QtGui.QFont("Gulim", 25, QtGui.QFont.Bold))
            self.maintenance_mode_status.setStyleSheet('color: red')


    def update_network_change_status(self):
        if self.network_status:
            self.network_status_value.setText("Connect")
            self.network_status_value.setFont(QtGui.QFont("Gulim", 10, QtGui.QFont.Bold))
            self.network_status_value.setStyleSheet('color: blue')
        else:
            self.network_status_value.setText("Disconnect")
            self.network_status_value.setFont(QtGui.QFont("Gulim", 10, QtGui.QFont.Bold))
            self.network_status_value.setStyleSheet('color: red')

    def update_inventory_status(self):
        self.red_value.setText(str(self.red_num))
        self.red_value.setFont(QtGui.QFont("Gulim", 15, QtGui.QFont.Bold))
        self.red_value.setStyleSheet('color: red')
        self.blue_value.setText(str(self.blue_num))
        self.blue_value.setFont(QtGui.QFont("Gulim", 15, QtGui.QFont.Bold))
        self.blue_value.setStyleSheet('color: blue')
        self.green_value.setText(str(self.green_num))
        self.green_value.setFont(QtGui.QFont("Gulim", 15, QtGui.QFont.Bold))
        self.green_value.setStyleSheet('color: green')

    def update_next_delivery_address(self):
        if self.next_delivery_address_num == "stop":
            self.next_delivery_address_value.display(0)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: red; }""")
        elif self.next_delivery_address_num == "101":
            self.next_delivery_address_value.display(101)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == "102":
            self.next_delivery_address_value.display(102)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == "103":
            self.next_delivery_address_value.display(103)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == "203":
            self.next_delivery_address_value.display(203)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == "202":
            self.next_delivery_address_value.display(202)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == "201":
            self.next_delivery_address_value.display(201)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")

    def update_next_delivery_list(self):
        self.next_red_value.setText(str(self.next_red_num))
        self.next_red_value.setFont(QtGui.QFont("Gulim", 15, QtGui.QFont.Bold))
        self.next_red_value.setStyleSheet('color: red')
        self.next_blue_value.setText(str(self.next_blue_num))
        self.next_blue_value.setFont(QtGui.QFont("Gulim", 15, QtGui.QFont.Bold))
        self.next_blue_value.setStyleSheet('color: blue')
        self.next_green_value.setText(str(self.next_green_num))
        self.next_green_value.setFont(QtGui.QFont("Gulim", 15, QtGui.QFont.Bold))
        self.next_green_value.setStyleSheet('color: green')

    def update_total_package_delivered(self):
        self.total_complete_order_num = self.routeDecision.getNumCompletedOrders()

        self.total_package_delivered_value.display(self.total_complete_order_num)

    def update_remain_battery(self):
        self.remain_battery_value.display(self.battery_num)

    def update_distance_traveled(self):
        self.distance_traveled_value.display(self.distance_num)

    def update_robot_address(self):
        if self.current_state == 0:
            self.current_robot_address_value.display(0)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: red; }""")
        elif self.current_state == 1:
            self.current_robot_address_value.display(101)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.current_state == 2:
            self.current_robot_address_value.display(102)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.current_state == 3:
            self.current_robot_address_value.display(103)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.current_state == 4:
            self.current_robot_address_value.display(203)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.current_state == 5:
            self.current_robot_address_value.display(202)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.current_state == 6:
            self.current_robot_address_value.display(201)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")

    def update_image(self):
        self.qtimage = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.robot_view.setPixmap(QtGui.QPixmap.fromImage(self.qtimage))
        self.robot_view.setPixmap(QPixmap(self.qtimage).scaled(self.robot_view.width(), self.robot_view.height(), Qt.KeepAspectRatio))

    def draw_graph(self):
        self.x.append(self.x[-1] + 1)

        curr_inventory = self.routeDecision.getInventory()
        self.red_num = curr_inventory[0]
        self.blue_num = curr_inventory[1]
        self.green_num = curr_inventory[2]

        rest_order_num = self.routeDecision.getCurrentOrdersPending()
        total_order_num = self.routeDecision.getNumTotalOrders()
        delivery_t_list = self.routeDecision.getAllDeliveryTime()

        curr_list_len = len(delivery_t_list)

        if self._prev_list_len != curr_list_len:
            cnt = curr_list_len - self._prev_list_len
            for i in range(cnt):
                self.x_bar.append(self.x_bar[-1] + 1)
                self.y2.append(delivery_t_list[i - cnt])
        self._prev_list_len = len(delivery_t_list)

        self.y1.append(total_order_num)
        self.y3.append(rest_order_num)

        # accumulated order per time
        self.pw1.plot(x=self.x, y=self.y1, symbolPen='g', symbolBrush=0.2, name='green')

        # backlog(time to done) per order
        bar_chart = pg.BarGraphItem(x=self.x_bar, height=self.y2, width=1, brush='y', pen='r')
        self.pw2.addItem(bar_chart)

        # rest order number per time
        self.pw3.plot(x=self.x, y=self.y3, symbolPen='g', symbolBrush=0.2, name='green')

    def init_socket(self, port):
        host_name = socket.gethostname()
        # host_ip = socket.gethostbyname(socket.gethostname())
        host_ip = '128.237.116.190'
        print("client Hostname :  ", host_name)
        print("client IP: ", host_ip, " on port ", port)

        mwconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mwconn.bind((host_ip, port))
        mwconn.listen(3)

        return mwconn

    def displayOnPygame(self, frame):
        img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = img.swapaxes(0, 1)
        img = pygame.surfarray.make_surface(img)
        self.screen.blit(img, (0, 0))
        pygame.display.flip()

    def thread_complete(self):
        print("THREAD COMPLETE!")

    def recurring_updater(self):
        self.update_robot_address()
        self.update_next_delivery_address()
        self.update_next_delivery_list()
        self.update_remain_battery()
        self.update_distance_traveled()
        self.update_network_change_status()
        self.update_inventory_status()
        self.update_total_package_delivered()
        #self.update_image()
        self.update_maintenance_mode()
        self.draw_graph()

    def execute_this_fn(self, progress_callback):
        record = False

        try:
            if not self.debug:

                # screen = pygame.display.set_mode((width, height))

                # flags
                flag_server = False  # start with False
                flag_worker = False
                flag_start = False
                flag_waiting = False
                flag_measure_dist = False
                flag_non_pkg = False
                flag_battery = False

                MODE_maintenance = False
                global_start = False
                inspection = False
                maintenance_activation_count = 0

                # flags for robot
                robot_mode = "Stop"  # "Go"
                last_order = '1'
                curr_orientation = 'cc'  # 'c'
                order_to_robot = False
                action = '0'

                delivery_boxes_by_addr = None
                delivery_info_by_addr = None
                delivery_path = None
                remain_destination = []
                remain_pkg = []

                detection_class = Detection()

                start_time = time.time()
                prev_time = start_time

                if record:
                    fourcc = cv2.VideoWriter_fourcc(*'XVID')
                    out = cv2.VideoWriter('test_driving.avi', fourcc, 50.0, (320, 240))

                while True:
                    if self.battery_num < 50:
                        MODE_maintenance = True
                        flag_battery = True

                        maintenance_activation_count += 1
                        robot_mode = "Stop"

                        msg = dict(type="Mode", state=True)
                        msg = json.dumps(msg)
                        controllerconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        controllerconn.connect((self.ConnectTo_ctrl, self.ctrl_port_2))
                        controllerconn.send(msg.encode('ascii'))
                        controllerdata = controllerconn.recv(4096)
                        controllerconn.close()
                        print("Response from worker ------ ", controllerdata.decode())

                    self.maintenance_mode_value = MODE_maintenance
                    # inspect robot state in every 1 sec
                    curr_time = time.time()
                    if curr_time - prev_time > 1.0:
                        inspection = True
                        prev_time = curr_time

                    # update battery level
                    self.battery_num = int(100 - (curr_time - start_time)/18.)

                    cv2.waitKey(1)
                    frame = self.streamer.grab_frame()
                    self.image = frame
                    # displayOnPygame(frame)

                    if record:
                        out.write(frame)

                    if not MODE_maintenance and not flag_waiting:
                        # while robot is not operating(wait for order)
                        if not flag_server and not flag_worker:
                            # flag_start is True when delivery decision complete and transferred path info.
                            flag_start, delivery_path, delivery_boxes_by_addr, delivery_info_by_addr = self.routeDecision.execute(
                                print_route=False, mode="prior") # FIFO, prior

                            if flag_start:
                                print("Delivery list ------ ", delivery_path)
                                flag_worker = True
                                global_start = True

                        # when starting delivery/arrived destination, execute once to load/unload the package
                        elif not flag_server and flag_worker:
                            flag_server = True
                            if flag_start:
                                msg = dict(type="Load", orders=delivery_boxes_by_addr)
                                self.next_delivery_address_num = delivery_path[0][1]
                                self.next_red_num = delivery_boxes_by_addr[0][1]
                                self.next_blue_num = delivery_boxes_by_addr[0][2]
                                self.next_green_num = delivery_boxes_by_addr[0][3]

                            else:
                                # sum_of_pkg = np.sum(remain_pkg[0])
                                # print("sumof pkg : ", sum_of_pkg)
                                # if not sum_of_pkg:
                                #     flag_non_pkg = True
                                #     continue

                                msg = dict(type="Unload", orders=remain_pkg[0])
                                self.next_delivery_address_num = remain_destination[1][1]
                                if len(remain_pkg) > 1:
                                    self.next_red_num = remain_pkg[1][1]
                                    self.next_blue_num = remain_pkg[1][2]
                                    self.next_green_num = remain_pkg[1][3]
                                else:
                                    self.next_red_num = 0
                                    self.next_blue_num = 0
                                    self.next_green_num = 0

                            msg = json.dumps(msg)
                            print("Sending to worker ------ ", msg)

                            try:
                                controllerconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                                controllerconn.connect((self.ConnectTo_ctrl, self.ctrl_port_2))
                                controllerconn.send(msg.encode('ascii'))
                                controllerdata = controllerconn.recv(4096)
                                controllerconn.close()
                            except:
                                print("ss")

                            print("Response from worker ------ ", controllerdata.decode())

                            if controllerdata.decode() is "":
                                print("Worker didn't get the data, try again")
                                time.sleep(0.5)
                                flag_server = False

                            elif flag_start:
                                flag_start = False


                        # while loading/unloading, wait for 'done' message from worker
                        elif flag_server and flag_worker:
                            print("... waiting for worker report ...")
                            flag_waiting = True

                        # while robot is operating
                        elif flag_server and not flag_worker:
                            #print("operating")
                            Stop_queue = False
                            obstacle_queue = False

                            out_img = detection_class.find_object(frame, curr_orientation)  # In_operation
                            out_img = detection_class.detect_flag(out_img)    # , green_stop_frame = 55(default)
                            cv2.imshow('detect result', out_img)
                            #print("after process : ", detection_class.status)
                            self.current_state = detection_class.status

                            destination_status = None
                            if global_start:
                                signage_list = ["stop", "101", "102", "103", "203", "202", "201"]
                                destination_status = signage_list.index(remain_destination[0][1])

                                # print("curr status / desired status / detect flag : ", detection_class.status, destination_status, detection_class.status_detect)
                                # print("ready flag : ", detection_class.ready_flag)

                            if detection_class.status_detect:
                                detection_class.status_detect = False
                                #print("server state : ",str(destination_status))
                                #print("class state : ", str(detection_class.status))
                                if str(destination_status) == str(detection_class.status):
                                    Stop_queue = True

                            if Stop_queue:
                                detection_class.flag_stop = True
                                # if pkg is remained, it means that robot is arrived at addresses
                                if not len(remain_pkg) == 0:
                                    print("Robot arrived at ------ ", remain_destination[0][1])
                                    flag_server = False
                                    flag_worker = True

                                    order_to_robot = True
                                    action = '1'

                                # if pkg is empty, it means delivery complete and robot returned to the STOP
                                else:
                                    print("Robot arrived at Loading zone. Prepare for next deliver!")
                                    flag_server = False
                                    flag_worker = False
                                    global_start = False

                                    order_to_robot = True
                                    action = '1'

                            if obstacle_queue:
                                MODE_maintenance = True

                                order_to_robot = True
                                action = '1'

                    elif MODE_maintenance and not flag_waiting:
                        print("... maintenance mode ...")
                        flag_waiting = True

                    elif flag_waiting:
                        cv2.waitKey(1)

                    ################## Client - Robot communication ##################
                    # client --->>> robot
                    if order_to_robot:
                        order_to_robot = False

                        #if detection_class.status == 0 and action == '3':
                            # if curr_orientation == 'c':
                            #     detection_class.status -= 1
                            # elif curr_orientation == 'cc':
                            #     detection_class.status += 1

                        # '1' : stop, '2' : go, '3' : u-turn & go
                        print("Sending to robot: ", action)
                        clientconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        clientconn.connect((self.ConnectTo, self.pi_port))
                        clientconn.send(action.encode('ascii'))
                        # data = clientconn.recv(4096)
                        # print("Response from Robot::", data.decode())
                        clientconn.close()

                        if action == '1':
                            robot_mode = "Stop"
                            flag_measure_dist = False
                        else:
                            robot_mode = "Go"
                            flag_measure_dist = True

                        if not MODE_maintenance:
                            last_order = action

                    elif inspection:
                        inspection = False

                        # print("... Inspecting robot state ...")
                        msg = "i"
                        clientconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        clientconn.connect((self.ConnectTo, self.pi_port))
                        clientconn.send(msg.encode('ascii'))

                        data = clientconn.recv(4096)
                        info = data.decode()
                        # print("Response state from Robot ------ ", info)  # info can be "Stop", "Go", "U-turn"
                        clientconn.close()

                        if str(info) == "U-turn":
                            info = "Go"
                        if str(info) == "Stop" and robot_mode == "Go":
                            flag_measure_dist = False

                            print("Robot state changed. Activate maintenance mode")
                            MODE_maintenance = True
                            maintenance_activation_count += 1
                            robot_mode = "Stop"

                            msg = dict(type="Mode", state=True)
                            msg = json.dumps(msg)
                            controllerconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            controllerconn.connect((self.ConnectTo_ctrl, self.ctrl_port_2))
                            controllerconn.send(msg.encode('ascii'))
                            controllerdata = controllerconn.recv(4096)
                            controllerconn.close()
                            print("Response from worker ------ ", controllerdata.decode())

                        if str(info) == "Go" and robot_mode == "Stop":
                            print("------------------------------------really?")
                            cv2.waitKey(0)

                    if flag_measure_dist:
                        self.distance_num += 1

                    ################## Client - Worker communication ##################
                    ## client <<<--- worker
                    try:
                        # report = "Load_done"

                        msg = "Received msg : "
                        mwconn, addr = self.ctrconn.accept()
                        mwdata = mwconn.recv(4096)
                        report = mwdata.decode()
                        msg += report
                        mwconn.send(msg.encode('ascii'))
                        mwconn.close()

                        print("Report from worker ------- ", report)
                        flag_waiting = False

                        if report == "Load_done":
                            if robot_mode == "Go":
                                continue
                            print("Load is done, move robot")
                            flag_worker = False

                            # update inventory of robot
                            remain_destination = delivery_path
                            remain_pkg = delivery_boxes_by_addr

                            order_to_robot = True
                            # '1' : stop, '2' : go, '3' : u-turn & go, '4' : delayed go, '5' : delayed u-turn & go
                            if curr_orientation == remain_destination[0][0]:
                                action = '2'

                            else:
                                action = '3'
                                curr_orientation = remain_destination[0][0]

                        elif report == "Unload_done":# or flag_non_pkg:
                            flag_non_pkg = False
                            if robot_mode == "Go":
                                continue
                            print("Delivery done to address ", remain_destination[0][1])
                            print("Delivered pkg : ", remain_pkg[0])
                            remain_destination.pop(0)
                            remain_pkg.pop(0)
                            self.routeDecision.checkOrderFullfilled(delivery_info_by_addr.pop(0))

                            print("Unload is done, move robot")
                            flag_worker = False

                            order_to_robot = True
                            # '1' : stop, '2' : go, '3' : u-turn and go
                            if curr_orientation == remain_destination[0][0]:
                                action = '2'
                            else:
                                action = '3'
                                curr_orientation = remain_destination[0][0]

                        elif report == "Pass":
                            print("Wrong delivery!")
                            remain_destination.pop(0)
                            remain_pkg.pop(0)

                            print("Skip the order, move robot")
                            flag_worker = False

                            order_to_robot = True
                            # '1' : stop, '2' : go, '3' : u-turn and go
                            if curr_orientation == remain_destination[0][0]:
                                action = '2'
                            else:
                                action = '3'
                                curr_orientation = remain_destination[0][0]

                        elif report == "done":
                            print("required job done")

                        elif report == "Activate":
                            print("Activating maintenance mode ...")
                            MODE_maintenance = True
                            maintenance_activation_count += 1

                            order_to_robot = True
                            action = '1'

                        elif report == "Deactivate":
                            print("Deactivating maintenance mode ...")
                            MODE_maintenance = False

                            if flag_battery:
                                flag_battery = False
                                self.battery_num = 100

                            order_to_robot = True
                            action = last_order

                    except socket.error:
                        '''no data yet..'''

                    ############## temporal initiation ################
                    if keyboard.is_pressed('a'):  # press when start
                        order_to_robot = True
                        action = '2'
                    if keyboard.is_pressed('s'):  # press when stop
                        order_to_robot = True
                        action = '1'
                    # For quit
                    if keyboard.is_pressed('f'):
                        clientconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        clientconn.connect((self.ConnectTo, self.pi_port))
                        action = '1'
                        # '1' : stop, '2' : go, '3' : u-turn and go
                        clientconn.send(action.encode('ascii'))

                        # data = clientconn.recv(4096)
                        clientconn.close()
                        sys.exit()


        except:
            print("exception occur")

        finally:
            self.ctrconn.close()
            # save log as csv format
            print("start saving log data")
            with open('output.csv', 'w', newline='') as myfile:
                wr = csv.writer(myfile, quoting=csv.QUOTE_ALL)
                wr.writerow(self.y1)
                wr.writerow(self.y2)
                wr.writerow(self.y3)

            save_pickle = [self.y1, self.y2, self.y3, self.battery_num, self.routeDecision]
            with open('_data_log.pickle', 'wb') as handle:
                pickle.dump(save_pickle, handle, protocol=pickle.HIGHEST_PROTOCOL)

            print("logging done")
            if record:
                out.release()

        return "Main program done."

    def _main_program(self):
        # Pass the function to execute
        worker = Worker(self.execute_this_fn)  # Any other args, kwargs are passed to the run function
        worker.signals.finished.connect(self.thread_complete)

        # Execute
        self.threadpool.start(worker)


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    app.exec_()
