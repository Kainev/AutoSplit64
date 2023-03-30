
from functools import partial
from typing import Any, List

from PyQt5.QtCore import QSize, Qt, pyqtSignal

from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QListWidgetItem,
    QWidget,
    QAbstractItemView,
    QLabel,
    QLineEdit,
    QComboBox,
    QSpacerItem,
    QSizePolicy,
    QListView,
    QPushButton,
    QGridLayout,
    QCheckBox,
    QSpinBox,
    QFileDialog,
    QApplication
)

from PyQt5.QtGui import (
    QPalette,
    QPixmap
)


from as64.api import SplitType, Version
from as64 import config, route
from as64.route import Route, Split, translate_lss
from as64ui.style import global_style_sheet
from as64ui.widgets.side_menu import SideMenu


class RouteEditor(QDialog):
    route_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Attributes
        self.setAttribute(Qt.WA_Moved)
        self.move(QApplication.desktop().screenGeometry(0).center() - self.rect().center())
        
        #
        self._current_path = None
        
        # Layouts
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        self._left_layout = QVBoxLayout()
        self._left_layout.setContentsMargins(0, 0, 10, 0)
        
        self._right_layout = QVBoxLayout()
        self._right_layout.setContentsMargins(10, 20, 10, 10)
        self._right_layout.setSpacing(15)
        
        # Widgets
        self._side_menu = SideMenu(self)
        
        self._properties = RoutePropertiesWidget(self)
        self._splits = RouteSplitsWidget(self)
        self._buttons = RouteButtonBar(self)
        
        # Configure Widgets
        self._side_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Populate layouts
        self._left_layout.addWidget(self._side_menu)
        
        self._right_layout.addWidget(self._properties)
        self._right_layout.addWidget(self._splits)
        self._right_layout.addWidget(self._buttons)
        
        self._layout.addLayout(self._left_layout)
        self._layout.addLayout(self._right_layout)     
        
        # Connect Signals
        self._buttons.add.connect(self._splits.add_split)
        self._buttons.insert.connect(self._splits.insert_split)
        self._buttons.remove.connect(self._splits.remove_split)
        self._buttons.apply.connect(self._apply)
        self._buttons.cancel.connect(self._cancel)
        
        self._side_menu.menu_click.connect(self._side_menu_click)
        
        #
        self.setMinimumSize(780, 650)
        
        self.setup_menu()

    def show(self):
        self._load_route(config.get('route', 'path'))
        super().show()
        
    def _side_menu_click(self, option: str) -> None:
        if option == 'New':
            self._new()
        elif option == 'Open':
            self._open()
        elif option == 'Save':
            self._save()
        elif option == 'Save As':
            self._save_as()
        elif option == 'Convert LSS':
            self._convert_lss()

    def _apply(self) -> None:
        self._save()
        self.hide()
        
    def _cancel(self) -> None:
        self.hide()
        
    def _convert_lss(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open LiveSplit File', filter='LiveSplit File (*.lss)')
        
        if not file_path:
            return

        route_instance = translate_lss(file_path)
        self._display_route(route_instance)
        
    def _new(self):
        self._current_path = None
        
        self._splits.clear()
        self._properties.clear()
        
    def _open(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, 'Open Route', 'routes', 'AS64 Route File (*.as64)')
        
        if file_path:
            self._load_route(file_path)
            
    def _save(self) -> None:
        title = self._properties.title()
        initial_star = self._properties.initial_star()
        version = self._properties.version()
        category = self._properties.category()
        timing = self._properties.timing()
        splits = self._splits.get_splits()
        
        route_instance = Route(title=title,
                      splits=splits,
                      initial_star=initial_star,
                      version=version,
                      category=category,
                      logic_plugin=timing
                      )   
        
        # If user is not currently working to a path, prompt for save location
        if not self._current_path:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Route", "routes",
                                                    "AS64 Route File (*.as64)")
            
            if file_path:
                self._current_path = file_path
            else:
                return
        
        # Save route    
        route.save(route_instance, self._current_path)
        
        # Update route path in config
        config.set('route', 'path', self._current_path)
        config.save()

        # Emit
        self.route_changed.emit()
        
    def _save_as(self) -> None:
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Route", "routes",
                                                   "AS64 Route File (*.as64)")
        
        if file_path:
            self._current_path = file_path
        else:
            return
        
        self._save()

    def _load_route(self, route_path: str) -> Route:
        _route = route.load(route_path)
        
        if _route:
            self._display_route(_route)
            
            # Update current path
            self._current_path = route_path
            config.set('route', 'path', self._current_path)
            config.save()
        
        return _route
    
    def _display_route(self, route_instance: Route) -> None:
        # Display route
        self._new()
        self._properties._display_route(route_instance)
        self._splits._display_route(route_instance)
            
    def setup_menu(self) -> None:
        new_pixmap = QPixmap("resources/icons/new_icon_32.png")
        open_pixmap = QPixmap("resources/icons/folder_icon_32.png")
        save_pixmap = QPixmap("resources/icons/save_icon_32.png")
        save_as_pixmap = QPixmap("resources/icons/save_as_icon_32.png")
        convert_pixmap = QPixmap("resources/icons/convert_lss_icon_32.png")
        
        self._side_menu.add_option(new_pixmap, "New")
        self._side_menu.add_option(open_pixmap, "Open")
        self._side_menu.add_option(save_pixmap, "Save")
        self._side_menu.add_option(save_as_pixmap, "Save As")
        self._side_menu.add_option(convert_pixmap, "Convert LSS")
        
        
