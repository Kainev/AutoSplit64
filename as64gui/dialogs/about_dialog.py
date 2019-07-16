from PyQt5 import QtCore, QtGui, QtWidgets

from ..constants import (
    TITLE,
    VERSION,
    AUTHOR,
    ICON_PATH
)
from as64core import resource_utils


class AboutDialog(QtWidgets.QDialog):
    open_capture = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)
        self.window_title = "About " + TITLE
        self.setWindowIcon(QtGui.QIcon(resource_utils.base_path(ICON_PATH)))

        # Layouts
        self.menu_layout = QtWidgets.QVBoxLayout()
        self.button_layout = QtWidgets.QHBoxLayout()

        # Widgets
        self.icon_lb = QtWidgets.QLabel()
        self.title_lb = QtWidgets.QLabel(TITLE)
        self.ver_title_lb = QtWidgets.QLabel("Version:")
        self.ver_lb = QtWidgets.QLabel(VERSION)
        self.author_title_lb = QtWidgets.QLabel("Author:")
        self.author_lb = QtWidgets.QLabel(AUTHOR)
        self.about_te = QtWidgets.QTextEdit()

        self.ok_btn = QtWidgets.QPushButton("Ok")

        # Font
        self.title_font = QtGui.QFont()
        self.title_font.setPointSize(16)

        self.initialize_window()

    def initialize_window(self):
        self.setWindowTitle(self.window_title)
        self.resize(200, 50)

        # Create Layout
        self.setLayout(self.menu_layout)

        # Configure Widgets
        self.icon_lb.setPixmap(QtGui.QPixmap(resource_utils.resource_path(ICON_PATH)))
        self.title_lb.setFont(self.title_font)

        self.ver_title_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.ver_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.author_title_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.author_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)

        self.ver_title_lb.setMaximumWidth(60)
        self.author_title_lb.setMaximumWidth(60)

        self.about_te.setDisabled(True)

        # Child Layouts
        icon_title_layout = QtWidgets.QHBoxLayout()
        icon_title_layout.addWidget(self.icon_lb)
        icon_title_layout.addWidget(self.title_lb)

        version_layout = QtWidgets.QHBoxLayout()
        version_layout.addWidget(self.ver_title_lb)
        version_layout.addWidget(self.ver_lb)

        author_layout = QtWidgets.QHBoxLayout()
        author_layout.addWidget(self.author_title_lb)
        author_layout.addWidget(self.author_lb)

        # Configure Layout
        #self.menu_layout.addLayout(icon_title_layout)
        self.menu_layout.addLayout(version_layout)
        self.menu_layout.addLayout(author_layout)
