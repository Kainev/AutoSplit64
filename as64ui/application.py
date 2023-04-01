from mimetypes import init

from PySide6.QtCore import (
    Qt,
    QObject,
    QUrl,
    Signal
)


from PySide6.QtWidgets import (
    QApplication
)

from PySide6.QtGui import (
    QPalette
)

from as64.api import config
from as64ui.dialog import RouteEditor, PluginManager, SplashScreen
from as64ui.main_window import MainWindow
from as64ui.colours import Colours
from as64ui.utils import apply_gradient


class Application(QObject):
    start = Signal()
    exit = Signal()

    def __init__(self, user_plugins, system_plugins, parent):
        super().__init__(parent)

        #
        self._user_plugins = user_plugins
        self._system_plugins = system_plugins

        # Load Theme/Colours
        self.load_theme(config.get("appearance", "theme"))
        
        # Splash screen
        self._splash_screen = SplashScreen()     
         
        # Main window and dialogs
        self._window = MainWindow()
        
        self._dialogs = {}
        
        # Connect signals
        self._window.openDialog.connect(self.open_dialog)
        self._window.start.connect(self.start.emit)

    def on_plugins_loaded(self, user_plugins, system_plugins):
        print(user_plugins, system_plugins)
        self._dialogs = {
            "Route": RouteEditor(),
            "Plugins": PluginManager(user_plugins, system_plugins),
        }

        self._dialogs["Route"].route_changed.connect(self._window.update_route_display)

    def on_splitter_update(self, status):
        self._window.set_selected_split(status.current_split_index)
        
    def open_dialog(self, dialog):
        self._dialogs[dialog].show()
        
    def show_window(self) -> None:
        self._splash_screen.hide()
        self._window.show()
        
    def show_splash_screen(self) -> None:
        self._window.hide()
        self._splash_screen.show()
        
    def set_started(self, started: bool) -> None:
        self._window.set_started(started)
                
    def load_theme(self, theme):
        """
        Apply colours defined in theme to applications palette

        :param theme:
        :return: Boolean
        """
        success = Colours.load_theme_colours(theme)

        if not success:
            return False

        palette = QPalette()
        palette.setColor(QPalette.Window, Colours.window)
        palette.setColor(QPalette.WindowText, Colours.text)
        palette.setColor(QPalette.Link, Colours.link)
        palette.setColor(QPalette.Base, Colours.base)
        palette.setColor(QPalette.Disabled, QPalette.Base, Colours.base_disabled)
        palette.setColor(QPalette.AlternateBase, Colours.alternate_base)
        palette.setColor(QPalette.ToolTipBase, Colours.tooltip)
        palette.setColor(QPalette.ToolTipText, Colours.tooltip_text)
        palette.setColor(QPalette.Text, Colours.text)
        palette.setColor(QPalette.Button, Colours.button_active)
        palette.setColor(QPalette.Disabled, QPalette.Button, Colours.button_disabled)
        palette.setColor(QPalette.ButtonText, Colours.button_text)
        palette.setColor(QPalette.BrightText, Colours.bright_text)
        palette.setColor(QPalette.Highlight, Colours.highlight)
        palette.setColor(QPalette.HighlightedText, Colours.highlight_text)
        palette.setColor(QPalette.Light, Colours.light)
        palette.setColor(QPalette.Dark, Colours.dark)

        QApplication.instance().setPalette(palette)

        # apply_gradient(self._window, Colours.app_primary, Colours.app_secondary)

        return True
