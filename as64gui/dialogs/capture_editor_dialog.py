from PyQt5 import QtWidgets
from PyQt5 import QtGui as QtGui
from PyQt5 import QtCore as QtCore

import cv2

from as64core import capture_window, config
from as64core import resource_utils
from ..widgets import HLine
from ..graphics import RectangleSelector
from ..constants import (
    ICON_PATH
)


class CaptureEditor(QtWidgets.QDialog):
    def __init__(self, parent=None):
        QtWidgets.QDialog.__init__(self, parent, QtCore.Qt.WindowSystemMenuHint | QtCore.Qt.WindowCloseButtonHint)

        self.window_title = "Game Capture Editor"
        self.setWindowIcon(QtGui.QIcon(resource_utils.resource_path(ICON_PATH)))

        # File Paths
        # TODO: ADD TO CONSTANTS
        self.preview_image_path = r'resources/images/game_preview.png'
        self.preview_not_found_image_path = r'resources/images/game_preview_not_found.png'

        # Layouts
        self.main_layout = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QGridLayout()
        self.right_layout = QtWidgets.QGridLayout()

        # Primary Widgets
        self.left_widget = QtWidgets.QWidget(self)
        self.right_widget = QtWidgets.QWidget(self)

        # Right Panel Widgets
        self.game_region_panel = RectangleCapturePanel("Game Region")
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

        # Left Panel Widgets
        self.process_lb = QtWidgets.QLabel("Process:")
        self.process_combo = QtWidgets.QComboBox()
        self.capture_btn = QtWidgets.QPushButton("Capture")

        # Graphics View
        self.graphics_scene = CaptureGraphicsScene()
        self.graphics_view = QtWidgets.QGraphicsView(self.graphics_scene)

        # Graphics Scene Items
        self.game_region_selector = RectangleSelector(0, 0, 50, 50)

        self.preview_pixmap = QtGui.QPixmap()

        self.initialize()

    def initialize(self):
        self.setWindowTitle(self.window_title)

        # Set Top Level Layouts
        self.setLayout(self.main_layout)
        self.left_widget.setLayout(self.left_layout)
        self.right_widget.setLayout(self.right_layout)

        self.right_widget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Configure Top Level Widgets
        self.left_widget.setFixedWidth(220)
        self.right_widget.setFixedWidth(220)

        # Add Top Level Widgets
        self.main_layout.addWidget(self.left_widget)
        self.main_layout.addWidget(self.graphics_view)
        self.main_layout.addWidget(self.right_widget)

        # Left Widget
        self.capture_btn.setDefault(False)
        self.capture_btn.setAutoDefault(False)
        self.process_combo.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)

        self._refresh_process_list()

        self.left_layout.addWidget(self.process_lb, 0, 0)
        self.left_layout.addWidget(self.process_combo, 0, 1)
        self.left_layout.addWidget(self.capture_btn, 1, 0, 1, 2)

        self.left_layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), 3, 0)

        # Right Widget
        self.apply_btn.setDefault(False)
        self.apply_btn.setAutoDefault(False)
        self.cancel_btn.setDefault(False)
        self.cancel_btn.setAutoDefault(False)

        self.right_layout.addWidget(self.game_region_panel, 5, 0, 1, 2)
        self.right_layout.addItem(QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding), 9, 0)
        self.right_layout.addWidget(HLine(), 10, 0, 1, 2)
        self.right_layout.addWidget(self.apply_btn, 15, 0)
        self.right_layout.addWidget(self.cancel_btn, 15, 1)

        # Configure Graphics View
        self.refresh_graphics_scene()

        # Connections
        self.graphics_scene.item_update.connect(self.on_graphics_item_update)

        self.capture_btn.clicked.connect(self.refresh_graphics_scene)
        self.apply_btn.clicked.connect(self.apply_clicked)
        self.cancel_btn.clicked.connect(self.cancel_clicked)
        self.game_region_panel.updated.connect(self.on_game_region_panel_update)
        self.process_combo.currentIndexChanged.connect(self.refresh_graphics_scene)

        self.refresh_graphics_scene()

    def _refresh_process_list(self):
        self.process_combo.clear()
        self._process_list = capture_window.get_visible_processes()
        self.process_combo.addItems([proc[0].name() for proc in self._process_list])

    def show(self):
        # Load game_region from preferences
        game_region = config.get('game', 'game_region')
        self.game_region_selector.resize(game_region[2], game_region[3])
        self.game_region_selector.setPos(game_region[0], game_region[1])

        self.game_region_panel.update_text(*[str(v) for v in game_region])

        self._refresh_process_list()

        p_name = config.get("game", "process_name")

        for i in range(len(self._process_list)):
            if self._process_list[i][0].name() == p_name:
                self.process_combo.setCurrentIndex(i)

        self.refresh_graphics_scene()

        config.create_rollback()
        super().show()

    def apply_clicked(self):
        config.set_key("game", "game_region", self.game_region_panel.get_data())
        config.set_key("game", "process_name", self.process_combo.currentText())
        config.save_config()
        self.close()

    def cancel_clicked(self):
        self.close()

    def on_graphics_item_update(self, e):
        if e.object_name == self.game_region_selector.object_name:
            rect = e.get_view_space_rect()
            self.game_region_panel.update_text(*[str(v) for v in rect])

    def on_game_region_panel_update(self, e):
        self.game_region_selector.resize(e[2], e[3])
        self.game_region_selector.setPos(e[0], e[1])

    def refresh_graphics_scene(self):
        """
        Clears the graphics scene and view, redraws all components including new screen capture
        :return:
        """

        # Remove all items that may be in the scene before clearing. Prevents program crash.
        self.graphics_scene.removeItem(self.game_region_selector)

        # Clear scene and update viewport
        self.graphics_scene.clear()
        self.graphics_view.update()

        # Update screen capture
        selected_hwnd = 0

        try:
            selected_hwnd = self._process_list[self.process_combo.currentIndex()][1]
        except IndexError:
            pass

        if selected_hwnd:
            try:
                preview_image = capture_window.capture(selected_hwnd)
                cv2.imwrite(resource_utils.resource_path(self.preview_image_path), preview_image)
            except:
                pass

        self.preview_pixmap.load(resource_utils.resource_path(self.preview_image_path))

        # Re-add all items to scene
        self.graphics_scene.addPixmap(self.preview_pixmap)
        self.graphics_scene.addItem(self.game_region_selector)

    def closeEvent(self, e):
        config.rollback()
        super().closeEvent(e)