class RoutePropertiesWidget(QFrame):
    DEFAULT_CATEGORIES = ['0 Star', '1 Star', '16 Star', '70 Star', '120 Star']
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Properties
        self.setMinimumHeight(150)
        self.setStyleSheet("QFrame { background: palette(Alternate-Base); border-radius: 5px; }")
        
        # Layout
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setVerticalSpacing(10)
        self._layout.setHorizontalSpacing(8)

        # Widgets
        self._title_lb = QLabel("Title:", self)
        self._category_lb = QLabel("Category:", self)
        self._timing_lb = QLabel("Timing:", self)
        self._version_lb = QLabel("Version:", self)
        self._star_lb = QLabel("Initial Star:", self)

        self._title_le = QLineEdit(self)
        self._category_combo = QComboBox(self)
        self._timing_combo = QComboBox(self)
        self._version_combo = QComboBox(self)
        self._star_sb = QSpinBox(self)
        
        self.initialize()
        
    def initialize(self):
        # Configure Widgets
        self._title_lb.setFixedHeight(27)
        self._category_lb.setFixedHeight(27)
        self._timing_lb.setFixedHeight(27)
        self._timing_lb.setContentsMargins(10, 0, 0, 0)
        self._version_lb.setFixedHeight(27)
        self._star_lb.setFixedHeight(27)
        
        self._title_le.setFixedHeight(27)
        self._title_le.setStyleSheet("QLineEdit { background-color: palette(Window); border-radius: 5px; padding-left: 10px}")
        
        self._star_sb.setStyleSheet(global_style_sheet)
        self._star_sb.setObjectName('NoArrowSpinBox')
        self._star_sb.setFixedSize(50, 30)
        self._star_sb.setRange(0, 120)
        self._star_sb.setRange(0, 120)
        
        self._category_combo.setView(QListView())
        self._category_combo.setFixedHeight(27)
        self._category_combo.setObjectName("WindowColourCombo")
        self._category_combo.setEditable(True)
        # self._category_combo.lineEdit().setStyleSheet("background-color: transparent")
        self._category_combo.setStyleSheet(global_style_sheet)
        self._category_combo.addItems([category for category in self.DEFAULT_CATEGORIES])
        
        self._timing_combo.setView(QListView())
        self._timing_combo.setFixedHeight(27)
        self._timing_combo.setFixedWidth(150)
        self._timing_combo.setObjectName("WindowColourCombo")
        self._timing_combo.setStyleSheet(global_style_sheet)
        self._timing_combo.addItem('RTA')
        
        self._version_combo.setView(QListView())
        self._version_combo.setFixedHeight(27)
        self._version_combo.setFixedWidth(150)
        self._version_combo.setObjectName("WindowColourCombo")
        self._version_combo.setStyleSheet(global_style_sheet)
        self._version_combo.addItems([version.value for version in Version])
               
        # Populate Layout
        self._layout.addWidget(self._title_lb, 0, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._title_le, 0, 1, 1, 4)

        self._layout.addWidget(self._category_lb, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._category_combo, 1, 1, 1, 4)
        
        self._layout.addWidget(self._version_lb, 2, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._version_combo, 2, 1)

        self._layout.addWidget(self._timing_lb, 2, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._timing_combo, 2, 3)

        self._layout.addWidget(self._star_lb, 3, 0, alignment=Qt.AlignmentFlag.AlignLeft)
        self._layout.addWidget(self._star_sb, 3, 1)

        spacer = QSpacerItem(5, 5, QSizePolicy.Expanding, QSizePolicy.Minimum)
        self._layout.addItem(spacer, 2, 4)

    def title(self) -> str:
        return self._title_le.text()
    
    def category(self) -> str:
        return self._category_combo.currentText()
    
    def timing(self) -> str:
        return self._timing_combo.currentText()
    
    def version(self) -> Version:
        return Version(self._version_combo.currentText())
    
    def initial_star(self) -> int:
        return self._star_sb.value()

    def clear(self) -> None:
        self._title_le.setText('')
        self._category_combo.setCurrentText('')
        self._timing_combo.setCurrentIndex(0)
        self._version_combo.setCurrentIndex(0)
        self._star_sb.clear()

    def _display_route(self, route_instance: Route) -> None:
        if not route_instance:
            return
        
        # Global route properties
        self._title_le.setText(route_instance.title)
        self._star_sb.setValue(route_instance.initial_star)
        self._category_combo.lineEdit().setText(route_instance.category)
        
        self._version_combo.setCurrentIndex(self._version_combo.findText(route_instance.version.value))
           
      
