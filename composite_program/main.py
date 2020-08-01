from PyQt5.QtWidgets import *
from view import View, MainWindow
from model import Model
import sys

qt_app = QApplication(sys.argv)
model = Model()
main_window = MainWindow(model)
main_window.showNormal()
qt_app.exec_()



