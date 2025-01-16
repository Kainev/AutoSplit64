from PyQt6 import QtCore, QtGui, QtWidgets
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
        super().__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.window_title = "Output"
        self.setWindowIcon(QtGui.QIcon(resource_utils.base_path(ICON_PATH)))

        # Output Reader
        self.output_reader = None

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
        self.setFixedSize(250, 375)

        # Create Layout
        self.setLayout(self.primary_layout)

        # Configure Widgets
        self.fade_status_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.fade_out_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.fade_in_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.xcam_percent_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.xcam_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.xcam_status_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.prediction_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.probability_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.execution_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.update_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

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
            QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum), 4, 0)
        self.primary_layout.addWidget(HLine(), 5, 0, 1, 4)
        self.primary_layout.addItem(
            QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum), 6, 0)

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

        self.primary_layout.addItem(QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum), 20, 0)
        self.primary_layout.addWidget(HLine(), 21, 0, 1, 4)
        self.primary_layout.addItem(QtWidgets.QSpacerItem(10, 5, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum), 22, 0)

        self.primary_layout.addLayout(update_rate_layout, 23, 1)

        self.primary_layout.addItem(QtWidgets.QSpacerItem(20, 20, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding), 40, 0)

        # Connections
        self.update_le.editingFinished.connect(self._update_rate_changed)

        self.update_le.setValidator(self._int_validator)

    def show(self):
        self.output_reader = OutputReader(parent=self)

        try:
            self.update_le.setText(str(self._update_rate))
        except ValueError:
            pass

        self.output_reader.start()
        self.output_reader.output.connect(self.display_output)

        super().show()

    def display_output(self, output):
        self.fade_status_le.setText(output["fade_status"])
        self.fade_out_le.setText(str(output["fadeout_count"]))
        self.fade_in_le.setText(str(output["fadein_count"]))
        self.xcam_percent_le.setText(str(output["xcam_percent"])[:6])
        self.xcam_le.setText(str(output["xcam_count"]))
        self.xcam_status_le.setText(str(output["xcam_status"]))

        self.prediction_le.setText(str(output["prediction"]))
        self.probability_le.setText(str(output["probability"])[:6])

        self.execution_le.setText(str(output["execution"])[:6])

    def hide(self):
        self.output_reader.running = False
        self.output_reader.exit()
        super().hide()

    def close(self):
        self.output_reader.running = False
        self.output_reader.exit()
        super().close()

    def closeEvent(self, e):
        self.output_reader.running = False
        self.output_reader.exit()
        super().closeEvent(e)

    def _update_rate_changed(self):
        try:
            self.output_reader.update_rate = int(self.update_le.text())
            config.set_key("general", "output_update_rate", self.output_reader.update_rate)
            config.save_config()
        except ValueError:
            pass


class OutputReader(QtCore.QThread):
    output = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent)

        self.running = True
        self.update_rate = config.get("general", "output_update_rate")

    def run(self):
        while self.running:
            try:
                prediction = as64.prediction_info.prediction
                probability = as64.prediction_info.probability
            except AttributeError:
                prediction = None
                probability = None

            output_data = {
                "fade_status": as64.fade_status,
                "fadeout_count": as64.fadeout_count,
                "fadein_count": as64.fadein_count,
                "xcam_percent": as64.xcam_percent,
                "xcam_count": as64.xcam_count,
                "xcam_status": as64.in_xcam,
                "prediction": prediction,
                "probability": probability,
                "execution": as64.execution_time
            }

            self.output.emit(output_data)

            try:
                time.sleep(1 / self.update_rate)
            except ValueError:
                pass
