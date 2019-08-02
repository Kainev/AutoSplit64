import webbrowser

from PyQt5 import QtCore, QtGui, QtWidgets


from as64core import resource_utils
from as64gui.constants import ICON_PATH


class UpdateDialog(QtWidgets.QDialog):

    ignore = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)
        self.window_title = "Update"
        self.setWindowIcon(QtGui.QIcon(resource_utils.base_path(ICON_PATH)))

        # Layouts
        self.menu_layout = QtWidgets.QGridLayout()
        self.button_layout = QtWidgets.QHBoxLayout()

        # Widgets
        self.update_btn = QtWidgets.QPushButton("Update and Restart")
        self.info_btn = QtWidgets.QPushButton("More Info")
        self.ignore_btn = QtWidgets.QPushButton("Ignore")
        self.remind_btn = QtWidgets.QPushButton("Remind Me Later")

        self.available_lb = QtWidgets.QLabel()
        self.highlights_te = QtWidgets.QTextEdit()
        self.blog_lb = QtWidgets.QLabel()
        self.current_title_lb = QtWidgets.QLabel("Current Version: ")
        self.current_info_lb = QtWidgets.QLabel()
        self.new_title_lb = QtWidgets.QLabel("New Version: ")
        self.new_info_lb = QtWidgets.QLabel()
        self.size_title_lb = QtWidgets.QLabel("Patch Size: ")
        self.size_info_lb = QtWidgets.QLabel()

        # Fonts
        self.version_font = QtGui.QFont()
        self.version_font.setBold(True)

        #
        self._update_info = None

        self.initialize_window()

    def initialize_window(self):
        self.setWindowTitle(self.window_title)
        self.resize(680, 350)

        # Create Layout
        self.setLayout(self.menu_layout)

        # Configure Widgets

        # Version Label
        self.available_lb.setFont(self.version_font)

        # Highlights TextEdit
        self.highlights_te.setDisabled(True)
        self.highlights_te.viewport().setAutoFillBackground(False)
        self.highlights_te.setFrameStyle(QtWidgets.QFrame.NoFrame)
        self.highlights_te.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)

        # Blog Label
        self.blog_lb.setOpenExternalLinks(True)

        # Other Labels
        self.current_title_lb.setFixedWidth(80)
        self.new_title_lb.setFixedWidth(80)
        self.size_title_lb.setFixedWidth(80)

        # Buttons
        self.update_btn.setMinimumSize(120, 24)
        self.info_btn.setMinimumSize(120, 24)
        self.ignore_btn.setMinimumSize(120, 24)
        self.remind_btn.setMinimumSize(120, 24)

        self.button_layout.addItem(
            QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum))
        self.button_layout.addWidget(self.update_btn)
        self.button_layout.addWidget(self.info_btn)
        self.button_layout.addWidget(self.ignore_btn)
        self.button_layout.addWidget(self.remind_btn)

        # Configure Layout
        self.menu_layout.addItem(QtWidgets.QSpacerItem(10, 12, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 0, 0)

        self.menu_layout.addWidget(self.available_lb, 1, 0, 1, 2)

        self.menu_layout.addItem(QtWidgets.QSpacerItem(10, 12, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 2, 0)

        self.menu_layout.addWidget(self.highlights_te, 4, 0, 1, 2)
        self.menu_layout.addWidget(self.blog_lb, 6, 0, 1, 2)

        self.menu_layout.addItem(QtWidgets.QSpacerItem(10, 12, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 7, 0)

        self.menu_layout.addWidget(self.current_title_lb, 8, 0)
        self.menu_layout.addWidget(self.current_info_lb, 8, 1)

        self.menu_layout.addWidget(self.new_title_lb, 10, 0)
        self.menu_layout.addWidget(self.new_info_lb, 10, 1)

        self.menu_layout.addWidget(self.size_title_lb, 12, 0)
        self.menu_layout.addWidget(self.size_info_lb, 12, 1)

        self.menu_layout.addItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), 29, 0)

        self.menu_layout.addLayout(self.button_layout, 30, 0, 1, 2)

        # Connections
        self.remind_btn.clicked.connect(self.close)
        self.ignore_btn.clicked.connect(self.close)
        self.info_btn.clicked.connect(self._open_update_blog)

    def set_update_info(self, version_info):
        self._update_info = version_info

        # Set version
        self.available_lb.setText("AutoSplit64 Version {} is now available!".format(self._update_info["latest"]["version"]))

        # Set Highlights
        self.highlights_te.clear()
        self.highlights_te.append("Highlights:\n")
        cursor = self.highlights_te.textCursor()
        cursor.insertList(QtGui.QTextListFormat.ListDisc)

        for highlight in self._update_info["latest"]["version_features"]:
            self.highlights_te.insertPlainText(highlight)
            self.highlights_te.append("")

        cursor.deletePreviousChar()

        highlights_font = self.highlights_te.document().defaultFont()
        font_metrics = QtGui.QFontMetrics(highlights_font)
        text_size = font_metrics.size(0, self.highlights_te.toPlainText())
        text_height = text_size.height() + 20

        self.highlights_te.setFixedHeight(text_height)

        # Set Blog Label
        url_link = "<a href=\"{}\">read the blog post</a>".format(self._update_info["latest"]["version_post"])
        self.blog_lb.setText("For more details, " + url_link)

        # Set Current Version
        self.current_info_lb.setText(self._update_info["current"]["version"])

        # Set New Version
        self.new_info_lb.setText(self._update_info["latest"]["version"])

        # Set Patch Size
        self.size_info_lb.setText("{} MB".format(str(self._update_info["latest"]["patch_size"])))

    def _open_update_blog(self):
        webbrowser.open(self._update_info["latest"]["version_post"])

