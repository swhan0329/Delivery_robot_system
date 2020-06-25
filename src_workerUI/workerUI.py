import tkinter as tk
import socket
from sys import *
import json
import keyboard
import Inventory
import cv2
from PIL import Image, ImageTk

def init_socket(port):
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(socket.gethostname())

    print("client Hostname :  ", host_name)
    print("client IP: ", host_ip, " on port ", port)

    mwconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mwconn.bind((host_ip, port))
    mwconn.listen(5)

    return mwconn

def controllerConnect(ConnectTo, port, msg):
    controllerconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("here")
    controllerconn.connect((ConnectTo, port))
    print("here")
    controllerconn.send(msg.encode('ascii'))
    print("here")
    controllerdata = controllerconn.recv(4096)
    print("here")
    controllerconn.close()
    return controllerdata

class UIFrame(tk.Frame):
    def __init__(self, master):
        # self.pack()

        self.port_1 = 8091
        self.ctrconn = init_socket(self.port_1)
        self.ctrconn.setblocking(0)

        self.port_2 = 8090
        self.ConnectTo = socket.gethostname() #'172.26.216.93'  # '169.254.61.141' # '172.26.216.93' # wj_ip # socket.gethostname()


        self.F = tk.Frame(master)
        self.F.pack()

        # For client -> controller connection
        self.update_recv()

        loaddeact_img = Inventory.loadDeactivateGraphic()
        self.loaddeact_img = self.imgToImgtk(loaddeact_img)
        unloaddeact_img = Inventory.unloadDeactivateGraphic()
        self.unloaddeact_img = self.imgToImgtk(unloaddeact_img)
        unloadpass_img = Inventory.unloadPassGraphic()
        self.unloadpass_img = self.imgToImgtk(unloadpass_img)

        maintenanceOn_img = Inventory.MaintenanceOn()
        self.maintenaceOn_img = self.imgToImgtk(maintenanceOn_img)
        maintenanceOff_img = Inventory.MaintenanceOff()
        self.maintenaceOff_img = self.imgToImgtk(maintenanceOff_img)
        invenbatterydeact_img = Inventory.InventoryBatteryDeactivateGraphic()
        self.invenbatterydeact_img = self.imgToImgtk(invenbatterydeact_img)
        invenact_img = Inventory.InventoryActivateGraphic()
        self.invenact_img = self.imgToImgtk(invenact_img)
        batteryact_img = Inventory.InventoryActivateGraphic()
        self.batteryact_img = self.imgToImgtk(batteryact_img)

        self.Loadbutton = tk.Button(self.F, image=self.loaddeact_img, background="white")
        self.Loadbutton.grid(row=0, column=0)
        self.Loadbutton.bind("<Button-1>", self.LoadDoneClick)
        self.loadkey = False

        self.Unloadbutton = tk.Button(self.F, image=self.unloaddeact_img, background="white")
        self.Unloadbutton.grid(row=1, column=0)
        self.Unloadbutton.bind("<Button-1>", self.UnloadDoneClick)
        self.unloadkey = False

        self.UnloadPassbutton = tk.Button(self.F, image=self.unloadpass_img, background="white")
        self.UnloadPassbutton.grid(row=1, column=1)
        self.UnloadPassbutton.bind("<Button-1>", self.UnloadPassClick)
        self.unloadpasskey = False

        self.Maintenancebutton = tk.Button(self.F, image=self.maintenaceOff_img, background="white")
        self.Maintenancebutton.grid(row=2, column=1)
        self.Maintenancebutton.bind("<Button-1>", self.MaintenanceButtonClick)
        self.maintenancekey = False

        self.InvenBatterybutton = tk.Button(self.F, image=self.invenbatterydeact_img)
        self.InvenBatterybutton.grid(row=2, column=0)
        self.InvenBatterybutton.bind("<Button-1>", self.InventoryBatteryButtonClick)
        self.invenbatterykey = False

        self.Resetbutton = tk.Button(self.F, text="reset", background="white")
        self.Resetbutton.grid(row=3, column=0)
        self.Resetbutton.bind("<Button-1>", self.ResetButtonClick)

        self.label = tk.Label(text="")
        self.label.pack()

        # 배터리 교체신호
        # 인벤토리 리필신호

    def ResetButtonClick(self, event):
        print("Reset")
        self.Loadbutton["image"] = self.loaddeact_img
        self.loadkey = False
        self.Unloadbutton["image"] = self.unloaddeact_img
        self.unloadkey = False
        self.Maintenancebutton["image"] = self.maintenaceOff_img
        self.maintenancekey = False

    def update_recv(self):
        # For client -> controller connection
        try:
            # msg = "client wanted connection and success"
            # print("Waiting")
            mwconn, addr = self.ctrconn.accept()
            mwdata = mwconn.recv(4096)
            print("From client::", mwdata)
            mwconn.send(mwdata)
            mwdata = mwdata.decode()
            self.mwdata = json.loads(mwdata)
            mwconn.close()
        except socket.error:
            '''no data yet..'''
        try:
            if self.mwdata["type"] == "Load":
                self.mwdata["type"] = "Done"
                self.stateLoad()
            elif self.mwdata["type"] == "Unload":
                self.mwdata["type"] = "Done"
                self.stateUnload()
            elif self.mwdata["type"] == "Mode":
                if self.mwdata["state"] == True:
                    self.Maintenancebutton["image"]=self.maintenaceOn_img
                    self.mwdata["type"] = "Done"
                    self.maintenancekey = True
                else:
                    self.Maintenancebutton["image"]=self.maintenaceOff_img
                    self.mwdata["type"] = "Done"
                    self.maintenancekey = False
            elif self.mwdata["type"] == "Battery":
                if self.mwdata["state"] == True:
                    self.InvenBatterybutton["image"]=self.batteryact_img
                    self.mwdata["type"] = "Done"
                    self.invenbatterykey = True
            elif self.mwdata["type"] == "Refill":
                if self.mwdata["state"] == True:
                    self.InvenBatterybutton["image"]=self.invenact_img
                    self.mwdata["type"] = "Done"
                    self.invenbatterykey = True

        except:
            pass

        self.F.after(1, self.update_recv)

    def imgToImgtk(self, img):
        b, g, r = cv2.split(img)
        img1 = cv2.merge((r,g,b))
        im = Image.fromarray(img1)
        imgtk = ImageTk.PhotoImage(image=im)
        return imgtk

    def stateLoad(self):
        print(self.mwdata)
        orderList = self.mwdata["orders"]
        Load_red = 0
        Load_blue = 0
        Load_green = 0
        for order in orderList:
            Load_red += order[1]
            Load_blue += order[2]
            Load_green += order[3]

        print("============Load list============")
        print("Red: ", Load_red, "Blue: ", Load_blue, "Green: ", Load_green)
        print("=================================")

        self.load_img = Inventory.loadGraphic(Load_red, Load_blue, Load_green)
        self.load_imgtk = self.imgToImgtk(self.load_img)
        self.Loadbutton["image"] = self.load_imgtk
        self.loadkey = True

    def stateUnload(self):
        print(self.mwdata)
        orderList = self.mwdata["orders"]
        address = orderList[0]
        Unload_red = orderList[1]
        Unload_blue = orderList[2]
        Unload_green = orderList[3]

        print("===========Unload list===========")
        print("address: ", address, "Red: ", Unload_red, "Blue: ", Unload_blue, "Green: ", Unload_green)
        print("=================================")
        self.unload_img = Inventory.unloadGraphic(address, Unload_red, Unload_blue, Unload_green)
        self.unload_imgtk = self.imgToImgtk(self.unload_img)
        self.Unloadbutton["image"] = self.unload_imgtk
        self.unloadkey = True


    def LoadDoneClick(self, event):
        print("Load Done click!")
        if self.loadkey == True:
            try:
                msg2 = "Load_done"
                controllerdata = controllerConnect(self.ConnectTo, self.port_2, msg2)
                print("From Server::", controllerdata.decode())
                self.Loadbutton["image"] = self.loaddeact_img
                self.loadkey = False
            except:
                pass

    def UnloadDoneClick(self, event):
        print("Unload Done click!")
        if self.unloadkey == True:
            try:
                msg2 = "Unload_done"
                controllerdata = controllerConnect(self.ConnectTo, self.port_2, msg2)
                print("From Server::", controllerdata.decode())
                self.Unloadbutton["image"] = self.unloaddeact_img
                self.unloadkey = False
            except:
                pass

    def UnloadPassClick(self, event):
        print("Unload Pass click!")
        if self.unloadkey == True:
            try:
                msg2 = "PASS"
                controllerdata = controllerConnect(self.ConnectTo, self.port_2, msg2)
                print("From Server::", controllerdata.decode())
                self.unloadkey = False
            except:
                pass

    def InventoryBatteryButtonClick(self, event):
        print("InventoryBattery click!")
        if self.invenbatterykey == True:
            try:
                msg2 = "done"
                controllerdata = controllerConnect(self.ConnectTo, self.port_2, msg2)
                print("From Server::", controllerdata.decode())
                self.invenbatterykey = False
            except:
                pass

    def MaintenanceButtonClick(self, event):
        try:
            if self.maintenancekey == True:
                state = "Deactivate"  # Maintenace mode on
                print("Maintenance mode off")
                controllerdata = controllerConnect(self.ConnectTo, self.port_2, state)
                print("From Server::", controllerdata.decode())
                self.maintenancekey = False
                self.Maintenancebutton["image"] = self.maintenaceOff_img
            else:
                state = "Activate"  # Maintenace mode on
                print("Maintenance mode on")
                controllerdata = controllerConnect(self.ConnectTo, self.port_2, state)
                print("From Server::", controllerdata.decode())
                self.maintenancekey = True
                self.Maintenancebutton["image"] = self.maintenaceOn_img
        except:
            pass


def main():
    root = tk.Tk()
    root.title('Worker System')
    root.geometry('800x1000')
    WSframe = UIFrame(root)
    root.mainloop()

if __name__ == '__main__':
    main()
