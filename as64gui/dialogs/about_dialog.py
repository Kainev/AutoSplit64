from PyQt6 import QtCore, QtGui, QtWidgets

from ..constants import (
    VERSION,
    AUTHOR,
    ABOUT_PATH,
    TITLE
)
from as64core import resource_utils


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.width = 420
        self.height = 280
        self.title = "About AutoSplit64+"

        self.background = QtWidgets.QLabel(parent=self)
        
        self.title_lb = QtWidgets.QLabel(TITLE, parent=self)
        self.ver_title_lb = QtWidgets.QLabel("Version:", parent=self)
        self.ver_lb = QtWidgets.QLabel(VERSION, parent=self)
        self.author_title_lb = QtWidgets.QLabel("Authors:", parent=self)
        self.author_lb = QtWidgets.QLabel(AUTHOR, parent=self)

        self.initialize_window()

    def initialize_window(self):
        self.setFixedSize(self.width, self.height)
        self.setWindowFlags(
            QtCore.Qt.WindowType.FramelessWindowHint | 
            QtCore.Qt.WindowType.WindowStaysOnTopHint | 
            QtCore.Qt.WindowType.Dialog
        )
        self.setAttribute(QtCore.Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowTitle(self.title)

        # Configure Widgets
        self.background.setPixmap(QtGui.QPixmap(resource_utils.resource_path(ABOUT_PATH)))
        
        title_font = QtGui.QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        
        label_font = QtGui.QFont()
        label_font.setPointSize(10)
        
        self.title_lb.setFont(title_font)
        self.ver_title_lb.setFont(label_font)
        self.ver_lb.setFont(label_font)
        self.author_title_lb.setFont(label_font)
        self.author_lb.setFont(label_font)

        self.background.move(0, 0)
        self.title_lb.move(275, 86)
        self.ver_title_lb.move(275, 120)
        self.ver_lb.move(275, 140)
        self.author_title_lb.move(275, 170)
        self.author_lb.move(275, 190)

    def mousePressEvent(self, e):
        self.close()
