# -*- coding: utf-8 -*-
"""bug说明：目前界面的参数为假的，主要还是默认读取文本文件：betalife.txt"""
# import os.path
import sys

from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QTableWidgetItem
from matplotlib import pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.backends.backend_qtagg import NavigationToolbar2QT
from matplotlib.figure import Figure
from qt_material import apply_stylesheet

from main_rou_t import RoutWindow
from subthreads.rou_ndt_thread import RouNdtThread
from ui_drpy import Ui_mainWindow

plt.rc("font", family='MicroSoft YaHei', weight="bold")  # 解决不能显示中文


# BASE_DIR = os.path.dirname(os.path.realpath(sys.argv[0]))


class MyWindow(QMainWindow, Ui_mainWindow):  # 这里的第一个继承需要与ui的窗体继承类一致
    def __init__(self):
        super().__init__()
        self.setupUi(self)  # ui的py文件里的函数，需要调用才可以，而且要有self，该显示窗口的父类MyWindow

        self.thread = None
        self.betalife = None
        self.electricity = None
        self.rou = None
        self.rou_t_window = None
        self.init_set()  # 给出初始化的设置及调用
        self.init_signal_slot()  # 初始化信号与槽的连接

    def init_set(self):
        pix = QPixmap('home.jpg')
        self.label_home.setPixmap(pix)
        self.betalife = self.readparameter()  # 读取动力学参数
        electricity1 = self.readelectricity()  # 读取原始电流
        self.electricity = electricity1[4:]

    def init_signal_slot(self):
        # 绑定反应性计算按钮点击事件
        self.pushButton_roustart.clicked.connect(self.start)
        self.pushButton_roustop.clicked.connect(self.stop)
        self.pushButton_elec.clicked.connect(self.draw_elec_line_data)
        self.pushButton_rou_t.clicked.connect(self.draw_rou_t)

    # 启动多线程执行反应性计算
    def start(self):
        print('Start clicked.')
        self.thread = RouNdtThread(self.betalife, self.electricity)  # 实例化一个线程
        # 将线程thread的信号finishSignal和UI主线程中的槽函数callback进行连接
        self.thread.finishSignal.connect(self.callback)
        # 启动线程，执行线程类中run函数
        self.thread.start()

    # 终止线程
    def stop(self):
        print('End')
        self.thread.terminate()

    def callback(self, rou):
        print('主线程：', rou)
        self.rou = rou
        self.drawline_rou()  # 利用返回的反应性数据绘制曲线
        self.draw_rou_data()

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

    # 读取原始电流
    # def readelectricity(self, openfile=os.path.join(BASE_DIR, "data", "000.txt"))
    def readelectricity(self, openfile="000.txt"):
        filehandler2 = open(openfile, "r")
        electricity0 = filehandler2.readlines()
        filehandler2.close()
        electricity1 = []
        for i in range(len(electricity0)):
            electricity1.append(float(electricity0[i].strip()))
        return electricity1

    def draw_elec_line_data(self):
        self.drawline_elec()
        self.draw_elec_data()

    def draw_elec_data(self):
        self.tableWidget_elec_rou_data.setColumnCount(2)
        self.tableWidget_elec_rou_data.setHorizontalHeaderLabels(['电流', '反应性'])
        for i in range(len(self.electricity)):
            row = self.tableWidget_elec_rou_data.rowCount()
            self.tableWidget_elec_rou_data.insertRow(row)
            item = QTableWidgetItem(str(self.electricity[i]))
            # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignVCenter)
            self.tableWidget_elec_rou_data.setItem(i, 0, item)

    def drawline_elec(self):
        xrange = []
        for i in range(len(self.electricity)):
            xrange.append(i * 0.01)

        x = xrange
        y1 = self.electricity

        view = FigureCanvasQTAgg(Figure(figsize=(5, 3)))
        axes = view.figure.subplots()
        toolbar = NavigationToolbar2QT(view)
        axes.plot(x[:-1], y1[:-1])
        axes.legend(['电流'], loc='upper right')
        axes.set_xlabel("时间/s", c='b')
        axes.set_ylabel("电流/?A", c='b')
        axes.set_title("电流变化曲线", c='b')
        axes.grid(ls='--', lw=0.5)
        view.draw()
        view.figure.savefig(fname='电流变化曲线.png',
                            dpi=300,
                            facecolor='lightblue'
                            )
        vlayout = QVBoxLayout()
        vlayout.addWidget(toolbar)  # ！这行一定要有，不然没有辅助工具
        vlayout.addWidget(view)
        self.plot_elec.setLayout(vlayout)

    def draw_rou_data(self):
        for i in range(len(self.rou)):
            item = QTableWidgetItem(str(self.rou[i]))
            # item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
            self.tableWidget_elec_rou_data.setItem(i + 1, 1, item)

    def drawline_rou(self):
        xrange = []
        for i in range(len(self.electricity)):
            xrange.append(i * 0.01)

        x = xrange
        y2 = self.rou

        view2 = FigureCanvasQTAgg(Figure(figsize=(5, 3)))
        axes2 = view2.figure.subplots()
        toolbar2 = NavigationToolbar2QT(view2)
        axes2.plot(x[:-1], y2, c='purple')
        axes2.legend(['反应性'], loc='upper right')
        axes2.set_xlabel("时间/s", c='b')
        axes2.set_ylabel("反应性/pcm", c='b')
        axes2.set_title("反应性变化曲线", c='b')
        axes2.grid(ls='--', lw=0.5)
        view2.draw()
        view2.figure.savefig(fname='反应性变化曲线.png',
                             dpi=300,
                             facecolor='lightblue'
                             )
        vlayout2 = QVBoxLayout()
        vlayout2.addWidget(toolbar2)  # ！这行一定要有，不然没有辅助工具
        vlayout2.addWidget(view2)
        self.plot_rou.setLayout(vlayout2)

    # 子界面，周期法计算反应性
    def draw_rou_t(self):
        self.rou_t_window = RoutWindow()  # 初始化子界面, 必须加self，以将进程放到主进程中,使其支持循环，否则子界面会闪退！
        self.rou_t_window.show()


class QSSLoader:
    def __init__(self):
        pass

    @staticmethod
    def read_qss_file(qss_file_name):
        with open(qss_file_name, 'r', encoding='UTF-8') as file:
            return file.read()


if __name__ == '__main__':
    if QApplication.instance() is None:
        app = QApplication(sys.argv)
    else:
        app = QApplication.instance()
        # 在app实例化之后，应用样式
    apply_stylesheet(app, theme='light_blue.xml')  # dark_blue.xml。这种app方式可以将皮肤传递到子窗口界面
    window = MyWindow()
    # style_file = os.path.join(os.getcwd(), "data", "style_blue.qss")
    # style_sheet = QSSLoader.read_qss_file(style_file)
    # window.setStyleSheet(style_sheet)
    window.show()
    app.exec()
