from functools import partial

from PyQt5.QtCore import (
    Qt,
    pyqtSignal
)

from PyQt5.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QAbstractButton,
    QSpacerItem,
    QSizePolicy,
)

from PyQt5.QtGui import (
    QPainter,
    QColor,
)



class SideMenu(QFrame):
    menu_click = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)

        # Properties
        self.setFixedSize(100, 480)
        self.setStyleSheet("QFrame { background: #202225; border-top-right-radius: 20px }" )

        # Layout
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 20, 0, 0)
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
        menu_button.clicked.connect(partial(self.menu_click.emit, text))

        menu_button.setMinimumHeight(90)

        self._menu_layout.addWidget(menu_button)
        self._menu_options[text] = menu_button
        
class MenuButton(QAbstractButton):
    def __init__(self, parent, pixmap, text):
        super().__init__(parent=parent)

        self._layout = QVBoxLayout(self)
        self._layout.setAlignment(Qt.AlignmentFlag.AlignHCenter)

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
        if self.isDown():
            painter = QPainter()
            painter.begin(self)
            color = QColor(0, 0, 0, 25)
            painter.fillRect(event.rect(), color)
        elif self.underMouse():
            painter = QPainter()
            painter.begin(self)
            color = QColor(255, 255, 255, 8)
            painter.fillRect(event.rect(), color)
