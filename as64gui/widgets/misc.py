from PyQt6 import QtCore, QtWidgets, QtGui

from as64gui.widgets import PictureButton
from as64gui import constants


class HLine(QtWidgets.QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setFrameShape(QtWidgets.QFrame.Shape.HLine)
        palette = QtGui.QPalette()
        palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(43, 45, 47))
        self.setPalette(palette)


class StarCountDisplay(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.slash_lb = QtWidgets.QLabel("/")
        self.left_lb = QtWidgets.QLabel("-")
        self.right_lb = QtWidgets.QLabel("-")

        self.initialize()

    def initialize(self):
        # Configure Layout
        layout = QtWidgets.QHBoxLayout()
        self.setLayout(layout)

        # Configure Widgets
        self.left_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.right_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)

        self.left_lb.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)
        self.slash_lb.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.right_lb.setSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum)

        layout.addWidget(self.left_lb)
        layout.addWidget(self.slash_lb)
        layout.addWidget(self.right_lb)

    def setFont(self, font):
        self.left_lb.setFont(font)
        self.slash_lb.setFont(font)
        self.right_lb.setFont(font)

    @property
    def star_count(self):
        return int(self.left_lb.text())

    @star_count.setter
    def star_count(self, count):
        self.left_lb.setText(str(count))

    @property
    def split_star(self):
        return int(self.right_lb.text())

    @split_star.setter
    def split_star(self, split):
        if split != -1:
            self.right_lb.setText(str(split))
        else:
            self.right_lb.setText("-")


