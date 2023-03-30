from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QDialog,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QLineEdit,
    QAbstractButton,
    QSpacerItem,
    QSizePolicy,
    QGraphicsDropShadowEffect
)

from PyQt5.QtGui import (
    QPainter,
    QColor,
    QPixmap
)
from as64ui.widgets.modern_list import ModernListWidget

from as64ui.widgets.side_menu import SideMenu
from as64ui.style import global_style_sheet

from as64 import route, config


class BaseWindow(QDialog):
    start = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)

        # Load route
        self._route = route.load(config.get('route', 'path'))
        
        #
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setStyleSheet(global_style_sheet)
                 
        # Layouts
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._top_layout = QVBoxLayout()
        self._top_layout.setContentsMargins(20, 20, 20, 20)
        self._top_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self._bottom_layout = QHBoxLayout()
        self._bottom_layout.setContentsMargins(0, 0, 0, 0)
        
        self._bottom_left_layout = QVBoxLayout()
        self._bottom_left_layout.setContentsMargins(0, 0, 0, 0)

        self._bottom_right_layout = QVBoxLayout()
        self._bottom_right_layout.setContentsMargins(20, 0, 20, 10)
        self._bottom_right_layout.setSpacing(10)
        self._bottom_right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Widgets
        self._side_menu = SideMenu(self)
        self._side_menu.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        self._route_title = QLineEdit(self)
        self._route_title.setFixedHeight(38)
        self._route_title.setReadOnly(True)
        self._route_title.setTextMargins(5, 0, 5, 0)
        
        self._splits_list = ModernListWidget(self)
        self._splits_list.set_display_count(11)
        self._splits_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.update_route_display()
        
        self._status_bar = QLineEdit(self)
        self._status_bar.setFixedHeight(38)
        self._status_bar.setReadOnly(True)
        
        # Populate Layouts
        self._bottom_left_layout.addWidget(self._side_menu)
        
        self._bottom_right_layout.addWidget(self._splits_list)
        self._bottom_right_layout.addWidget(self._status_bar)
        
        self._bottom_layout.addLayout(self._bottom_left_layout)
        self._bottom_layout.addLayout(self._bottom_right_layout)

        self._top_layout.addWidget(self._route_title, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._layout.addLayout(self._top_layout)
        self._layout.addLayout(self._bottom_layout)
        
        # Signals
        self._side_menu.menu_click.connect(self.on_menu_click)
        self._side_menu.action_click.connect(self.on_start_clicked)

    def update_route_display(self):
        # Reload route
        self._route = route.load(config.get('route', 'path'))

        # Populate splits list
        self._splits_list.clear()
        for split in self._route.splits:
            self._splits_list.add_item(split.title)

        # Set route title
        self._route_title.setText(self._route.title)

    def set_started(self, started: bool) -> None:
        if started:
            self._side_menu.set_action_state('Stop')
        else:
            self._side_menu.set_action_state('Start')
        
    def on_start_clicked(self) -> None:
        if self._side_menu.current_state() == 'Initializing':
            return
            
        if self._side_menu.current_state() == 'Start':
            self._side_menu.set_action_state('Initializing')
            
        self.start.emit()
        
    def add_menu_option(self, pixmap: QPixmap, text: str) -> None:
        self._side_menu.add_option(pixmap, text)
        
    def on_menu_click(self, clicked):
        raise NotImplementedError
