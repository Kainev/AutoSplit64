from as64ui.dialog.base_window import BaseWindow



from PyQt5.QtGui import (
    QPixmap
)


class MainWindow(BaseWindow):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Autosplit64")
        
        self.resize(380, 560)
        
        self.setup_menu()
        
        self.show()
        
    def setup_menu(self) -> None:
        route_pixmap = QPixmap("resources/icons/route_icon_32.png")
        capture_pixamp = QPixmap("resources/icons/capture_icon_32.png")
        calibration_pixmap = QPixmap("resources/icons/calibration_icon_32.png")
        plugins_pixmap = QPixmap("resources/icons/plugins_icon_32.png")
        settings_pixmap = QPixmap("resources/icons/settings_icon_32.png")
        
        self.add_menu_option(route_pixmap, "Route")
        self.add_menu_option(capture_pixamp, "Capture")
        self.add_menu_option(calibration_pixmap, "Calibration")
        self.add_menu_option(plugins_pixmap, "Plugins")
        self.add_menu_option(settings_pixmap, "Settings")