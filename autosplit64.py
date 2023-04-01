# Disable Future Warnings (TensorFlow has many)
# import warnings
# warnings.filterwarnings("ignore", message=r"Passing", category=FutureWarning)

# Import version number
from _version import __version__

# Python
import sys
from threading import Thread
from time import sleep, time

# PySide6
from PySide6.QtCore import (
    QObject,
    Signal,
)

from PySide6.QtWidgets import (
    QApplication,
)

from PySide6.QtGui import (
    QFontDatabase,
    QFont,
)

# AS64
from as64 import AS64, config, constants, GameStatus
from as64.plugin import import_plugins, initialize_plugins
from as64ui.application import Application


class AutoSplit64(QObject):  
    MINIMUM_SPLASH_SCREEN_TIME = 2

    splitter_update = Signal(GameStatus)
    
    def __init__(self, parent=None) -> None:
        super().__init__(parent=parent)
        
        # Core components
        self._as64: AS64 = None
        self._user_plugins: list = []
        self._system_plugin_classes: dict = {}

        # UI
        self._app: Application = Application(self._user_plugins, self._system_plugin_classes, self)
        
        # Signals
        self._app.start.connect(self.toggle_start)
        self.splitter_update.connect(self._app.on_splitter_update)
        
        # Initialize
        self.initialize()
        
    def initialize(self) -> None:
        # Show splash screen
        self._app.show_splash_screen()
        
        # Process Qt events to allow splash screen to display without being blocked by plugin loading
        # qApp.processEvents()
        QApplication.processEvents()
        
        # Load plugins
        load_start_time = time()
        self.load_plugins()
        self._app.on_plugins_loaded(self._user_plugins, self._system_plugin_classes)
        load_end_time = time()

        # Ensure minimum display time for splash screen
        sleep_time = self.MINIMUM_SPLASH_SCREEN_TIME - (load_end_time - load_start_time)
        sleep(sleep_time if sleep_time > 0 else 0)

        # Display main window
        self._app.show_window()

    def toggle_start(self) -> None:
        if self._as64:
            # Stop the AS64 instance
            self._as64.stop()
            self._as64 = None
            
            # Tell the UI it has stopped
            self._app.set_started(False)
            return
        
        # If no instance, running, call the start function in a new thread
        Thread(target=self.start).start()

    def load_plugins(self) -> None:
        # Initialize user plugins
        user_plugin_classes = import_plugins(constants.USER_PLUGIN_DIR)
        self._user_plugins = initialize_plugins(user_plugin_classes)

        # Update config for user plugins
        config.set('plugins', 'user', [cls.__module__.split('.')[-1] for cls in user_plugin_classes])
        config.save()

        # Import system plugins
        system_plugin_classes = import_plugins(constants.SYSTEM_PLUGIN_DIR)
        # self._system_plugins = initialize_plugins(system_plugin_classes)
        self._system_plugin_classes = {cls.__module__.split('.')[-1]: cls for cls in system_plugin_classes}
        
        # TODO: Check if all system plugins are present, give user a warning if not (?)

    def start(self):
        self._as64 = AS64(system_plugins=self._system_plugin_classes, user_plugins=self._user_plugins, update_callback=self.on_update_callback)
        self._app.set_started(True)
        self._as64.run()

    def on_update_callback(self, status):
        self.splitter_update.emit(status)


if __name__ == "__main__":
    import os
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"

    # Load AS64 config file
    config.load()

    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    app.setApplicationName('AutoSplit64')
    app.setOrganizationName('Kainev')

    # Load font
    font_id = QFontDatabase.addApplicationFont('resources\\fonts\\MyriadProRegular.ttf')
    font_string = QFontDatabase.applicationFontFamilies(font_id)[0]
    font = QFont(font_string, 11)
    font.setHintingPreference(QFont.HintingPreference.PreferNoHinting);
    font.setLetterSpacing(QFont.PercentageSpacing, 110)
    app.setFont(font)

    _main = AutoSplit64(app)

    app.exec()



    
# if __name__ == "__main__":
#     #
#     sys._excepthook = sys.excepthook
#
#     def exception_hook(exctype, value, tracebook):
#         sys._excepthook(exctype, value, tracebook)
#         sys.exit(1)
#
#     sys.excepthook = exception_hook
#
#     # Load AS64 config file
#     config.load()
#
#     # Qt Application
#     import os
#     os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
#
#     qt_app = QApplication(sys.argv)
#     qt_app.setStyle('Fusion')
#     # qt_app.setAttribute(Qt.AA_EnableHighDpiScaling)
#
#     # Load font
#     id = QFontDatabase.addApplicationFont('resources\\fonts\\MyriadProRegular.ttf')
#     font_string = QFontDatabase.applicationFontFamilies(id)[0]
#     font = QFont(font_string, 11)
#     font.setHintingPreference(QFont.HintingPreference.PreferNoHinting);
#     font.setLetterSpacing(QFont.PercentageSpacing, 110)
#     qt_app.setFont(font)
#
#
#
#     qt_app.setApplicationName('AutoSplit 64')
#     qt_app.setOrganizationName('AutoSplit 64')
#     qt_app.setOrganizationDomain('https://autosplit64.com')
#
#     # AutoSplit64 Application
#     _main = AutoSplit64(qt_app)
#
#     # Exit
#     sys.exit(qt_app.exec_())
