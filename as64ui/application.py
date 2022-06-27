from PyQt5.QtCore import (
    Qt,
    QObject,
    pyqtSignal,
    QUrl
)

from PyQt5.QtWidgets import (
    QApplication
)

from PyQt5.QtGui import (
    QPalette
)

from as64.api import config
from as64ui.main_window import MainWindow
from as64ui.colours import Colours
from as64ui.utils import apply_gradient


class Application(QObject):
    def __init__(self, parent):
        super().__init__(parent)
        
        self._window = MainWindow()
        
        self._dialogs = {
            
        }
        
        # Load Theme/Colours
        self.load_theme(config.get("appearance", "theme"))
        
        
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

        apply_gradient(self._window, Colours.app_primary, Colours.app_secondary)

        return True