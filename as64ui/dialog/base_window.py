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

from as64ui.widgets.side_menu import SideMenu


class BaseWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)  
        
        #
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
                 
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
        self._bottom_right_layout.setContentsMargins(0, 0, 0, 0)
        self._bottom_right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Widgets
        self._side_menu = SideMenu(self)

        self._route_title = QLineEdit(self)
        self._route_title.setFixedHeight(30)
        
        # Populate Layouts
        self._bottom_left_layout.addWidget(self._side_menu, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        
        self._bottom_layout.addLayout(self._bottom_left_layout)
        self._bottom_layout.addLayout(self._bottom_right_layout)

        self._top_layout.addWidget(self._route_title, alignment=Qt.AlignmentFlag.AlignVCenter)

        self._layout.addLayout(self._top_layout)
        self._layout.addLayout(self._bottom_layout)
        
    def add_menu_option(self, pixmap: QPixmap, text: str) -> None:
        self._side_menu.add_option(pixmap, text)
        
        
        
        
        
        
    