from functools import partial

from PyQt5.QtCore import (
    Qt,
    pyqtSignal,
    QRectF,
    QRect
)

from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QAbstractButton,
    QSpacerItem,
    QSizePolicy,
    QApplication
)

from PyQt5.QtGui import (
    QPainter,
    QPainterPath,
    QColor,
    QPalette,
    QRegion
)



class SideMenu(QFrame):
    menu_click = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Properties
        self.setFixedSize(100, 480)
        self.setStyleSheet("QFrame { background: #202225; border-top-right-radius: 10px }" )

        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)

        self._menu_layout = QVBoxLayout(self)

        self._menu_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._menu_layout.setContentsMargins(0, 0, 0, 0)
        self._menu_layout.setSpacing(0)

        # Widgets
        self._button = QPushButton(self)
        self._button.setStyleSheet("background: #26752e; border-top-right-radius: 0px")
        self._button.setFixedSize(100, 30)

        # Populate layout
        self.setLayout(self._layout)

        self._layout.addLayout(self._menu_layout)
        self._layout.addWidget(self._button, alignment=Qt.AlignmentFlag.AlignBottom)

        #
        self._menu_options = {}

    def add_option(self, pixmap, text):
        menu_button = MenuButton(self, pixmap, text)
        
        if not self._menu_options:
            menu_button.is_first_item = True
        
        menu_button.clicked.connect(partial(self.menu_click.emit, text))

        menu_button.setMinimumHeight(90)

        self._menu_layout.addWidget(menu_button)
        self._menu_options[text] = menu_button
        
        
class MenuButton(QAbstractButton):
    def __init__(self, parent, pixmap, text, is_first_item=False):
        super().__init__(parent=parent)
        
        self.is_first_item = is_first_item

        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._layout.setSpacing(10)

        self._icon = QLabel()
        self._icon.setPixmap(pixmap)
        self._icon.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._label = QLabel(text)
        self._label.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self._layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        self._layout.addWidget(self._icon, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self._label, alignment=Qt.AlignmentFlag.AlignHCenter)
        self._layout.addSpacerItem(QSpacerItem(0, 0, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def enterEvent(self, event):
        self.update()

    def paintEvent(self, event):
        should_paint = False
        
        if self.isDown():
            should_paint = True
            colour = QColor(0, 0, 0, 25)
        elif self.underMouse():
            should_paint = True
            colour = QColor(QApplication.palette().color(QPalette.Highlight))
            colour.setAlpha(100)
            
            
        if should_paint:
            painter = QPainter()

            painter.begin(self)
            painter.setRenderHint(QPainter.Antialiasing)
            
            event_rect: QRect = event.rect()
                        
            if not self.is_first_item:
                painter.fillRect(event_rect, colour)
            else:
                # Paint straight-edged corners
                painter.fillRect(QRectF(event_rect.x(), event_rect.y(), 10, event_rect.height()), colour)
                painter.fillRect(QRectF(event_rect.x() + 10, event_rect.height() - 10, event_rect.width() - 10, 10), colour)
                
                # Paint rounded top-right corner
                path = QPainterPath()
                path.addRoundedRect(QRectF(event_rect), 10, 10)
                painter.setClipRegion(QRegion(event_rect.x() + 10, event_rect.y(), event_rect.width() - 10, event_rect.height() - 10))
                painter.fillPath(path, colour)
