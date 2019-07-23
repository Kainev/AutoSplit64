import sys

from PyQt5 import QtCore, QtWidgets, QtGui

from as64updater.updater_gui import UpdaterGUI
from as64updater.update_core import UpdaterCore


class Updater(QtCore.QObject):
    UPDATE_ERROR = QtCore.pyqtSignal(str)
    UPDATE_COMPLETE = QtCore.pyqtSignal()
    UPDATE_FOUND = QtCore.pyqtSignal(str)
    DOWNLOAD_BEGIN = QtCore.pyqtSignal()
    DOWNLOAD_COMPLETE = QtCore.pyqtSignal()
    DOWNLOAD_REPORT = QtCore.pyqtSignal(float)
    INSTALL_REPORT = QtCore.pyqtSignal(float)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Initialize GUI
        self.gui = UpdaterGUI()
        self.core = UpdaterCore(master_version_url="https://autosplit64.com/.version",
                                local_version_path=".version")

        self.core.set_listener(self)

        # Connections
        self.gui.abort_button.clicked.connect(self.core.abort_download)

        self.DOWNLOAD_REPORT.connect(self.gui.set_progress)
        self.INSTALL_REPORT.connect(self.gui.set_progress)

        self.UPDATE_FOUND.connect(self.gui.set_download_version)
        self.DOWNLOAD_BEGIN.connect(lambda: self.gui.set_status(UpdaterGUI.DOWNLOADING))
        self.DOWNLOAD_COMPLETE.connect(lambda: self.gui.set_status(UpdaterGUI.INSTALLING))
        self.UPDATE_COMPLETE.connect(self.exit)

        self.core.start()

    def update_error(self, error):
        self.UPDATE_ERROR.emit(error)

    def update_complete(self):
        self.UPDATE_COMPLETE.emit()

    def update_found(self, version):
        self.UPDATE_FOUND.emit(version)

    def download_begin(self):
        self.DOWNLOAD_BEGIN.emit()

    def download_complete(self):
        self.DOWNLOAD_COMPLETE.emit()

    def download_report(self, percentage):
        self.DOWNLOAD_REPORT.emit(percentage)

    def install_report(self, percentage):
        self.INSTALL_REPORT.emit(percentage)

    def exit(self):
        self.core.abort_download()
        self.gui.close()


if __name__ == "__main__":
    # Create QT Application
    qt_app = QtWidgets.QApplication(sys.argv)

    # Configure QT Application Style
    qt_app.setStyle('Fusion')

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(60, 63, 65))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(200, 203, 207))
    palette.setColor(QtGui.QPalette.Link, QtGui.QColor(88, 157, 246))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(23, 25, 27))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 55, 57))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtGui.QColor(200, 203, 207))
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 55, 57))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(200, 203, 207))
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(75, 110, 175))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.Light, QtGui.QColor(105, 108, 112))
    palette.setColor(QtGui.QPalette.Dark, QtGui.QColor(12, 12, 12))

    qt_app.setPalette(palette)

    # Create main application
    updater = Updater(qt_app)

    # Exit
    sys.exit(qt_app.exec_())
