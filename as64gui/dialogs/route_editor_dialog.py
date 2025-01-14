from os import path
from json import JSONDecodeError
import re
import xml.etree.ElementTree as ET
from functools import partial

from PyQt6 import QtWidgets, QtCore, QtGui
from PyQt6.QtGui import QIcon, QIntValidator, QAction

from as64core import resource_utils
from as64core import route_loader, config
from as64core.route import Route, Split
from as64gui.widgets import TableWidgetDragRows, HLine
from as64gui.constants import (
    ICON_PATH
)
from as64core.constants import (
    SPLIT_NORMAL,
    SPLIT_FADE_ONLY,
    SPLIT_MIPS,
    SPLIT_MIPS_X,
    SPLIT_XCAM,
    SPLIT_FINAL,
    TIMING_RTA,
    TIMING_UP_RTA,
    TIMING_FILE_SELECT
)


class RouteEditor(QtWidgets.QMainWindow):
    route_updated = QtCore.pyqtSignal()

    CATEGORIES = ["0 Star", "1 Star", "16 Star", "70 Star", "120 Star"]

    DOWN = 1
    UP = -1
    DISABLE_NONE = 1
    DISABLE_FADEOUT = 2
    DISABLE_FADEIN = 4
    DISABLE_XCAM = 8
    DISABLE_STAR_COUNT = 16

    def __init__(self, parent=None):
        super(RouteEditor, self).__init__(parent)

        # Route
        self.route = None
        self.route_path = None

        self.window_title = "Route Editor"
        self.width = 780
        self.height = 600
        self.setWindowIcon(QIcon(resource_utils.resource_path(ICON_PATH)))

        self.split_types = [SPLIT_NORMAL, SPLIT_FADE_ONLY, SPLIT_MIPS, SPLIT_MIPS_X, SPLIT_XCAM, SPLIT_FINAL]

        self.split_types_flags = {
            SPLIT_NORMAL: RouteEditor.DISABLE_XCAM,
            SPLIT_FADE_ONLY: RouteEditor.DISABLE_STAR_COUNT | RouteEditor.DISABLE_XCAM,
            SPLIT_MIPS: RouteEditor.DISABLE_XCAM | RouteEditor.DISABLE_FADEOUT | RouteEditor.DISABLE_FADEIN,
            SPLIT_MIPS_X: RouteEditor.DISABLE_XCAM | RouteEditor.DISABLE_FADEOUT | RouteEditor.DISABLE_FADEIN,
            SPLIT_XCAM: RouteEditor.DISABLE_NONE,
            SPLIT_FINAL: RouteEditor.DISABLE_XCAM | RouteEditor.DISABLE_FADEOUT | RouteEditor.DISABLE_FADEIN
        }

        # Menu Bar
        self.menu_bar = None

        # Layouts
        self.main_layout = QtWidgets.QVBoxLayout()
        self.add_delete_layout = QtWidgets.QVBoxLayout()
        self.apply_close_layout = QtWidgets.QHBoxLayout()
        self.global_settings_layout = QtWidgets.QGridLayout()

        # Widgets
        self.insert_above_btn = QtWidgets.QPushButton("Insert Above")
        self.insert_below_btn = QtWidgets.QPushButton("Insert Below")
        self.remove_btn = QtWidgets.QPushButton("Remove")
        self.move_up_btn = QtWidgets.QPushButton("Move Up")
        self.move_down_btn = QtWidgets.QPushButton("Move Down")
        self.split_table = TableWidgetDragRows()
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")

        self.title_lb = QtWidgets.QLabel("Title:")
        self.init_star_lb = QtWidgets.QLabel("Initial Star:")
        self.version_lb = QtWidgets.QLabel("Version:")
        self.category_lb = QtWidgets.QLabel("Category:")
        self.timing_lb = QtWidgets.QLabel("Timing:")

        self.title_le = QtWidgets.QLineEdit()
        self.init_star_le = QtWidgets.QLineEdit()

        self.version_combo = QtWidgets.QComboBox()
        self.category_combo = QtWidgets.QComboBox()
        self.timing_combo = QtWidgets.QComboBox()

        self.int_validator = QIntValidator()

        self.initialize()

    def initialize(self):
        # Set Window Properties
        self.setWindowTitle(self.window_title)
        self.resize(self.width, self.height)

        # Menu Bar
        self.menu_bar = self.menuBar()
        self.file_menu()

        # Main Widget
        main_widget = QtWidgets.QWidget()
        self.setCentralWidget(main_widget)
        main_widget.setLayout(self.main_layout)

        # Configure Widgets
        self.split_table.setIconSize(QtCore.QSize(30, 30))
        self.split_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.Stretch)
        self.split_table.setColumnCount(7)
        self.split_table.setHorizontalHeaderLabels(["Icon", "Split Title", "Star count", "Fadeout", "Fadein", "X-Cam", "Split Type"])

        self.insert_above_btn.setMinimumWidth(125)
        self.insert_below_btn.setMinimumWidth(125)
        self.remove_btn.setMinimumWidth(125)
        self.move_up_btn.setMinimumWidth(125)
        self.move_down_btn.setMinimumWidth(125)

        self.apply_btn.setMaximumWidth(100)
        self.cancel_btn.setMaximumWidth(100)

        self.title_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.init_star_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.version_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.category_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)
        self.timing_lb.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight | QtCore.Qt.AlignmentFlag.AlignVCenter)

        self.title_lb.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)
        self.init_star_lb.setSizePolicy(QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Minimum)

        self.init_star_le.setValidator(self.int_validator)

        self.version_combo.setMaximumWidth(65)
        self.version_combo.addItem("JP")
        self.version_combo.addItem("US")

        self.timing_combo.setMaximumWidth(80)
        self.timing_combo.addItem(TIMING_RTA)
        self.timing_combo.addItem(TIMING_UP_RTA)
        self.timing_combo.addItem(TIMING_FILE_SELECT)

        for category in self.CATEGORIES:
            self.category_combo.addItem(category)
        self.category_combo.setEditable(True)
        self.category_combo.lineEdit().setText("")

        self.init_star_le.setFixedWidth(45)

        # add_delete Layout
        self.add_delete_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignLeft)
        self.add_delete_layout.addWidget(self.insert_above_btn)
        self.add_delete_layout.addWidget(self.insert_below_btn)
        self.add_delete_layout.addWidget(self.remove_btn)
        self.add_delete_layout.addWidget(self.move_up_btn)
        self.add_delete_layout.addWidget(self.move_down_btn)
        self.add_delete_layout.addItem(QtWidgets.QSpacerItem(10, 10, QtWidgets.QSizePolicy.Policy.Minimum, QtWidgets.QSizePolicy.Policy.Expanding))

        # apply_close Layout
        self.apply_close_layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignRight)
        self.apply_close_layout.addWidget(self.apply_btn)
        self.apply_close_layout.addWidget(self.cancel_btn)

        # Global Settings Layout
        self.global_settings_layout.addWidget(self.title_lb, 5, 0)
        self.global_settings_layout.addWidget(self.title_le, 5, 1)
        self.global_settings_layout.addWidget(self.category_lb, 6, 0)
        self.global_settings_layout.addWidget(self.category_combo, 6, 1)
        self.global_settings_layout.addWidget(self.init_star_lb, 7, 0)
        self.global_settings_layout.addWidget(self.init_star_le, 7, 1)
        self.global_settings_layout.addWidget(self.version_lb, 8, 0)
        self.global_settings_layout.addWidget(self.version_combo, 8, 1)
        self.global_settings_layout.addWidget(self.timing_lb, 9, 0)
        self.global_settings_layout.addWidget(self.timing_combo, 9, 1)

        # Splits Layout
        splits_layout = QtWidgets.QHBoxLayout()
        splits_layout.addLayout(self.add_delete_layout)
        splits_layout.addWidget(self.split_table)

        # Main Layout
        self.main_layout.addLayout(self.global_settings_layout)
        self.main_layout.addWidget(HLine())
        self.main_layout.addLayout(splits_layout)
        self.main_layout.addLayout(self.apply_close_layout)

        # Connections
        self.insert_above_btn.clicked.connect(lambda: self._insert_row(self.split_table.currentIndex().row()))
        self.insert_below_btn.clicked.connect(lambda: self._insert_row(self.split_table.currentIndex().row() + 1))
        self.remove_btn.clicked.connect(self.remove_clicked)
        self.move_up_btn.clicked.connect(lambda: self.moveCurrentRow(self.UP))
        self.move_down_btn.clicked.connect(lambda: self.moveCurrentRow(self.DOWN))
        self.apply_btn.clicked.connect(self.apply_clicked)
        self.cancel_btn.clicked.connect(self.cancel_clicked)
        self.split_table.cellDoubleClicked.connect(self.double_clicked)

    def file_menu(self):
        """Create file menu"""
        file_sub_menu = self.menu_bar.addMenu('File')

        # Create Actions
        new_action = QAction('New', self)
        open_action = QAction('Open', self)
        save_action = QAction('Save', self)
        save_as_action = QAction('Save As..', self)
        convert_action = QAction('Convert LSS', self)
        exit_action = QAction('Exit', self)

        # Configure ToolTips
        new_action.setStatusTip('Create new route')
        open_action.setStatusTip('Open route from file')
        save_action.setStatusTip('Save route')
        save_as_action.setStatusTip('Save route as')
        convert_action.setStatusTip('Convert LiveSplit route')
        exit_action.setStatusTip('Exit Application')

        # Set Shortcuts
        new_action.setShortcut('CTRL+N')
        open_action.setShortcut('CTRL+O')
        save_action.setShortcut('CTRL+S')
        exit_action.setShortcut('CTRL+W')

        # Connections
        new_action.triggered.connect(self.new)
        open_action.triggered.connect(self.open)
        save_action.triggered.connect(self.save)
        save_as_action.triggered.connect(self.save_as)
        convert_action.triggered.connect(self.convert_lss)
        exit_action.triggered.connect(self.close)

        # Add Actions
        file_sub_menu.addAction(new_action)
        file_sub_menu.addAction(open_action)
        file_sub_menu.addSeparator()
        file_sub_menu.addAction(save_action)
        file_sub_menu.addAction(save_as_action)
        file_sub_menu.addSeparator()
        file_sub_menu.addAction(convert_action)
        file_sub_menu.addSeparator()
        file_sub_menu.addAction(exit_action)

    def show(self):
        self.load_route()
        super().show()

    def moveCurrentRow(self, direction=DOWN):
        if direction not in (self.DOWN, self.UP):
            return

        indexes = sorted(set(item.row() for item in self.split_table.selectedItems()), reverse=(direction == self.DOWN))
        new_indexes = []

        if not indexes:
            return

        for idx in indexes:
            new_idx = idx + direction

            if new_idx >= self.split_table.rowCount() or new_idx < 0:
                break

            new_indexes.append(new_idx)

            try:
                icon_path = self.split_table.item(idx, 0).toolTip()
            except AttributeError:
                icon_path = None

            row_data = [
                icon_path,
                self.split_table.item(idx, 1).text(),
                self.split_table.item(idx, 2).text(),
                self.split_table.item(idx, 3).text(),
                self.split_table.item(idx, 4).text(),
                self.split_table.item(idx, 5).text(),
                self.split_table.cellWidget(idx, 6).currentText()
            ]

            self.split_table.removeRow(idx)
            self._insert_row(new_idx, row_data[0], row_data[1], row_data[2], row_data[3], row_data[4], row_data[5], row_data[6])

        self.split_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.MultiSelection)

        for idx in new_indexes:
            for col in range(self.split_table.columnCount()):
                try:
                    self.split_table.item(idx, col).setSelected(True)
                except AttributeError:
                    pass

        self.split_table.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)

    def remove_clicked(self):
        indexes = sorted(set(item.row() for item in self.split_table.selectedItems()), reverse=True)

        for index in indexes:
            self.split_table.removeRow(index)
            self.split_table.selectRow(index)

    def apply_clicked(self):
        err_code = self.save()

        if err_code == -1:
            return

        self.close()

    def cancel_clicked(self):
        self.close()

    def double_clicked(self, x, y):
        if y != 0:
            return

        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Choose Icon", resource_utils.base_path("resources/icons"))

        if not file_name:
            return

        # Convert to relative path, if possible
        file_path = resource_utils.abs_to_rel(file_name)

        # Create Item
        item = QtWidgets.QTableWidgetItem()

        item.setIcon(QIcon(file_path))
        item.setToolTip(file_path)
        item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
        self.split_table.setItem(x, 0, item)

    def load_route(self, route_path=None):
        """
        Loads route from path specified in preferences
        :return:
        """
        if not route_path:
            _route_path = config.get("route", "path")
        else:
            _route_path = route_path

        try:
            route = route_loader.load(_route_path)

            if route:
                route_error = route_loader.validate_route(route)
            else:
                self.new()
                return

            if route_error:
                self.display_error_message(route_error, "Route Error")

        except FileNotFoundError:
            route = None
            self.display_error_message("Route file not found.", "Invalid route: {}".format(path.basename(_route_path)))
        except KeyError:
            route = None
            self.display_error_message("Invalid or missing Key", "Invalid route: {}".format(path.basename(_route_path)))
        except JSONDecodeError:
            route = None
            self.display_error_message("Invalid JSON formatting", "Invalid route: {}".format(path.basename(_route_path)))
        except PermissionError:
            route = None

        if route:
            self.route = route
            self.route_path = self.route.file_path
            config.set_key("route", "path", resource_utils.abs_to_rel(_route_path))
            config.save_config()
            self.display_route()

    def display_route(self):
        if not self.route:
            return

        self.title_le.setText(self.route.title)
        self.init_star_le.setText(str(self.route.initial_star))
        self.category_combo.lineEdit().setText(self.route.category)

        if self.route.version == "US":
            self.version_combo.setCurrentIndex(1)
        else:
            self.version_combo.setCurrentIndex(0)

        if self.route.timing == TIMING_RTA:
            self.timing_combo.setCurrentIndex(0)
        elif self.route.timing == TIMING_UP_RTA:
            self.timing_combo.setCurrentIndex(1)
        elif self.route.timing == TIMING_FILE_SELECT:
            self.timing_combo.setCurrentIndex(2)

        splits_length = len(self.route.splits)
        self.split_table.setRowCount(splits_length)

        for i in range(splits_length):
            item = QtWidgets.QTableWidgetItem()
            item.setIcon(QIcon(self.route.splits[i].icon_path))
            item.setToolTip(self.route.splits[i].icon_path)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
            self.split_table.setItem(i, 0, item)
            self.split_table.setItem(i, 1, QtWidgets.QTableWidgetItem(self.route.splits[i].title))
            self.split_table.setItem(i, 2, QtWidgets.QTableWidgetItem(str(self.route.splits[i].star_count)))
            self.split_table.setItem(i, 3, QtWidgets.QTableWidgetItem(str(self.route.splits[i].on_fadeout)))
            self.split_table.setItem(i, 4, QtWidgets.QTableWidgetItem(str(self.route.splits[i].on_fadein)))
            self.split_table.setItem(i, 5, QtWidgets.QTableWidgetItem(str(self.route.splits[i].on_xcam)))
            self._add_split_combo(i, self.route.splits[i].split_type)
            self._set_disable_columns(i, self.route.splits[i].split_type,
                                      str(self.route.splits[i].on_fadeout),
                                      str(self.route.splits[i].on_fadein),
                                      str(self.route.splits[i].on_xcam),
                                      str(self.route.splits[i].star_count))

    def display_error_message(self, message, title):
        """
        Display a warning dialog with given title and message
        :param title: Window title
        :param message: Warning/error message
        :return:
        """
        msg = QtWidgets.QMessageBox(self)
        msg.setIcon(QtWidgets.QMessageBox.Icon.Warning)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.show()

    def new(self):
        self.route = None
        self.route_path = None

        self.split_table.setRowCount(0)

        self.title_le.setText("")
        self.init_star_le.setText("")
        self.version_combo.setCurrentIndex(0)

    def open(self):
        """ Show native file dialog to select a .route file for use. """
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Route", resource_utils.absolute_path("routes"),
                                                             "AS64 Route Files (*.as64)")

        if file_name:
            self.load_route(file_name)

    def save_as(self):
        file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Route", resource_utils.base_path() + "/routes", "AS64 Route Files (*.as64)")

        if file_name != '':
            self.route_path = file_name
        else:
            return

        self.save()

    def save(self):
        self.apply_btn.setFocus()

        splits = []

        if self.split_table.rowCount() < 1:
            self.display_error_message("No Splits", "Route Error")
            return -1

        for row in range(self.split_table.rowCount()):
            title = self.split_table.item(row, 1).text()
            if len(title) <= 0:
                self.display_error_message("Invalid Title - Row: " + str(row + 1), "Route Error")
                self.split_table.setCurrentCell(row, 1)
                return -1

            try:
                star_count = int(self.split_table.item(row, 2).text())
            except (ValueError, AttributeError):
                if not self.split_table.cellWidget(row, 6).currentText() == SPLIT_FADE_ONLY:
                    self.display_error_message("Invalid Star Count - Row: " + str(row + 1), "Route Error")
                    self.split_table.setCurrentCell(row, 2)
                    return -1
                else:
                    star_count = -1

            try:
                fadeouts = int(self.split_table.item(row, 3).text())
            except (ValueError, AttributeError):
                if self.split_table.cellWidget(row, 6).currentText == SPLIT_NORMAL:
                    self.display_error_message("Invalid Fadeout - Row: " + str(row + 1), "Route Error")
                    self.split_table.setCurrentCell(row, 3)
                    return -1
                else:
                    fadeouts = -1

            try:
                fadeins = int(self.split_table.item(row, 4).text())
            except (ValueError, AttributeError):
                if self.split_table.cellWidget(row, 6).currentText == SPLIT_NORMAL:
                    self.display_error_message("Invalid Fadein - Row: " + str(row + 1), "Route Error")
                    self.split_table.setCurrentCell(row, 4)
                    return -1
                else:
                    fadeins = -1


            try:
                xcam = int(self.split_table.item(row, 5).text())
            except (ValueError, AttributeError):
                if self.split_table.cellWidget(row, 6).currentText == SPLIT_XCAM:
                    self.display_error_message("Invalid XCam - Row: " + str(row + 1), "Route Error")
                    self.split_table.setCurrentCell(row, 5)
                    return -1
                else:
                    xcam = -1

            try:
                icon_path = self.split_table.item(row, 0).toolTip()
            except (ValueError, AttributeError):
                icon_path = ""

            split_type = self.split_table.cellWidget(row, 6).currentText()

            splits.append(Split(title,
                                star_count,
                                fadeouts,
                                fadeins,
                                xcam,
                                split_type,
                                icon_path))

        title = self.title_le.text()
        if len(title) <= 0:
            self.display_error_message("Invalid Route Title", "Route Error")
            return -1

        try:
            initial_star = int(self.init_star_le.text())
        except (ValueError, AttributeError):
            self.display_error_message("Invalid Initial Star", "Route Error")
            return -1

        category = self.category_combo.lineEdit().text()

        route = Route(self.route_path,
                      title,
                      splits,
                      initial_star,
                      self.version_combo.itemText(self.version_combo.currentIndex()),
                      category,
                      self.timing_combo.itemText(self.timing_combo.currentIndex()))

        route_error = route_loader.validate_route(route)

        if route_error:
            self.display_error_message(route_error, "Route Error")
            return -1

        if not self.route_path:
            file_name, _ = QtWidgets.QFileDialog.getSaveFileName(self, "Save Route", resource_utils.base_path() + "/routes", "AS64 Route Files (*.as64)")

            if file_name != '':
                self.route_path = file_name
            else:
                return -1

        route_loader.save(route, self.route_path)
        config.set_key("route", "path", self.route_path)
        config.save_config()
        self.route_updated.emit()

    def convert_lss(self):
        file_name, _ = QtWidgets.QFileDialog.getOpenFileName(self, "Open Route", "",
                                                             "Livesplit (*.lss)")

        if not file_name:
            return

        self.new()

        tree = ET.parse(file_name)
        root = tree.getroot()
        segments = root.find('Segments')

        # Default initial star to 0
        self.init_star_le.setText("0")

        # STAGE NAMES
        DW_NAMES_IN = ['key1', 'key 1', 'bowser', 'dw', 'dark world', 'darkworld', 'bitdw', 'dworld']
        DW_NAMES_CONTAINS = ['key 1', 'dark world']

        LBLJ_NAMES_CONTAINS = ['lblj']

        FS_NAMES_IN = ['key2', 'key 2', 'fs', 'firesea', 'fire sea', 'bitfs', 'fsea']
        FS_NAMES_CONTAINS = ['key 2', 'fire sea']

        UPSTAIRS_NAMES_CONTAINS = [r'/up', r'/upstairs', 'upstairs']

        MIPS_NAMES = ['mips']

        BLJ_NAMES_IN = ['bljs', 'blj']

        is_16 = False
        for seg in reversed(segments):
            name = seg.find('Name').text

            numbers = re.findall(r'\d+', name)

            try:
                if int(numbers[len(numbers)-1]) == 16:
                    is_16 = True
                    break
                elif int(numbers[len(numbers)-1]) > 16:
                    break
            except (IndexError, ValueError):
                pass

        for i, child in enumerate(segments):
            name = child.find('Name').text

            # Attempt to determine star count
            numbers = re.findall(r'\d+', name)

            try:
                star_count = str(numbers[len(numbers)-1])
            except IndexError:
                star_count = ""

            # Determine most likely fadeout count & split type (will redo this code at some point, ran out of time :[ )
            fadeouts = "1"
            split_type = SPLIT_NORMAL

            name_delimited = name.lower().split()
            for s_name in DW_NAMES_IN:
                if s_name in name_delimited:
                    fadeouts = "2"

            for s_name in DW_NAMES_CONTAINS:
                if name.lower().find(s_name) != -1:
                    fadeouts = "2"

            for s_name in LBLJ_NAMES_CONTAINS:
                if name.lower().find(s_name) != -1:
                    fadeouts = "2"
                    star_count = "0"

            for s_name in FS_NAMES_IN:
                if s_name in name_delimited:
                    if is_16:
                        fadeouts = "3"
                    else:
                        fadeouts = "2"

            for s_name in FS_NAMES_CONTAINS:
                if name.lower().find(s_name) != -1:
                    if is_16:
                        fadeouts = "3"
                    else:
                        fadeouts = "2"

            for s_name in UPSTAIRS_NAMES_CONTAINS:
                if name.lower().find(s_name) != -1:
                    fadeouts = "4"

            for s_name in MIPS_NAMES:
                if s_name in name_delimited:
                    split_type = SPLIT_MIPS

            for s_name in BLJ_NAMES_IN:
                if s_name in name_delimited:
                    fadeouts = "4"

            if i == len(segments) - 1:
                split_type = SPLIT_FINAL

            if star_count == "" and i != len(segments) - 1:
                try:
                    star_count = self.split_table.item(self.split_table.rowCount() - 1, 2).text()
                except:
                    star_count = "0"

            self._insert_row(title=name,
                             star_count=star_count,
                             fadeouts=fadeouts,
                             row_type=split_type)

        # Set final star (as often not in split title)
        try:
            final_star = int(self.split_table.item(self.split_table.rowCount() - 1, 2).text())
        except IndexError:
            final_star = None
        except ValueError:
            try:
                prev_star_count = int(self.split_table.item(self.split_table.rowCount() - 2, 2).text())
                if prev_star_count == 16:
                    final_star = "16"
                elif prev_star_count == 69:
                    final_star = "70"
                elif prev_star_count == 119:
                    final_star = "120"
                elif prev_star_count >= 0:
                    final_star = str(prev_star_count)

                self.split_table.setItem(self.split_table.rowCount() - 1, 2, QtWidgets.QTableWidgetItem(final_star))
            except (ValueError, IndexError, UnboundLocalError):
                final_star = None

        # Set Category
        if final_star == "16":
            self.category_combo.lineEdit().setText("16 Star")
        elif final_star == "70":
            self.category_combo.lineEdit().setText("70 Star")
            self.version_combo.setCurrentIndex(1)
        elif final_star == "120":
            self.category_combo.lineEdit().setText("120 Star")

    def split_type_changed(self, combo):
        row = -1
        for i in range(self.split_table.rowCount()):
            if combo == self.split_table.cellWidget(i, 6):
                row = i
                break

        if row == -1:
            return

        self._set_disable_columns(row, self.split_table.cellWidget(row, 6).currentText())

    def _set_disable_columns(self, row, row_type, fadeouts="1", fadeins="0", xcam="1", star_count="0"):
        try:
            if self.split_types_flags[row_type] & RouteEditor.DISABLE_FADEOUT == RouteEditor.DISABLE_FADEOUT:
                self.split_table.item(row, 3).setText("-")
                self.split_table.item(row, 3).setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            else:
                self.split_table.item(row, 3).setText(fadeouts)
                self.split_table.item(row, 3).setFlags(
                    QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled)

            if self.split_types_flags[row_type] & RouteEditor.DISABLE_FADEIN == RouteEditor.DISABLE_FADEIN:
                self.split_table.item(row, 4).setText("-")
                self.split_table.item(row, 4).setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            else:
                self.split_table.item(row, 4).setText(fadeins)
                self.split_table.item(row, 4).setFlags(
                    QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled)

            if self.split_types_flags[row_type] & RouteEditor.DISABLE_XCAM == RouteEditor.DISABLE_XCAM:
                self.split_table.item(row, 5).setText("-")
                self.split_table.item(row, 5).setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            else:
                self.split_table.item(row, 5).setText(xcam)
                self.split_table.item(row, 5).setFlags(
                    QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled)

            if self.split_types_flags[row_type] & RouteEditor.DISABLE_STAR_COUNT == RouteEditor.DISABLE_STAR_COUNT:
                self.split_table.item(row, 2).setText("-")
                self.split_table.item(row, 2).setFlags(QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEnabled)
            else:
                self.split_table.item(row, 2).setText(star_count)
                self.split_table.item(row, 2).setFlags(
                    QtCore.Qt.ItemFlag.ItemIsSelectable | QtCore.Qt.ItemFlag.ItemIsEditable | QtCore.Qt.ItemFlag.ItemIsEnabled)
        except KeyError:
            pass

    def _insert_row(self, index=None, icon_path=None, title="", star_count="", fadeouts="1", fadeins="0", xcam="-1", row_type=SPLIT_NORMAL):
        if index is None:
            index = self.split_table.rowCount()

        index = max(index, 0)

        self.split_table.insertRow(index)

        # Timeout and fade-in count to be 0 by default
        if icon_path:
            item = QtWidgets.QTableWidgetItem()
            item.setIcon(QIcon(icon_path))
            item.setToolTip(icon_path)
            item.setFlags(QtCore.Qt.ItemFlag.ItemIsEnabled | QtCore.Qt.ItemFlag.ItemIsSelectable)
            self.split_table.setItem(index, 0, item)

        self.split_table.setItem(index, 1, QtWidgets.QTableWidgetItem(title))
        self.split_table.setItem(index, 2, QtWidgets.QTableWidgetItem(str(star_count)))
        self.split_table.setItem(index, 3, QtWidgets.QTableWidgetItem(""))
        self.split_table.setItem(index, 4, QtWidgets.QTableWidgetItem(""))
        self.split_table.setItem(index, 5, QtWidgets.QTableWidgetItem(""))

        self._add_split_combo(index, row_type)
        self._set_disable_columns(index, row_type, fadeouts, fadeins, xcam, star_count)
        self.split_table.selectRow(index)

    def _add_split_combo(self, row, default=SPLIT_NORMAL):
        combo = QtWidgets.QComboBox()

        for split_type in self.split_types:
            combo.addItem(split_type)

        self.split_table.setCellWidget(row, 6, combo)
        try:
            self.split_table.cellWidget(row, 6).setCurrentIndex(self.split_types.index(default))
        except ValueError:
            default = SPLIT_NORMAL

        combo.currentIndexChanged.connect(partial(self.split_type_changed, combo))

