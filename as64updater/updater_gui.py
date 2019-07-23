from PyQt5 import QtCore, QtGui, QtWidgets

from resource_utils import base_path


class UpdaterGUI(QtWidgets.QMainWindow):

    DOWNLOADING = 0
    INSTALLING = 1

    closed = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Window Properties
        self.setAttribute(QtCore.Qt.WA_DeleteOnClose, True)
        self.width = 268
        self.height = 100
        self.setWindowIcon(QtGui.QIcon(base_path("resources/gui/icons/icon.png")))

        #
        self._version = None

        # Main Layout
        self.main_layout = QtWidgets.QVBoxLayout()

        # Content
        self.content_widget = QtWidgets.QWidget()
        self.label = QtWidgets.QLabel("")
        self.progress_bar = QtWidgets.QProgressBar()
        self.abort_button = QtWidgets.QPushButton("Abort")

        self.initialize()
        self.show()

    def initialize(self):
        # Configure Window
        self.setFixedSize(self.width, self.height)
        self.setCentralWidget(self.content_widget)

        # Configure Widgets
        self.progress_bar.setFixedSize(250, 20)
        self.abort_button.setFixedSize(100, 30)

        self.progress_bar.setMaximum(100)

        # Add abort button to container to avoid layout resize when button is hidden
        abort_button_container = QtWidgets.QWidget()
        abort_button_container.setLayout(QtWidgets.QVBoxLayout())
        abort_button_container.layout().setContentsMargins(0, 0, 0, 0)
        abort_button_container.layout().addStretch(0)
        abort_button_container.layout().setSpacing(0)
        abort_button_container.layout().addWidget(self.abort_button)

        # Configure Download Widget
        self.content_widget.setLayout(QtWidgets.QVBoxLayout())
        self.content_widget.layout().addWidget(self.label)
        self.content_widget.layout().addWidget(self.progress_bar)
        self.content_widget.layout().addWidget(abort_button_container, alignment=QtCore.Qt.AlignRight)

    def set_download_version(self, version):
        self._version = version



    def set_status(self, status):
        if status == UpdaterGUI.DOWNLOADING:
            self.label.setText("Downloading Version {}".format(self._version))
        elif status == UpdaterGUI.INSTALLING:
            self.label.setText("Installing Version {}".format(self._version))
            self.abort_button.setHidden(True)

        self.progress_bar.setValue(0)

    def set_progress(self, percent):
        self.progress_bar.setValue(percent)

    def display_error_message(self, message, title="Error"):
        """
        Display a warning dialog with given title and message
        :param title: Window title
        :param message: Warning/error message
        :return:
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.show()
