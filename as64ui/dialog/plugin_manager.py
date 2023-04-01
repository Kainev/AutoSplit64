from PySide6.QtCore import (
    Qt,
    QSize,
)

from PySide6.QtWidgets import (
    QApplication,
    QSizePolicy,
    QWidget,
    QDialog,
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QScrollArea,
    QTabWidget,
    QLabel,
    QLineEdit,
    QPushButton,
)

from PySide6.QtGui import (
    QScreen,
    QFont,
)

from as64 import config

from as64ui.style import global_style_sheet
from as64ui.widgets import HLine


class PluginManager(QDialog):
    def __init__(self, user_plugins, system_plugins, parent=None):
        super().__init__(parent)

        # Attributes
        self.setAttribute(Qt.WA_Moved)
        self.move(QScreen.geometry(QApplication.screens()[0]).center() - self.rect().center())
        self.setWindowTitle("Plugin Manager")
        self.setStyleSheet(global_style_sheet)

        # Layouts
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(20)

        # Widgets
        self._tab_widget = QTabWidget(self)
        self._user_plugins_widget = UserPluginsWidget(self)
        self._system_plugins_widget = SystemPluginsWidget(system_plugins, self)

        #
        # self._tab_widget.setTabBar(ExpandingTabBar())
        self._tab_widget.tabBar().setDocumentMode(True)
        self._tab_widget.tabBar().setExpanding(True)
        self._tab_widget.addTab(self._user_plugins_widget, "User Plugins")
        self._tab_widget.addTab(self._system_plugins_widget, "System Plugins")

        # Populate layout
        self._layout.addWidget(self._tab_widget)
        # self._layout.addWidget(self._user_plugins_widget)
        # self._layout.addWidget(self._system_plugins_widget)

        # Size
        self.setFixedWidth(480)
        self.resize(480, 700)


class UserPluginsWidget(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)

        # Properties
        self.setMinimumHeight(150)

        # Layouts
        self._layout = QVBoxLayout(self)

        # Widgets
        self._initialize()

    def _initialize(self):
        # Layouts
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(20, 20, 20, 20)

        # Widgets

        # Populate layouts


class SystemPluginsWidget(QFrame):
    def __init__(self, system_plugins, parent=None):
        super().__init__(parent)

        # Properties
        self.setMinimumHeight(150)

        # Layouts
        self._layout = QVBoxLayout(self)
        self._scroll_widget_layout = QVBoxLayout()

        # Widgets
        self._scroll_area = QScrollArea(self)
        self._scroll_widget = QWidget(self)
        self._capture = SystemPluginPicker('Capture Plugin', 'capture', system_plugins[config.get('plugins', 'system', 'capture')], self)
        self._fade = SystemPluginPicker('Fade Plugin', 'fade', system_plugins[config.get('plugins', 'system', 'fade')], self)
        self._star = SystemPluginPicker('Star Plugin', 'star', system_plugins[config.get('plugins', 'system', 'star')], self)
        self._xcam = SystemPluginPicker('X-Cam Plugin', 'xcam', system_plugins[config.get('plugins', 'system', 'xcam')], self)
        self._split = SystemPluginPicker('Split Plugin', 'split', system_plugins[config.get('plugins', 'system', 'split')], self)
        self._logic = SystemPluginPicker('Logic Plugin', 'logic', system_plugins[config.get('plugins', 'system', 'logic')], self)

        self._initialize()

    def _initialize(self):
        # Layouts
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._scroll_widget_layout.setContentsMargins(0, 20, 0, 20)
        self._scroll_widget_layout.setSpacing(20)

        # Widgets
        self._scroll_widget.setLayout(self._scroll_widget_layout)
        self._scroll_widget.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self._scroll_widget.setMinimumWidth(458)
        self._scroll_area.setContentsMargins(0, 0, 0, 0)
        self._scroll_area.setViewportMargins(0, 0, 0, 0)
        self._scroll_area.setStyleSheet("""
                                        QScrollBar::vertical
                                        {
                                            width: 18px;
                                            background: palette(base);
                                        }
                                        
                                        QScrollBar::handle:vertical
                                        {
                                            margin-left: 3px;
                                            margin-right: 3px;
                                            background: palette(Window);
                                            border-radius: 3px;
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

        self._capture.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Populate layouts
        self._scroll_widget_layout.addWidget(self._capture)
        self._scroll_widget_layout.addWidget(HLine(self))
        self._scroll_widget_layout.addWidget(self._fade)
        self._scroll_widget_layout.addWidget(HLine(self))
        self._scroll_widget_layout.addWidget(self._star)
        self._scroll_widget_layout.addWidget(HLine(self))
        self._scroll_widget_layout.addWidget(self._xcam)
        self._scroll_widget_layout.addWidget(HLine(self))
        self._scroll_widget_layout.addWidget(self._split)
        self._scroll_widget_layout.addWidget(HLine(self))
        self._scroll_widget_layout.addWidget(self._logic)

        #
        self._scroll_area.setWidget(self._scroll_widget)

        #
        self._layout.addWidget(self._scroll_area, 1)


class SystemPluginPicker(QWidget):
    def __init__(self, title, config_key, plugin, parent=None):
        super().__init__(parent)

        #
        self._config_key = config_key

        # Layout
        self._layout = QVBoxLayout(self)
        self._name_version_layout = QHBoxLayout()
        self._author_browse_layout = QHBoxLayout()

        # Widgets
        self._title_lb = QLabel(title, self)
        self._name_le = TitleLineEdit('Name', plugin.DEFINITION.NAME, self)
        self._version_le = TitleLineEdit('Version', plugin.DEFINITION.VERSION, self)
        self._author_le = TitleLineEdit('Author', plugin.DEFINITION.AUTHOR, self)
        self._browse_btn = QPushButton("Browse", self)

        self._initialize()

    def _initialize(self):
        # Style
        self.setStyleSheet("""
                            QPushButton
                            {
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
                            
                            QLineEdit
                            {
                                border-radius: 5px;
                            }
                            """
                           )

        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)

        # Layouts
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(20, 0, 20, 0)
        self._author_browse_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        # Widgets
        self._title_lb.setFont(title_font)
        self._version_le.setFixedWidth(90)
        self._browse_btn.setFixedWidth(90)
        self._author_le.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)

        # Populate layouts
        self._layout.addWidget(self._title_lb)
        self._layout.addLayout(self._name_version_layout, 1)
        self._layout.addLayout(self._author_browse_layout, 1)

        self._name_version_layout.addWidget(self._name_le)
        self._name_version_layout.addWidget(self._version_le)

        self._author_browse_layout.addWidget(self._author_le, 1)
        self._author_browse_layout.addWidget(self._browse_btn, 0, Qt.AlignmentFlag.AlignBottom)

        #
        self._browse_btn.clicked.connect(self._browse)

    def _browse(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Plugin', 'plugins', '(*.py *.pyd)')

        if file_path:
            print(file_path)


class TitleLineEdit(QWidget):
    def __init__(self, title, text, parent=None):
        super().__init__(parent)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)

        self._title = QLabel(title, self)
        self._line_edit = QLineEdit(self)
        self._line_edit.setReadOnly(True)
        self._line_edit.setTextMargins(5, 0, 5, 0)
        self._line_edit.setMinimumHeight(30)
        self._line_edit.setText(text)

        self._layout.addWidget(self._title)
        self._layout.addWidget(self._line_edit)

    def setText(self, text):
        self._line_edit.setText(text)
