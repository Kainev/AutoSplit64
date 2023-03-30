from as64ui.colours import Colours
from as64ui.dialog.base_window import BaseWindow

from PyQt5.QtCore import (
    pyqtSignal
)

from PyQt5.QtGui import (
    QPixmap,
    QColor
)


class MainWindow(BaseWindow):
    openDialog = pyqtSignal(str)
    
    class State(object):
        START = 'Start'
        INITIALIZING = 'Initializing'
        STOP = 'Stop'
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("AutoSplit64")
        
        self.resize(380, 560)
        
        self.setup_menu()

    def set_started(self, started: bool) -> None:
        if started:
            self._side_menu.set_action_state(self.State.STOP)
        else:
            self._side_menu.set_action_state(self.State.START)

    def setup_menu(self) -> None:
        self._side_menu.add_action_state(self.State.START, QColor(38, 117, 46, 255))
        self._side_menu.add_action_state(self.State.INITIALIZING, Colours.highlight, Colours.highlight, Colours.highlight)
        self._side_menu.add_action_state(self.State.STOP, QColor(128, 30, 33))
        self._side_menu.set_action_state(self.State.START)
        
        route_pixmap = QPixmap("resources/icons/route_icon_32.png")
        capture_pixmap = QPixmap("resources/icons/capture_icon_32.png")
        calibration_pixmap = QPixmap("resources/icons/calibration_icon_32.png")
        plugins_pixmap = QPixmap("resources/icons/plugins_icon_32.png")
        settings_pixmap = QPixmap("resources/icons/settings_icon_32.png")
        
        self.add_menu_option(route_pixmap, "Route")
        self.add_menu_option(capture_pixmap, "Capture")
        self.add_menu_option(calibration_pixmap, "Calibration")
        self.add_menu_option(plugins_pixmap, "Plugins")
        self.add_menu_option(settings_pixmap, "Settings")
        
    def on_menu_click(self, clicked):
        self.openDialog.emit(clicked)
