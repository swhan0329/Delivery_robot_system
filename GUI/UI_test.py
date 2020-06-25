import sys

import pyqtgraph as pg

from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSlot, pyqtSignal, QObject, Qt, QThread, QTimer
from PyQt5.QtMultimediaWidgets import QVideoWidget
import time, random


class ExMain(QWidget):
    def __init__(self):
        super().__init__()
        self.setupUI()

    def setupUI(self):
        hbox = QHBoxLayout()

        self.pw2 = pg.PlotWidget(title="a graph")
        self.pw3 = pg.PlotWidget(title="b graph")
        self.pw4 = pg.PlotWidget(title="c graph")
        self.pw5 = pg.PlotWidget(title="d graph")
        self.pw6 = pg.PlotWidget(title="e graph")
        hbox.addWidget(self.pw2)
        hbox.addWidget(self.pw3)
        hbox.addWidget(self.pw4)
        hbox.addWidget(self.pw5)
        hbox.addWidget(self.pw6)

        self.setLayout(hbox)

        # self.setGeometry(300, 100, 800, 500)  # x, y, width, height
        self.setWindowTitle("pyqtgraph 예제 - realtime")

        self.x = [1, 2, 3]
        self.y = [4, 5, 6]

        self.mytimer = QTimer()
        self.mytimer.start(1000)  # 1초마다 차트 갱신 위함...
        self.mytimer.timeout.connect(self.get_data)
        self.new_y =[]
        self.draw_chart()
        self.show()

    def draw_chart(self,):

        cnt = len(self.y)

        for i in range(cnt):
            temp = random.random()*60
            self.new_y.append(temp) # 0 이상 ~ 60 미만 random 숫자 만들기

        bar_chart = pg.BarGraphItem(x=self.x, height=self.new_y, width=1, brush='y', pen='r', title="잔상남음")
        self.pw2.addItem(bar_chart)

    @pyqtSlot()
    def get_data(self):
        # print(time.localtime())
        # print(time.strftime("%H%M%S", time.localtime()))

        data: str = time.strftime("%S", time.localtime())  # 초 단위만 구함.

        last_x = self.x[-1]
        self.x.append(last_x + 1)

        self.y.append(int(data))
        self.draw_chart()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ExMain()
    sys.exit(app.exec_())
