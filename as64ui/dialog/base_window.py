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
        
        self._left_layout = QVBoxLayout(self)
        self._left_layout.setContentsMargins(0, 0, 0, 0)

        self._right_layout = QVBoxLayout(self)
        self._right_layout.setContentsMargins(0, 0, 0, 0)
        self._right_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        
        # Widgets
        self._side_menu = SideMenu(self)
        
        # Populate Layouts
        self._left_layout.addWidget(self._side_menu, alignment=Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignLeft)
        
        self._layout.addLayout(self._left_layout)
        
    def add_menu_option(self, pixmap: QPixmap, text: str) -> None:
        self._side_menu.add_option(pixmap, text)
        
        
        
        
        
        
    