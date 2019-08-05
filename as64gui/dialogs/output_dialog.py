from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Thread
import time

from ..constants import (
    ICON_PATH
)

import as64core as as64
from as64core import resource_utils, config
from as64gui.widgets import HLine


class OutputDialog(QtWidgets.QDialog):
    open_capture = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)
        self.window_title = "Output"
        self.setWindowIcon(QtGui.QIcon(resource_utils.base_path(ICON_PATH)))

        #
        self._update_rate = config.get("general", "output_update_rate")

        # Layouts
        self.primary_layout = QtWidgets.QGridLayout()

        # Widgets
        self.fade_status_lb = QtWidgets.QLabel("Fade Status:")
        self.fade_out_lb = QtWidgets.QLabel("Fade-out Count:")
        self.fade_in_lb = QtWidgets.QLabel("Fade-in Count:")
        self.xcam_percent_lb = QtWidgets.QLabel("X-Cam Percent:")
        self.xcam_lb = QtWidgets.QLabel("X-Cam Count:")
        self.xcam_status_lb = QtWidgets.QLabel("X-Cam Status:")
        self.prediction_lb = QtWidgets.QLabel("Prediction:")
        self.probability_lb = QtWidgets.QLabel("Probability:")
        self.execution_lb = QtWidgets.QLabel("Execution Time:")
        self.update_lb = QtWidgets.QLabel("Update Rate:")

        self.fade_status_le = QtWidgets.QLineEdit()
        self.fade_out_le = QtWidgets.QLineEdit()
        self.fade_in_le = QtWidgets.QLineEdit()
        self.xcam_percent_le = QtWidgets.QLineEdit()
        self.xcam_le = QtWidgets.QLineEdit()
        self.xcam_status_le = QtWidgets.QLineEdit()
        self.prediction_le = QtWidgets.QLineEdit()
        self.probability_le = QtWidgets.QLineEdit()
        self.execution_le = QtWidgets.QLineEdit()
        self.update_le = QtWidgets.QLineEdit()

        self.update_enabled = True

        # Validators
        self._int_validator = QtGui.QIntValidator(0, 30)

        self.initialize_window()

    def initialize_window(self):
        self.setWindowTitle(self.window_title)
        self.setFixedSize(240, 375)

        # Create Layout
        self.setLayout(self.primary_layout)

        # Configure Widgets
        self.fade_status_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.fade_out_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.fade_in_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.xcam_percent_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.xcam_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.xcam_status_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.prediction_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.probability_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.execution_lb.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.update_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.fade_status_le.setDisabled(True)
        self.fade_out_le.setDisabled(True)
        self.fade_in_le.setDisabled(True)
        self.xcam_percent_le.setDisabled(True)
        self.xcam_le.setDisabled(True)
        self.xcam_status_le.setDisabled(True)
        self.prediction_le.setDisabled(True)
        self.probability_le.setDisabled(True)
        self.execution_le.setDisabled(True)

        self.fade_status_lb.setFixedWidth(100)
        self.fade_out_lb.setFixedWidth(100)
        self.fade_in_lb.setFixedWidth(100)
        self.xcam_percent_lb.setFixedWidth(100)
        self.xcam_lb.setFixedWidth(100)
        self.xcam_status_lb.setFixedWidth(100)
        self.prediction_lb.setFixedWidth(100)
        self.probability_le.setFixedWidth(100)
        self.execution_lb.setFixedWidth(100)

        self.execution_le.setFixedWidth(100)
        self.fade_out_le.setFixedWidth(100)
        self.fade_in_le.setFixedWidth(100)
        self.xcam_percent_le.setFixedWidth(100)
        self.xcam_le.setFixedWidth(100)
        self.xcam_status_le.setFixedWidth(100)
        self.prediction_le.setFixedWidth(100)
        self.probability_le.setFixedWidth(100)
        self.execution_le.setFixedWidth(100)

        update_rate_layout = QtWidgets.QHBoxLayout()
        update_rate_layout.addWidget(self.update_lb)
        update_rate_layout.addWidget(self.update_le)

        # Configure Layout
        self.primary_layout.addWidget(self.fade_status_lb, 0, 0)
        self.primary_layout.addWidget(self.fade_status_le, 1, 0)

        self.primary_layout.addWidget(self.fade_out_lb, 2, 0)
        self.primary_layout.addWidget(self.fade_in_lb, 2, 1)
        self.primary_layout.addWidget(self.fade_out_le, 3, 0)
        self.primary_layout.addWidget(self.fade_in_le, 3, 1)

        self.primary_layout.addItem(
            QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 4, 0)
        self.primary_layout.addWidget(HLine(), 5, 0, 1, 4)
        self.primary_layout.addItem(
            QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 6, 0)

        self.primary_layout.addWidget(self.xcam_percent_lb, 7, 0)
        self.primary_layout.addWidget(self.xcam_percent_le, 8, 0)
        self.primary_layout.addWidget(self.xcam_lb, 9, 0)
        self.primary_layout.addWidget(self.xcam_status_lb, 9, 1)
        self.primary_layout.addWidget(self.xcam_le, 10, 0)
        self.primary_layout.addWidget(self.xcam_status_le, 10, 1)

        self.primary_layout.addWidget(HLine(), 11, 0, 1, 4)

        self.primary_layout.addWidget(self.prediction_lb, 13, 0)
        self.primary_layout.addWidget(self.probability_lb, 13, 1)
        self.primary_layout.addWidget(self.prediction_le, 14, 0)
        self.primary_layout.addWidget(self.probability_le, 14, 1)

        self.primary_layout.addWidget(HLine(), 16, 0, 1, 4)

        self.primary_layout.addWidget(self.execution_lb, 18, 0)
        self.primary_layout.addWidget(self.execution_le, 19, 0)

        self.primary_layout.addItem(QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 20, 0)
        self.primary_layout.addWidget(HLine(), 21, 0, 1, 4)
        self.primary_layout.addItem(QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Minimum), 22, 0)

        self.primary_layout.addLayout(update_rate_layout, 23, 1)

        self.primary_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), 40, 0)

        # Connections
        self.update_le.editingFinished.connect(self._update_rate_changed)

        self.update_le.setValidator(self._int_validator)

    def show(self):
        try:
            self.update_le.setText(str(self._update_rate))
        except ValueError:
            pass

        self.update_enabled = True
        Thread(target=self.update_output).start()

        super().show()

    def hide(self):
        self.update_enabled = False
        super().hide()

    def close(self):
        self.update_enabled = False
        super().close()

    def closeEvent(self, e):
        self.update_enabled = False
        super().closeEvent(e)

    def update_output(self):
        while self.update_enabled:
            try:
                self.fade_status_le.setText(as64.fade_status)
                self.fade_out_le.setText(str(as64.fadeout_count))
                self.fade_in_le.setText(str(as64.fadein_count))
                self.xcam_percent_le.setText(str(as64.xcam_percent)[:6])
                self.xcam_le.setText(str(as64.xcam_count))
                self.xcam_status_le.setText(str(as64.in_xcam))

                try:
                    self.prediction_le.setText(str(as64.prediction_info.prediction))
                    self.probability_le.setText(str(as64.prediction_info.probability)[:6])
                except AttributeError:
                    pass

                self.execution_le.setText(str(as64.execution_time)[:6])
            except RuntimeError:
                self.update_enabled = False

            try:
                time.sleep(1 / self._update_rate)
            except ValueError:
                pass

    def _update_rate_changed(self):
        try:
            self._update_rate = int(self.update_le.text())
            config.set_key("general", "output_update_rate", self._update_rate)
            config.save_config()
        except ValueError:
            pass
