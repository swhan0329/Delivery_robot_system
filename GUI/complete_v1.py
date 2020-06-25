import sys, random
import pyqtgraph as pg
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5 import QtGui
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import cv2

form_class = uic.loadUiType("GUI.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        #######initialize#######
        self.destination_status = 0
        self.next_delivery_address_num=0
        self.network_status = 0
        self.red_num = 26
        self.blue_num = 26
        self.green_num = 26
        self.next_red_num = 0
        self.next_blue_num = 0
        self.next_green_num = 0
        self.battery_num = 100
        self.distance_num = 0
        self.total_package_delivered__num = 0
        self.image = cv2.imread("green.png")

        #####graph initialize#####
        hbox1 = QHBoxLayout()
        self.pw1 = pg.PlotWidget(title="a graph")
        self.pw1.showGrid(x=True, y=True) #show the grid
        hbox1.addWidget(self.pw1)
        self.graph1.setLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.pw2 = pg.PlotWidget(title="a graph")
        self.pw2.showGrid(x=True, y=True)  # show the grid
        hbox2.addWidget(self.pw2)
        self.graph2.setLayout(hbox2)

        hbox3 = QHBoxLayout()
        self.pw3 = pg.PlotWidget(title="a graph")
        self.pw3.showGrid(x=True, y=True)  # show the grid
        hbox3.addWidget(self.pw3)
        self.graph3.setLayout(hbox3)

        self.x1 = [0]
        self.y1 = [0]
        self.x2 = [0]
        self.y2 = [0]
        self.x3 = [0]
        self.y3 = [0]
        ###############################
        self.run()

    def run(self):
        self.update_robot_address()
        self.update_next_delivery_address()
        self.update_next_delivery_list()
        self.update_remain_battery()
        self.update_distance_traveled()
        self.update_network_change_status()
        self.update_inventory_status()
        self.update_total_package_delivered()
        self.update_image()
        self.draw_graph()

    def update_network_change_status(self):
        if self.network_status:
            self.network_status_value.setText("Connect")
            self.network_status_value.setFont(QtGui.QFont("Gulim", 20, QtGui.QFont.Bold))
            self.network_status_value.setStyleSheet('color: blue')
        else:
            self.network_status_value.setText("Disconnect")
            self.network_status_value.setFont(QtGui.QFont("Gulim", 20, QtGui.QFont.Bold))
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
        if self.next_delivery_address_num == 0:
            self.next_delivery_address_value.display(0)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: red; }""")
        elif self.next_delivery_address_num == 1:
            self.next_delivery_address_value.display(101)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")

        elif self.next_delivery_address_num == 2:
            self.next_delivery_address_value.display(102)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == 3:
            self.next_delivery_address_value.display(103)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == 4:
            self.next_delivery_address_value.display(203)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == 5:
            self.next_delivery_address_value.display(202)
            self.next_delivery_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.next_delivery_address_num == 6:
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
        self.total_package_delivered_value.display(self.total_package_delivered__num)

    def update_remain_battery(self):
        self.remain_battery_value.display(self.battery_num)

    def update_distance_traveled(self):
        self.distance_traveled_value.display(self.distance_num)

    def update_robot_address(self):
        if self.destination_status == 0:
            self.current_robot_address_value.display(0)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: red; }""")
        elif self.destination_status == 1:
            self.current_robot_address_value.display(101)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.destination_status == 2:
            self.current_robot_address_value.display(102)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.destination_status == 3:
            self.current_robot_address_value.display(103)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.destination_status == 4:
            self.current_robot_address_value.display(203)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.destination_status == 5:
            self.current_robot_address_value.display(202)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")
        elif self.destination_status == 6:
            self.current_robot_address_value.display(201)
            self.current_robot_address_value.setStyleSheet("""QLCDNumber {color: black; }""")

    def update_image(self):
        self.image = QtGui.QImage(self.image.data, self.image.shape[1], self.image.shape[0], QtGui.QImage.Format_RGB888).rgbSwapped()
        self.robot_view.setPixmap(QtGui.QPixmap.fromImage(self.image))
        self.robot_view.setPixmap(QPixmap(self.image).scaled(self.robot_view.width(), self.robot_view.height(), Qt.KeepAspectRatio))

    def draw_graph(self):
        line_chart = self.pw1.plot(x=self.x1, y=self.y1, symbolPen='g', symbolBrush=0.2, name='green')
        bar_chart = pg.BarGraphItem(x=self.x2, height=self.y2, width=1, brush='y', pen='r')
        self.pw2.addItem(bar_chart)
        line_chart = self.pw3.plot(x=self.x3, y=self.y3, symbolPen='g', symbolBrush=0.2, name='green')


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()



    mytimer = QTimer()
    mytimer.start(1000)  # 1초마다 갱신 위함...
    mytimer.timeout.connect(get_data)

    myWindow.show()
    app.exec_()
