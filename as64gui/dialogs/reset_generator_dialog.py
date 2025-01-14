import time
import os
import shutil

from PyQt6 import QtCore, QtGui, QtWidgets
import cv2

from ..constants import (
    ICON_PATH
)
from as64core import resource_utils

from as64core.game_capture import GameCapture
from as64core.image_utils import is_black
from as64core import (
    GAME_JP,
    RESET_REGION,
    FADEOUT_REGION,
    config
)


class ResetGeneratorHelpDialog(QtWidgets.QDialog):
    line1 = """AutoSplit64's reset feature works based on matching the second and third frame of the Super Mario 64 logo that appears when launching the game."""
    line2 = """If the colours or capture size of your particular game feed differ from the default standard it may be required to generate custom templates from your game capture."""
    line3 = """While in-game, press generate, then RESET your console. Ensure the generated images look similar to the examples. """

    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.window_title = "Reset Template Generator Help"
        self.setWindowIcon(QtGui.QIcon(resource_utils.base_path(ICON_PATH)))

        # Layouts
        self.menu_layout = QtWidgets.QVBoxLayout()
        self.button_layout = QtWidgets.QHBoxLayout()

        # Widgets
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.append(self.line1)
        self.text_edit.append("\n")
        self.text_edit.append(self.line2)
        self.text_edit.append("\n")
        self.text_edit.append(self.line3)

        self.ok_btn = QtWidgets.QPushButton("OK")

        # Font
        self.title_font = QtGui.QFont()
        self.title_font.setPointSize(16)

        self.initialize_window()

    def initialize_window(self):
        self.setWindowTitle(self.window_title)
        self.resize(400, 225)

        # Create Layout
        self.setLayout(self.menu_layout)

        # Configure Widgets
        self.text_edit.setEnabled(False)

        # Child Layouts
        self.button_layout.addItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))
        self.button_layout.addWidget(self.ok_btn)

        # Configure Layout
        self.menu_layout.addWidget(self.text_edit)
        self.menu_layout.addLayout(self.button_layout)

        self.ok_btn.clicked.connect(self.hide)


