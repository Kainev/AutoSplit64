import sys
from threading import Thread

from PyQt5.QtCore import (
    QObject
)

from PyQt5.QtWidgets import (
    QApplication
)

from as64 import AS64, config
from as64.plugin import import_plugins, initialize_plugins


class AutoSplit64(QObject):
    def __init__(self, parent=None):
        super().__init__(parent=parent)

        self._as64: AS64 = None
        self._user_plugins: list = []
        self._system_plugins: dict = {}

        self.load_plugins()

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
        user_plugin_dir = config.get('advanced', 'user_plugin_dir')

        plugin_classes = import_plugins(user_plugin_dir)
        self._user_plugins = initialize_plugins(plugin_classes)
        

    def start(self):
        self._as64 = AS64()
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
    qt_app = QApplication(sys.argv)
    qt_app.setStyle('Fusion')

    qt_app.setApplicationName('AutoSplit 64')
    qt_app.setOrganizationName('AutoSplit 64')
    qt_app.setOrganizationDomain('https://autosplit64.com')

    # AutoSplit64 Application
    _main = AutoSplit64(qt_app)

    # Exit
    sys.exit(qt_app.exec_())
