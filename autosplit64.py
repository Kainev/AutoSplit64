import sys
from threading import Thread
from time import time

from PyQt5.QtCore import (
    Qt,
    QObject
)

from PyQt5.QtWidgets import (
    QApplication,
    QWidget
)

from as64 import AS64, config, constants
from as64.plugin import import_plugins, initialize_plugins
from as64ui.application import Application


class AutoSplit64(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._as64: AS64 = None
        self._user_plugins: list = []
        self._system_plugin_classes: dict = {}
        
        self._app: Application = Application(self)

        t = time()
        # self.load_plugins()
        f = time()
        
        print("F:", f - t)
        
        

        self.temporary_command_input()

        
    def temporary_command_input(self):
        while True:
            user_input = input()

            if user_input.lower() == 'start':
                try:
                    self._as64.stop()
                except:
                    pass

                Thread(target=self.start).start()
            elif user_input.lower() == 'quit':
                try:
                    self._as64.stop()
                except:
                    pass

                sys.exit(1)


    def load_plugins(self) -> None:
        # Initialize user plugins
        user_plugin_classes = import_plugins(constants.USER_PLUGIN_DIR)
        self._user_plugins = initialize_plugins(user_plugin_classes)

        # Update config for user plugins
        config.set('plugins', 'user', [cls.__module__.split('.')[-1] for cls in user_plugin_classes])
        config.save()

        system_plugin_classes = import_plugins(constants.SYSTEM_PLUGIN_DIR)
        self._system_plugin_classes = {cls.__module__.split('.')[-1]: cls for cls in system_plugin_classes}

        # TODO: Check if all system plugins are present, give user an warning if not (?)

    def start(self):
        self._as64 = AS64(system_plugins=self._system_plugin_classes, user_plugins=self._user_plugins)
        self._as64.run()

    
if __name__ == "__main__":    
    # 
    sys._excepthook = sys.excepthook

    def exception_hook(exctype, value, tracebook):
        sys._excepthook(exctype, value, tracebook)
        sys.exit(1)

    sys.excepthook = exception_hook

    # Load AS64 config file
    config.load()

    # Qt Application
    import os
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('Fusion')
    qt_app.setAttribute(Qt.AA_EnableHighDpiScaling)

    qt_app.setApplicationName('AutoSplit 64')
    qt_app.setOrganizationName('AutoSplit 64')
    qt_app.setOrganizationDomain('https://autosplit64.com')
    
    # AutoSplit64 Application
    _main = AutoSplit64(qt_app)

    # Exit
    sys.exit(qt_app.exec_())