class ResetGeneratorDialog(QtWidgets.QDialog):
    TEMPLATE_DIR = "templates/"
    
    def __init__(self, parent=None):
        super().__init__(parent, QtCore.Qt.WindowType.WindowSystemMenuHint | QtCore.Qt.WindowType.WindowCloseButtonHint)
        self.window_title = "Reset Template Generator"
        self.setWindowIcon(QtGui.QIcon(resource_utils.base_path(ICON_PATH)))

        # Layouts
        self.menu_layout = QtWidgets.QGridLayout()
        self.button_layout = QtWidgets.QHBoxLayout()

        # Widgets
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.generate_btn = QtWidgets.QPushButton("Generate")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        self.help_btn = QtWidgets.QPushButton("Help")

        self.gen_1_px = QtWidgets.QLabel()
        self.gen_2_px = QtWidgets.QLabel()
        self.def_1_px = QtWidgets.QLabel()
        self.def_2_px = QtWidgets.QLabel()

        self.gen_1_sb = QtWidgets.QSpinBox()
        self.gen_2_sb = QtWidgets.QSpinBox()

        self._reset_generator = None

        self.help_dialog = ResetGeneratorHelpDialog(self)

        self.initialize_window()

    def initialize_window(self):
        self.setWindowTitle(self.window_title)
        self.resize(400, 200)

        # Create Layout
        self.setLayout(self.menu_layout)

        # Configure Widgets
        self.gen_1_px.setFixedSize(251, 137)
        self.gen_2_px.setFixedSize(251, 137)
        self.def_1_px.setFixedSize(251, 137)
        self.def_2_px.setFixedSize(251, 137)

        self.def_1_px.setPixmap(QtGui.QPixmap(ResetGeneratorDialog.TEMPLATE_DIR + "default_reset_one.jpg"))
        self.def_2_px.setPixmap(QtGui.QPixmap(ResetGeneratorDialog.TEMPLATE_DIR + "default_reset_two.jpg"))

        self.button_layout.addItem(
            QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Minimum))
        self.button_layout.addWidget(self.help_btn)
        self.button_layout.addWidget(self.cancel_btn)
        self.button_layout.addWidget(self.generate_btn)
        self.button_layout.addWidget(self.apply_btn)

        gen_1_lb = QtWidgets.QLabel("Generated Frame Two:")
        gen_2_lb = QtWidgets.QLabel("Generated Frame Three:")
        self.gen_1_sb.setMaximumWidth(40)
        self.gen_2_sb.setMaximumWidth(40)
        self.gen_1_sb.setRange(1, ResetGenerator.CAPTURE_COUNT)
        self.gen_2_sb.setRange(1, ResetGenerator.CAPTURE_COUNT)
        self.gen_1_sb.setValue(2)
        self.gen_2_sb.setValue(3)

        gen_1_top_layout = QtWidgets.QHBoxLayout()
        gen_1_top_layout.addWidget(self.gen_1_sb)
        gen_1_top_layout.addWidget(gen_1_lb)

        gen_2_top_layout = QtWidgets.QHBoxLayout()
        gen_2_top_layout.addWidget(self.gen_2_sb)
        gen_2_top_layout.addWidget(gen_2_lb)

        def_1_lb = QtWidgets.QLabel("Desired Frame Two:")
        def_2_lb = QtWidgets.QLabel("Desired Frame Three:")

        # Configure Layout
        self.menu_layout.addLayout(gen_1_top_layout, 1, 0)
        self.menu_layout.addLayout(gen_2_top_layout, 1, 1)
        self.menu_layout.addWidget(self.gen_1_px, 2, 0)
        self.menu_layout.addWidget(self.gen_2_px, 2, 1)
        self.menu_layout.addWidget(def_1_lb, 3, 0)
        self.menu_layout.addWidget(def_2_lb, 3, 1)
        self.menu_layout.addWidget(self.def_1_px, 4, 0)
        self.menu_layout.addWidget(self.def_2_px, 4, 1)
        self.menu_layout.addLayout(self.button_layout, 5, 0, 1, 2)

        self.generate_btn.clicked.connect(self.generate_clicked)
        self.apply_btn.clicked.connect(self.apply_clicked)
        self.cancel_btn.clicked.connect(self.cancel_clicked)
        self.help_btn.clicked.connect(self.help_dialog.show)
        self.gen_1_sb.valueChanged.connect(self.gen_1_changed)
        self.gen_2_sb.valueChanged.connect(self.gen_2_changed)

    def show(self):
        self._reset_generator = ResetGenerator()
        self._reset_generator.generated.connect(self.on_generate)
        self._reset_generator.error.connect(self.on_error)

        self.gen_1_px.clear()
        self.gen_2_px.clear()
        self.generate_btn.setText("Generate")
        self.generate_btn.setEnabled(True)
        self.apply_btn.setEnabled(False)
        self.gen_1_sb.setEnabled(False)
        self.gen_2_sb.setEnabled(False)
        super().show()

    def hide(self):
        self._reset_generator.stop()
        super().hide()

    def generate_clicked(self):
        self.generate_btn.setText("Waiting..")
        self.generate_btn.setEnabled(False)
        self._reset_generator.start()

    def apply_clicked(self):
        try:
            os.remove(ResetGeneratorDialog.TEMPLATE_DIR + "generated_reset_one.jpg")
        except FileNotFoundError:
            pass

        try:
            os.remove(ResetGeneratorDialog.TEMPLATE_DIR + "generated_reset_two.jpg")
        except FileNotFoundError:
            pass

        try:
            os.rename(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(self.gen_1_sb.value()) + ".jpg",  ResetGeneratorDialog.TEMPLATE_DIR + "generated_reset_one.jpg")
        except FileNotFoundError:
            pass

        try:
            os.rename(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(self.gen_2_sb.value()) + ".jpg",  ResetGeneratorDialog.TEMPLATE_DIR + "generated_reset_two.jpg")
        except FileNotFoundError:
            pass

        for i in range(ResetGenerator.CAPTURE_COUNT + 1):
            try:
                os.remove(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(i) + ".jpg")
            except FileNotFoundError:
                pass

        config.set_key("advanced", "reset_frame_one", ResetGeneratorDialog.TEMPLATE_DIR + "generated_reset_one.jpg")
        config.set_key("advanced", "reset_frame_two", ResetGeneratorDialog.TEMPLATE_DIR + "generated_reset_two.jpg")
        config.save_config()

        self._reset_generator.stop()
        self.hide()

    def cancel_clicked(self):
        for i in range(ResetGenerator.CAPTURE_COUNT):
            try:
                os.remove(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(i) + ".jpg")
            except FileNotFoundError:
                pass

        self._reset_generator.stop()
        self.hide()

    def on_generate(self):
        self.gen_1_px.setPixmap(QtGui.QPixmap(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_2.jpg").scaledToWidth(251).scaledToHeight(137))
        self.gen_2_px.setPixmap(QtGui.QPixmap(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_3.jpg").scaledToWidth(251).scaledToHeight(137))
        self.gen_1_sb.setValue(2)
        self.gen_2_sb.setValue(3)
        self.generate_btn.setText("Generate")
        self.generate_btn.setEnabled(True)
        self.apply_btn.setEnabled(True)
        self.gen_1_sb.setEnabled(True)
        self.gen_2_sb.setEnabled(True)

    def gen_1_changed(self, value):
        self.gen_1_px.setPixmap(QtGui.QPixmap(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(value) + ".jpg").scaledToWidth(251).scaledToHeight(137))

    def gen_2_changed(self, value):
        self.gen_2_px.setPixmap(QtGui.QPixmap(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(value) + ".jpg").scaledToWidth(251).scaledToHeight(137))

    def closeEvent(self, event):
        for i in range(ResetGenerator.CAPTURE_COUNT):
            try:
                os.remove(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(i) + ".jpg")
            except FileNotFoundError:
                pass

        self._reset_generator.stop()
        super().closeEvent(event)

    def on_error(self, error):
        self.generate_btn.setText("Generate")
        self.generate_btn.setEnabled(True)
        self.apply_btn.setEnabled(False)
        self.display_error_message(error)

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


class ResetGenerator(QtCore.QThread):
    CAPTURE_COUNT = 5

    generated = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self._running = False
        self._game_capture = GameCapture(config.get("game", "process_name"), config.get("game", "game_region"), GAME_JP)

    def run(self):
        self._running = True
        reset_occurred = False
        frame = 0

        generated_frames = []

        while self._running:
            c_time = time.time()
            try:
                self._game_capture.capture()
            except:
                self.error.emit("Unable to capture " + config.get("game", "process_name"))
                self.stop()
                break

            reset_region = self._game_capture.get_region(RESET_REGION)
            fadeout_region = self._game_capture.get_region(FADEOUT_REGION)

            if is_black(fadeout_region, 0.1, 0.97):
                reset_occurred = True

            if reset_occurred:
                if not is_black(fadeout_region, config.get("thresholds", "black_threshold"), 0.99):
                    frame += 1

                    if frame <= self.CAPTURE_COUNT:
                        generated_frames.append(reset_region)
                    else:
                        self._running = False

            try:
                time.sleep((1 / 29.97) - (time.time() - c_time))
            except ValueError:
                pass

        for i, frame in enumerate(generated_frames):
            cv2.imwrite(ResetGeneratorDialog.TEMPLATE_DIR + "generated_temp_" + str(i + 1) + ".jpg", frame)

        self.generated.emit()

    def stop(self):
        self._running = False