class RectangleCapturePanel(QtWidgets.QWidget):
    updated = QtCore.pyqtSignal(list)

    def __init__(self, title, parent=None):
        super().__init__(parent)

        # Layout
        self.main_layout = QtWidgets.QGridLayout(self)

        # Widgets
        self.title_lb = QtWidgets.QLabel(title)
        self.xoffset_lb = QtWidgets.QLabel("X Offset:")
        self.yoffset_lb = QtWidgets.QLabel("Y Offset:")
        self.width_lb = QtWidgets.QLabel("Width:")
        self.height_lb = QtWidgets.QLabel("Height:")
        self.xoffset_le = QtWidgets.QLineEdit()
        self.yoffset_le = QtWidgets.QLineEdit()
        self.width_le = QtWidgets.QLineEdit()
        self.height_le = QtWidgets.QLineEdit()

        self.int_validator = QtGui.QIntValidator()

        self.initialize()

    def initialize(self):

        # Set Layout
        self.setLayout(self.main_layout)

        # Configure Widgets
        self.xoffset_lb.setFixedWidth(70)
        self.yoffset_lb.setFixedWidth(70)
        self.width_lb.setFixedWidth(70)
        self.height_lb.setFixedWidth(70)

        self.xoffset_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.yoffset_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.width_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        self.height_lb.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.xoffset_le.setMinimumWidth(80)
        self.yoffset_le.setMinimumWidth(80)
        self.width_le.setMinimumWidth(80)
        self.height_le.setMinimumWidth(80)

        self.xoffset_le.setValidator(self.int_validator)
        self.yoffset_le.setValidator(self.int_validator)
        self.width_le.setValidator(self.int_validator)
        self.height_le.setValidator(self.int_validator)

        # Configure Layout
        line = HLine()

        self.main_layout.addWidget(self.title_lb, 0, 0, 1, 2)
        self.main_layout.addWidget(line, 1, 0, 1, 2)
        self.main_layout.addWidget(self.xoffset_lb, 2, 0)
        self.main_layout.addWidget(self.yoffset_lb, 3, 0)
        self.main_layout.addWidget(self.width_lb, 4, 0)
        self.main_layout.addWidget(self.height_lb, 5, 0)

        self.main_layout.addWidget(self.xoffset_le, 2, 1)
        self.main_layout.addWidget(self.yoffset_le, 3, 1)
        self.main_layout.addWidget(self.width_le, 4, 1)
        self.main_layout.addWidget(self.height_le, 5, 1)

        # Connections
        self.xoffset_le.editingFinished.connect(self.text_changed)
        self.yoffset_le.editingFinished.connect(self.text_changed)
        self.width_le.editingFinished.connect(self.text_changed)
        self.height_le.editingFinished.connect(self.text_changed)

    def update_text(self, x_offset=None, y_offset=None, width=None, height=None):
        if x_offset:
            self.xoffset_le.setText(x_offset)

        if y_offset:
            self.yoffset_le.setText(y_offset)

        if width:
            self.width_le.setText(width)

        if height:
            self.height_le.setText(height)

    def text_changed(self):
        try:
            self.updated.emit(self.get_data())
        except:
            pass

    def get_data(self):
        return [int(float(self.xoffset_le.text())), int(float(self.yoffset_le.text())),
                int(float(self.width_le.text())), int(float(self.height_le.text()))]


class CaptureGraphicsScene(QtWidgets.QGraphicsScene):
    item_update = QtCore.pyqtSignal(object)

