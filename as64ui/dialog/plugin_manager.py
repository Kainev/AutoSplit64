import os

from PySide6.QtCore import (
    Qt,
    QSize,
    Signal,
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
    QListWidget,
    QListWidgetItem,
    QTabWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QAbstractItemView
)

from PySide6.QtGui import (
    QScreen,
    QFont,
)

from as64 import config
from as64.plugin import Plugin, import_plugin, initialize_plugin

from as64ui.style import global_style_sheet
from as64ui.widgets import HLine


class PluginManager(QDialog):
    plugin_loaded = Signal(Plugin)

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
        self._user_plugins_widget = UserPluginsWidget(user_plugins, self)
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

        # Connections
        self._user_plugins_widget.plugin_loaded.connect(self.plugin_loaded.emit)


class UserPluginItem(QWidget):
    def __init__(self, _plugin, parent=None, list_item: QListWidgetItem = None):
        super().__init__(parent)

        self._plugin = _plugin

        self.setObjectName("SplitWidget")

        # self.setStyleSheet("QFrame#SplitWidget { background: palette(Base); border-radius: 10px; }")
        self.setMinimumHeight(48)
        self.setStyleSheet(global_style_sheet)

        self._list_item = list_item

        # Layout
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(10, 10, 10, 10)
        self._layout.setSpacing(10)

        # Widgets
        self._plugin_le = QLineEdit(self)
        self._version_le = QLineEdit(self)

        self._version_le.setMaximumWidth(75)
        self._version_le.setReadOnly(True)
        self._plugin_le.setReadOnly(True)

        self._plugin_le.setStyleSheet(
            "QLineEdit { background-color: palette(Window); border-radius: 5px; padding-left: 10px; height: 30px; }")

        self._version_le.setStyleSheet(
            "QLineEdit { background-color: palette(Window); border-radius: 5px; padding-left: 10px; height: 30px; }")

        #
        self._plugin_le.setText(self._plugin.DEFINITION.NAME)
        self._version_le.setText(self._plugin.DEFINITION.VERSION)

        self._layout.addWidget(self._plugin_le)
        self._layout.addWidget(self._version_le)

    def plugin(self):
        return self._plugin

    def sizeHint(self) -> QSize:
        return QSize(100, 50)


class UserPluginsWidget(QFrame):
    plugin_loaded = Signal(Plugin)

    def __init__(self, user_plugins, parent=None):
        super().__init__(parent)

        self._user_plugins = user_plugins

        # Properties
        self.setMinimumHeight(150)

        # Layouts
        self._layout = QVBoxLayout(self)
        self._button_layout = QHBoxLayout()

        # Widgets
        self._list = QListWidget(self)

        self._load_btn = QPushButton("Load", self)
        self._unload_btn = QPushButton("Unload", self)

        self._initialize()

    def _initialize(self):
        # Style
        self.setStyleSheet("""
                            QFrame
                            {
                                background: palette(window);
                            }
                            
                            QScrollBar::vertical
                            {
                                width: 18px;
                                background: palette(base);
                            }
                            
                            QScrollBar::handle:vertical
                            {
                                margin-left: 3px;
                                margin-right: 3px;
                                margin-top: 3px;
                                margin-bottom: 3px;
                                background: palette(Window);
                                border-radius: 5px;
                            }
                            
                            QScrollBar::sub-line:vertical
                            {
                                background: none;
                            }
                            
                            QScrollBar::add-line:vertical
                            {
                                background: none;
                            }
                            
                            QPushButton
                            {
                                height: 40px;
                                min-width: 90px;
                                border-radius: 0px;
                                border-color: palette(base);
                                border-width: 1px;
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

        # Layouts
        self._layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self._button_layout.setContentsMargins(0, 0, 0, 0)
        self._button_layout.setSpacing(0)

        # Widgets
        self._list.setDragDropMode(QAbstractItemView.DragDrop)
        self._list.setDefaultDropAction(Qt.DropAction.MoveAction)
        self._list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self._list.setSpacing(5)
        self._list.setStyleSheet("""
                                    
                                 QListView
                                 {
                                    outline: none;
                                    border: none;
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
                                 """)

        print("USER PLUGINS", self._user_plugins)
        for _plugin in self._user_plugins:
            self.add_plugin(_plugin)

        # Populate layouts
        self._button_layout.addWidget(self._load_btn)
        self._button_layout.addWidget(self._unload_btn)

        self._layout.addWidget(self._list, 1)
        self._layout.addLayout(self._button_layout, 0)

        # Connections
        self._load_btn.clicked.connect(self._browse)
        self._unload_btn.clicked.connect(self._unload_selected_plugin)

    def add_plugin(self, _plugin) -> UserPluginItem:
        item = QListWidgetItem()
        item.setSizeHint(QSize(100, 50))

        plugin_widget = UserPluginItem(_plugin, self._list, item)

        self._list.addItem(item)
        self._list.setItemWidget(item, plugin_widget)

        return plugin_widget

    def _unload_selected_plugin(self):
        item = self._list.selectedItems()[0]
        widget: UserPluginItem = self._list.itemWidget(item)

        self._user_plugins.remove(widget.plugin())

        # Update config for user plugins
        config.set('plugins', 'user', [cls.__module__.split('.')[-1] for cls in self._user_plugins])
        config.save()

        self._list.clear()

        for _plugin in self._user_plugins:
            self.add_plugin(_plugin)


    def _browse(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, 'Select Plugin', 'plugins', '(*.py *.pyd)')

        if file_path:
            _plugin = initialize_plugin(import_plugin(os.path.relpath(file_path)))
            self._user_plugins.append(_plugin)

            # Update config for user plugins
            config.set('plugins', 'user', [cls.__module__.split('.')[-1] for cls in self._user_plugins])
            config.save()

            self.add_plugin(_plugin)

            # self.plugin_loaded.emit(_plugin)


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
                                            margin-top: 3px;
                                            margin-bottom: 3px;
                                            background: palette(Window);
                                            border-radius: 5px;
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
        self._name_le = TitleLineEdit('Plugin', plugin.DEFINITION.NAME, self)
        self._version_le = TitleLineEdit('Version', plugin.DEFINITION.VERSION, self)
        self._author_le = TitleLineEdit('Author', plugin.DEFINITION.AUTHOR, self)
        self._browse_btn = QPushButton("Select", self)

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

    def lineEdit(self):
        return self._line_edit

    def label(self):
        return self._title
