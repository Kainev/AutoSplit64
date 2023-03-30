from PyQt5.QtCore import QSize, Qt

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
    QGridLayout
)

from PyQt5.QtGui import (
    QPalette,
    QPixmap,
    QFont
)


class SplashScreen(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Window
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        #
        self.setFixedSize(500, 240)
        
        # Layouts
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        
        # Widgets
        self._frame = QFrame(self)
        
        self._icon_lb = QLabel(self._frame)
        self._as64_lb = QLabel('AutoSplit64', self._frame)
        
        self._by_synozure_lb = QLabel('By Synozure', self._frame)
        
        self._version_lb = QLabel('0.9.0', self._frame)
        self._status_lb = QLabel('Loading plugins..', self._frame)
        
        self.initialize()

    def initialize(self) -> None:
        # Configure Widgets
        self._frame.setStyleSheet('background-color: palette(Window); border-radius: 10px')
        
        self._icon_lb.setPixmap(QPixmap('resources/icons/logo_icon_128.png'))
        self._icon_lb.move(42, 19)
        
        title_font = QFont()
        title_font.setPointSize(28)
        title_font.setLetterSpacing(QFont.PercentageSpacing, 125)
        
        subtitle_font = QFont()
        subtitle_font.setPointSize(12)
        subtitle_font.setLetterSpacing(QFont.PercentageSpacing, 125)
        
        self._as64_lb.setFont(title_font)
        self._as64_lb.move(200, 74)
        
        self._by_synozure_lb.setFont(subtitle_font)
        self._by_synozure_lb.move(320, 117)
        
        self._version_lb.setFont(subtitle_font)
        self._version_lb.move(23, 205)
        
        self._status_lb.setFont(subtitle_font)
        self._status_lb.move(333, 205)
        
        # Populate Layouts
        self._layout.addWidget(self._frame)
        
        