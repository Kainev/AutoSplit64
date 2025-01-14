from PyQt6 import QtCore, QtGui, QtWidgets

from ..constants import (
    VERSION,
    AUTHOR,
    ABOUT_PATH
)
from as64core import resource_utils


class AboutDialog(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self.width = 420
        self.height = 280
        self.title = "About AutoSplit64"

        self.background = QtWidgets.QLabel(parent=self)

        self.ver_title_lb = QtWidgets.QLabel("Version:", parent=self)
        self.ver_lb = QtWidgets.QLabel(VERSION, parent=self)
        self.author_title_lb = QtWidgets.QLabel("Author:", parent=self)
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

        self.background.move(0, 0)
        self.ver_title_lb.move(260, 201)
        self.ver_lb.move(302, 201)
        self.author_title_lb.move(262, 221)
        self.author_lb.move(302, 221)

    def mousePressEvent(self, e):
        self.close()