class SplitWidget(QWidget):
    def __init__(self, parent=None, list_item: QListWidgetItem=None):
        super().__init__(parent)
        
        self.setObjectName("SplitWidget")
        
        # self.setStyleSheet("QFrame#SplitWidget { background: palette(Base); border-radius: 10px; }")
        self.setMinimumHeight(48)
        self.setStyleSheet(global_style_sheet)
        
        self._list_item = list_item
        
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._top_layout = QHBoxLayout()
        self._top_layout.setContentsMargins(15, 0, 15, 0)
        self._top_layout.setSpacing(10)
        
        # Widgets
        self._title_lb = QLabel("Title:", self)
        self._type_lb = QLabel("Type:", self)
        self._star_lb = QLabel("Star:", self)
        
        self._title_le = QLineEdit(self)
        self._type_combo = QComboBox(self)
        self._star_sb = QSpinBox(self)
        
        self._detail_widget = None
        
        # Customize Widgets
        self._title_lb.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self._title_lb.setObjectName("BaseColourLabel")
        # self.setStyleSheet("QLabel { background-color: palette(Base);}")
        
        self._title_le.setMinimumWidth(175)
        self._title_le.setFixedHeight(30)
        self._title_le.setStyleSheet("QLineEdit { background-color: palette(Window); border-radius: 5px; padding-left: 10px}")
        self._type_lb.setObjectName("BaseColourLabel")
        
        self._type_combo.setObjectName("WindowColourCombo")
        self._type_combo.setView(QListView())
        self._type_combo.setFixedWidth(150)
        self._type_combo.setFixedHeight(30)
        self._type_combo.addItems([split_type.value for split_type in SplitType])
        self._type_combo.currentTextChanged.connect(self._on_type_change)
        
        self._star_lb.setObjectName("BaseColourLabel")
        
        self._star_sb.setObjectName('NoArrowSpinBox')
        self._star_sb.setFixedSize(50, 30)
        self._star_sb.setRange(0, 120)

        self._top_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        # Populate Layouts
        self._top_layout.addWidget(self._title_lb)
        self._top_layout.addWidget(self._title_le, stretch=1)
        
        spacer = QSpacerItem(20, 5)
        self._top_layout.addSpacerItem(spacer)
        self._top_layout.addWidget(self._type_lb)
        self._top_layout.addWidget(self._type_combo)
        
        spacer = QSpacerItem(20, 5)
        self._top_layout.addSpacerItem(spacer)
        self._top_layout.addWidget(self._star_lb)
        self._top_layout.addWidget(self._star_sb)
        
        # self._top_layout.addStretch(1)
        
        self._layout.addLayout(self._top_layout)
        
        self._list_item.setSizeHint(QSize(100, 50))
 
    def title(self) -> str:
        return self._title_le.text()
    
    def star(self) -> int:
        if self._type_combo.currentText() == SplitType.STAR.value:
            return self._star_sb.value()

        return None
    
    def split_type(self) -> SplitType:
        return SplitType(self._type_combo.currentText())
        
    def detail_widget_values(self) -> dict:
        if self._detail_widget:
            return self._detail_widget.get_values()

        return None
        
    def sizeHint(self) -> QSize:
        return QSize(100, 50)        
        
    def set_detail_widget(self, widget: Any=None) -> None:
        if self._detail_widget:
            self._layout.removeWidget(self._detail_widget)
            
        extra_size = QSize(0, 0)
            
        if widget:
            self._layout.addWidget(widget)
            extra_size = widget.sizeHint()
            
        self._detail_widget = widget
        self._list_item.setSizeHint(self.sizeHint() + extra_size)
        
    def set_split(self, split: Split) -> None:
        self._title_le.setText(split.title)
        self._type_combo.setCurrentIndex(self._type_combo.findText(split.split_type.value))
        
        if split.star_count is not None:
            self._star_sb.setValue(split.star_count)
            
        if self._detail_widget:
            self._detail_widget.set_split(split)
        
    def _on_type_change(self, text: str) -> None:
        if text == 'Custom':
            self.set_detail_widget(CustomDetailWidget(self))
        else:
            self.set_detail_widget(None)
            
        if text != 'Star':
            self._star_lb.hide()
            self._star_sb.hide()
            self._top_layout.addSpacerItem(QSpacerItem(101, 10, QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Minimum))
        else:
            self._top_layout.takeAt(self._top_layout.count() - 1)
            self._star_lb.show()
            self._star_sb.show()  
        
        
class RouteSplitsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumHeight(400)
        self.setStyleSheet("""
                            QFrame
                            {
                                background: palette(Alternate-Base);
                                border-radius: 5px;
                            }
                            
                            QScrollBar::vertical
                            {
                                width: 12px;
                                background: rgba(0, 0, 0, 0);
                            }
                            
                            QScrollBar::handle:vertical
                            {
                                background: palette(Window);
                                border-radius: 3px;
                                margin-left: 5px;
                                margin-left: 5px;
                            }
                            
                            QScrollBar::sub-line:vertical
                            {
                                background: none;
                            }
                            
                            QScrollBar::add-line:vertical
                            {
                                background: none;
                            } 
                            """)
        
        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        
        # Widgets
        self._list = QListWidget(self)
        self._list.setDragDropMode(QAbstractItemView.DragDrop)
        self._list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._list.setStyleSheet("""
                                 QListView
                                 {
                                    outline: none;
                                 }
                                 QListView::item
                                 {
                                    background: palette(Base);
                                    border-radius: 5px;
                                 }
                                 QListView::item::selected
                                 {
                                    border-style: solid;
                                    border-width: 3px;
                                    border-color: palette(Highlight);
                                    
                                 }
                                 
                                 QScrollBar::vertical
                                 {
                                    width: 45px;
                                 }
                                 
                                 QScrollBar::handle:vertical
                                 {
                                    min-height:50px;
                                 }
                                 """)
        self._list.setSpacing(4)
        
        # Populate layout
        self._layout.addWidget(self._list)
        
    def clear(self) -> None:
        self._list.clear()
        
    def _display_route(self, route_instance: Route) -> None:
        if not route_instance:
            return
        
        for split in route_instance.splits:
            split_widget = self.add_split()
            split_widget.set_split(split)
            
    def get_splits(self) -> List[Split]:
        splits = []
        
        for split_index in range(self._list.count()):
            item = self._list.item(split_index)
            widget: SplitWidget = self._list.itemWidget(item)
            
            values = widget.detail_widget_values()
            
            title = widget.title()
            
            try:
                star_count = values['star_count']
            except (KeyError, TypeError):
                star_count = widget.star()
                
            try:    
                fadeout = values['fadeout']
            except (KeyError, TypeError):
                fadeout = None
            
            try:    
                fadein = values['fadein']
            except (KeyError, TypeError):
                fadein = None
                
            try:    
                x_cam = values['x_cam']
            except (KeyError, TypeError):
                x_cam = None
                
            split_type = widget.split_type()
                
            splits.append(Split(title=title,
                                star_count=star_count,
                                fadeout=fadeout,
                                fadein=fadein,
                                xcam=x_cam,
                                split_type=split_type))
            
        return splits

    def add_split(self) -> SplitWidget:
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 50))
        
        split_widget = SplitWidget(self._list, item)
            
        self._list.addItem(item)
        self._list.setItemWidget(item, split_widget)
        
        return split_widget
        
    def insert_split(self) -> None:
        item = QListWidgetItem()
        # item.setSizeHint(QSize(100, 50))
        
        split_widget = SplitWidget(self._list, item)
            
        try:
            selected_index = self._list.selectedIndexes()[0].row()
        except IndexError:
            selected_index = self._list.count()
            
        self._list.insertItem(selected_index + 1 , item)
        self._list.setItemWidget(item, split_widget)
        
    def remove_split(self) -> None:
        selected_items = self._list.selectedItems()
                
        for item in selected_items:
            self._list.takeItem(self._list.indexFromItem(item).row())
    
    
