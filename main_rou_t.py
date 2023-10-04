# -*- coding: utf-8 -*-
"""bug说明：周期表重复制作时不能更新视窗显示，但是存图可以更新，周期表可以更新"""
# import os.path
import sys

from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTableWidgetItem
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
from qt_material import apply_stylesheet

from ui_rou_t import Ui_MainWindow

plt.rc("font", family='MicroSoft YaHei', weight="bold")  # 解决不能显示中文

# BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))


class RoutWindow(QMainWindow, Ui_MainWindow):  # 这里的第一个继承需要与ui的窗体继承类一致
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # ui的py文件里的函数，需要调用才可以，而且要有self，该显示窗口的父类

        self.init_signal_slot()  # 初始化信号与槽的连接
        self.period = None
        self.rou = None
        self.betalife = self.readparameter()  # 读取动力学参数
        self.beta = self.betalife[:6]
        self.betasum = sum(self.beta)
        self.life = self.betalife[6]
        self.gama = self.betalife[7]
        self.namenda = self.betalife[8:]

    # 绑定反应性计算按钮点击事件
    def init_signal_slot(self):
        self.pushButton_calculate_rou.clicked.connect(self.get_rou)
        self.pushButton_rou_table.clicked.connect(self.rou_table)

    # 读取动力学参数
    # def readparameter(self, openfile=os.path.join(BASE_DIR, "data", "betalife.txt")):
    def readparameter(self, openfile="betalife.txt"):
        filehandler1 = open(openfile, "r", encoding='gbk', errors='ignore')
        betalife0 = filehandler1.readlines()
        filehandler1.close()
        betalife = []
        for i in range(len(betalife0) - 1):
            betalife.append(float(betalife0[i].strip()))
        return betalife

    def get_rou(self):
        rou = self.calculate_rou(float(self.lineEdit_t.text()))
        self.lineEdit_rou.setText(str(round(rou, 3)))

    def calculate_rou(self, period):
        beta = self.beta
        namenda = self.namenda
        life = self.life
        qiuhe = 0
        k_fenzi = 1 + life / period
        for i in range(6):
            qiuhe += beta[i] / (1 + namenda[i] * period)
        k_fenmu = 1 - qiuhe
        keff = k_fenzi / k_fenmu
        rou = (1 - 1 / keff) * 100000
        return rou

    def rou_table(self):
        self.period = []
        self.rou = []
        deltat = float(self.lineEdit_t_delta.text())
        period = float(self.lineEdit_t_begin.text())
        while period < float(self.lineEdit_t_end.text()):
            rou = self.calculate_rou(period)
            self.rou.append(round(rou, 3))
            self.period.append(round(period, 3))
            period = period + deltat
        print(self.period, self.rou)
        self.draw_rou_table()  # 制作周期表
        self.draw_rou_line()  # 绘制周期曲线

    # 制作周期表
    def draw_rou_table(self):
        self.tableWidget_rou_table.setRowCount(0)
        self.tableWidget_rou_table.setColumnCount(2)
        self.tableWidget_rou_table.setHorizontalHeaderLabels(['周期', '反应性'])
        for i in range(len(self.period)):
            row = self.tableWidget_rou_table.rowCount()
            self.tableWidget_rou_table.insertRow(row)
            item_period = QTableWidgetItem(str(self.period[i]))
            # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignVCenter)
            self.tableWidget_rou_table.setItem(i, 0, item_period)
            item_rou = QTableWidgetItem(str(self.rou[i]))
            # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignVCenter)
            self.tableWidget_rou_table.setItem(i, 1, item_rou)

    # 绘制周期曲线
    def draw_rou_line(self):
        x = self.period
        y1 = self.rou
        view = FigureCanvasQTAgg(Figure(figsize=(5, 3)))
        axes = view.figure.subplots()
        toolbar = NavigationToolbar2QT(view)
        axes.plot(x, y1)
        axes.legend(['周期反应性'], loc='upper right')
        axes.set_xlabel("周期/s", c='b')
        axes.set_ylabel("反应性/pcm", c='b')
        axes.set_title("周期-反应性曲线", c='b')
        axes.grid(ls='--', lw=0.5)
        view.draw()
        view.figure.savefig(fname='周期-反应性曲线.png',
                            dpi=300,
                            # facecolor='lightblue'
                            )
        vlayout = QVBoxLayout()
        vlayout.addWidget(toolbar)  # ！这行一定要有，不然没有辅助工具
        vlayout.addWidget(view)
        self.graphicsView_rou_table.setLayout(vlayout)


if __name__ == '__main__':
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
        # 在app实例化之后，应用样式
    apply_stylesheet(app, theme='light_blue.xml')  # dark_blue.xml
    window = RoutWindow()
    window.show()
    app.exec()