class RouteButtonBar(QFrame):
    add = pyqtSignal()
    insert = pyqtSignal()
    remove = pyqtSignal()
    apply = pyqtSignal()
    cancel = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.setMinimumHeight(50)
        
        self.setStyleSheet("""
                            QFrame
                            {
                                border-radius: 5px;
                            }
                            
                            QPushButton
                            {
                                height: 30px;
                                height: 30px;
                                min-width: 90px;
                                border-radius: 5px;
                                background-color: palette(Alternate-Base);
                            }
                            
                            QPushButton::hover
                            {
                                background-color: #474b53;
                            }
                            
                            QPushButton::pressed
                            {
                                background-color: palette(Dark);
                            }
                           """)
        
        # Layout
        self._layout = QHBoxLayout(self)
        
        # Widgets
        self._add_button = QPushButton("Add", self)
        self._insert_button = QPushButton("Insert", self)
        self._remove_button = QPushButton("Remove", self)
        self._apply_button = QPushButton("Apply", self)
        self._cancel_button = QPushButton("Cancel", self)
        
        # Populate layout
        self._layout.addWidget(self._add_button)
        self._layout.addWidget(self._insert_button)
        self._layout.addWidget(self._remove_button)
        self._layout.addStretch(1)
        self._layout.addWidget(self._cancel_button)
        self._layout.addWidget(self._apply_button)
        
        # Connect Signals
        self._add_button.clicked.connect(self.add.emit)
        self._insert_button.clicked.connect(self.insert.emit)
        self._remove_button.clicked.connect(self.remove.emit)
        self._apply_button.clicked.connect(self.apply.emit)
        self._cancel_button.clicked.connect(self.cancel.emit)


class CustomDetailWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Layout
        self._layout = QGridLayout(self)
        self._layout.setContentsMargins(15, 0, 15, 0)
        self._layout.setHorizontalSpacing(10)
        self._layout.setVerticalSpacing(0)
        self.setStyleSheet(global_style_sheet)

        # Widgets
        self._star_cb = QCheckBox(self)
        self._fadeout_cb = QCheckBox(self)
        self._fadein_cb = QCheckBox(self)
        self._x_cam_cb = QCheckBox(self)

        self._star_lb = QLabel('Star:', self)
        self._fadeout_lb = QLabel('Fadeout:', self)
        self._fadein_lb = QLabel('Fade-in:', self)
        self._x_cam_lb = QLabel('X-Cam:', self)
        
        self._star_sb = QSpinBox(self)
        self._fadeout_sb = QSpinBox(self)
        self._fadein_sb = QSpinBox(self)
        self._x_cam_sb = QSpinBox(self)
        
        # Configure Widgets
        self._star_lb.setObjectName("BaseColourLabel")
        self._star_lb.setFixedHeight(30)
        self._fadeout_lb.setObjectName("BaseColourLabel")
        self._fadeout_lb.setFixedHeight(30)

        self._fadein_lb.setObjectName("BaseColourLabel")
        self._fadein_lb.setFixedHeight(30)
        self._x_cam_lb.setObjectName("BaseColourLabel")
        self._x_cam_lb.setFixedHeight(30)
        
        self._star_sb.setObjectName('NoArrowSpinBox')
        self._star_sb.setFixedSize(50, 30)
        self._star_sb.setRange(0, 120)
        
        self._fadeout_sb.setObjectName('NoArrowSpinBox')
        self._fadeout_sb.setFixedSize(50, 30)
        self._fadeout_sb.setMinimum(0)
        
        self._fadein_sb.setObjectName('NoArrowSpinBox')
        self._fadein_sb.setFixedSize(50, 30)
        self._fadein_sb.setMinimum(0)
        
        self._x_cam_sb.setObjectName('NoArrowSpinBox')
        self._x_cam_sb.setFixedSize(50, 30)
        self._x_cam_sb.setMinimum(0)
        
        # Populate layout
        self._layout.addWidget(self._star_cb, 0, 0, 1, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self._fadeout_cb, 0, 2,1, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self._fadein_cb, 0, 4,1, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self._x_cam_cb, 0, 6,1, 2, alignment=Qt.AlignmentFlag.AlignHCenter)
        
        self._layout.addWidget(self._star_lb, 1, 0, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._star_sb, 1, 1, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self._layout.addWidget(self._fadeout_lb, 1, 2, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._fadeout_sb, 1, 3, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self._layout.addWidget(self._fadein_lb, 1, 4, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._fadein_sb, 1, 5, alignment=Qt.AlignmentFlag.AlignLeft)
        
        self._layout.addWidget(self._x_cam_lb, 1, 6, alignment=Qt.AlignmentFlag.AlignRight)
        self._layout.addWidget(self._x_cam_sb, 1, 7, alignment=Qt.AlignmentFlag.AlignLeft)
        
        # Set options to default
        self._set_option_enabled(self._star_cb, self._star_lb, self._star_sb)
        self._set_option_enabled(self._fadeout_cb, self._fadeout_lb, self._fadeout_sb)
        self._set_option_enabled(self._fadein_cb, self._fadein_lb, self._fadein_sb)
        self._set_option_enabled(self._x_cam_cb, self._x_cam_lb, self._x_cam_sb)

        # Signals
        self._star_cb.stateChanged.connect(partial(self._set_option_enabled, self._star_cb, self._star_lb, self._star_sb))
        self._fadeout_cb.stateChanged.connect(partial(self._set_option_enabled, self._fadeout_cb, self._fadeout_lb, self._fadeout_sb))
        self._fadein_cb.stateChanged.connect(partial(self._set_option_enabled, self._fadein_cb, self._fadein_lb, self._fadein_sb))
        self._x_cam_cb.stateChanged.connect(partial(self._set_option_enabled, self._x_cam_cb, self._x_cam_lb, self._x_cam_sb))
        
    def get_values(self) -> dict:
        if self._star_cb.isChecked():
            star_count = self._star_sb.value()
        else:
            star_count = None
            
        if self._fadeout_cb.isChecked():
            fadeout = self._fadeout_sb.value()
        else:
            fadeout = None
            
        if self._fadein_cb.isChecked():
            fadein = self._fadein_sb.value()
        else:
            fadein = None
            
        if self._x_cam_cb.isChecked():
            x_cam = self._x_cam_sb.value()
        else:
            x_cam = None
        
        return {
            'star_count': star_count,
            'fadeout': fadeout,
            'fadein': fadein,
            'x_cam': x_cam
        }
    
    def set_split(self, split: Split) -> None:
        if split.star_count is not None:
            self._star_cb.setChecked(True)
            self._star_sb.setValue(split.star_count)
            
        if split.fadeout is not None:
            self._fadeout_cb.setChecked(True)
            self._fadeout_sb.setValue(split.fadeout)
            
        if split.fadein is not None:
            self._fadein_cb.setChecked(True)
            self._fadein_sb.setValue(split.fadein)
            
        if split.xcam is not None:
            self._x_cam_cb.setChecked(True)
            self._x_cam_sb.setValue(split.xcam)

    def _set_option_enabled(self, checkbox, label, line_edit) -> None:
        disabled = not checkbox.isChecked()
        
        label.setDisabled(disabled)
        line_edit.setDisabled(disabled)
        
        if disabled:
            line_edit.clear()

    def sizeHint(self) -> QSize:
        return QSize(300, 65)
