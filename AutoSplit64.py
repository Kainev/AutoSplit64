import sys
from threading import Thread
import os
import logging
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 0=all, 1=info, 2=warnings, 3=errors
logging.getLogger('tensorflow').setLevel(logging.ERROR)

# Filter out TensorFlow deprecation warnings
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

from PyQt6 import QtCore, QtWidgets, QtGui

from as64gui.app import App

import as64core
from as64core.processing import register_process, insert_global_hook, insert_global_processor_hook, ProcessorGenerator
from as64core.route_loader import load

from as64processes.standard import *
from as64processes.xcam import *
from as64processes.ddd import *
from as64processes.final import *


class AutoSplit64(QtCore.QObject):
    error = QtCore.pyqtSignal(str)
    update_found = QtCore.pyqtSignal(dict)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Initialize GUI
        self.app = App()

        # Connections
        self.app.start.connect(lambda: Thread(target=self.start).start())
        self.app.stop.connect(self.stop)
        self.app.destroyed.connect(lambda: self.stop())
        self.error.connect(self.app.display_error_message)

    def start(self):
        as64core.init()

        register_process("WAIT", ProcessWait())
        register_process("RUN_START", ProcessRunStart())
        register_process("RUN_START_UP_RTA", ProcessRunStartUpSegment())
        register_process("STAR_COUNT", ProcessStarCount())
        register_process("FADEIN", ProcessFadein())
        register_process("FADEOUT", ProcessFadeout())
        register_process("FADEOUT_NO_STAR", ProcessFadeoutNoStar())
        register_process("FADEOUT_RESET_ONLY", ProcessFadeoutResetOnly())
        register_process("POST_FADEOUT", ProcessPostFadeout())
        register_process("FLASH_CHECK", ProcessFlashCheck())
        register_process("RESET", ProcessReset())
        register_process("DUMMY", ProcessDummy())

        register_process("XCAM", ProcessXCam())
        register_process("XCAM_UP_RTA", ProcessXCamStartUpSegment())

        register_process("FILE_SELECT_SPLIT", ProcessFileSelectSplit())

        register_process("FIND_DDD_PORTAL", ProcessFindDDDPortal())
        register_process("DDD_SPLIT", ProcessDDDEntry())  # TODO: RENAME ProcessDDDEntry to ProcessDDDSplit
        register_process("DDD_SPLIT_X", ProcessDDDEntryX())  # TODO: RENAME ProcessDDDEntryX to ProcessDDDSplitX

        register_process("FINAL_DETECT_ENTRY", ProcessFinalStageEntry())  # TODO: RENAME
        register_process("FINAL_DETECT_SPAWN", ProcessFinalStarSpawn())  # TODO: RENAME
        register_process("FINAL_STAR_SPLIT", ProcessFinalStarGrab())  # TODO: RENAME to FINAL_STAR_SPLIT

        try:
            timing = load(config.get("route", "path")).timing
        except AttributeError:
            timing = None

        if timing == as64core.TIMING_UP_RTA:
            insert_global_hook("RESET", ProcessResetNoStart())
            as64core.start_on_reset = False
            initial_processor = ProcessorGenerator.generate("logic/up_rta/initial_up_rta.processor")
        elif timing == as64core.TIMING_FILE_SELECT:
            insert_global_hook("RESET", ProcessResetNoStart())
            as64core.start_on_reset = False
            initial_processor = ProcessorGenerator.generate("logic/file_select/initial_file_select_start.processor")
        else:
            initial_processor = ProcessorGenerator.generate("logic/standard/initial.processor")

        standard_processor = ProcessorGenerator.generate("logic/standard/star_fade.processor")
        fade_only_processor = ProcessorGenerator.generate("logic/standard/fade_only.processor")
        xcam_processor = ProcessorGenerator.generate("logic/standard/xcam_split.processor")
        ddd_processor = ProcessorGenerator.generate("logic/ddd/ddd.processor")
        mips_x_processor = ProcessorGenerator.generate("logic/ddd/mips_x.processor")
        final_processor = ProcessorGenerator.generate("logic/final/final.processor")

        as64core.register_split_processor(as64core.SPLIT_INITIAL, initial_processor)
        as64core.register_split_processor(as64core.SPLIT_NORMAL, standard_processor)
        as64core.register_split_processor(as64core.SPLIT_FADE_ONLY, fade_only_processor)
        as64core.register_split_processor(as64core.SPLIT_MIPS, ddd_processor)
        as64core.register_split_processor(as64core.SPLIT_MIPS_X, mips_x_processor)
        as64core.register_split_processor(as64core.SPLIT_FINAL, final_processor)
        as64core.register_split_processor(as64core.SPLIT_XCAM, xcam_processor)

        as64core.set_update_listener(self.on_update)
        as64core.set_error_listener(self.on_error)

        as64core.start()

        self.app.set_started(True)

    def stop(self):
        as64core.stop()

    def on_update(self, index, star_count, split_star):
        self.app.update_display(index, star_count, split_star)

    def on_error(self, error):
        self.error.emit(error)
        self.app.set_started(False)

    def exit(self):
        self.stop()
        self.app.close()


if __name__ == "__main__":
    # Create QT Application
    qt_app = QtWidgets.QApplication(sys.argv)

    # Configure QT Application Style
    qt_app.setStyle('Fusion')

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.ColorRole.Window, QtGui.QColor(60, 63, 65))
    palette.setColor(QtGui.QPalette.ColorRole.WindowText, QtGui.QColor(200, 203, 207))
    palette.setColor(QtGui.QPalette.ColorRole.Link, QtGui.QColor(88, 157, 246))
    palette.setColor(QtGui.QPalette.ColorRole.Base, QtGui.QColor(23, 25, 27))
    palette.setColor(QtGui.QPalette.ColorRole.AlternateBase, QtGui.QColor(53, 55, 57))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipBase, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ColorRole.ToolTipText, QtGui.QColor(255, 255, 255))
    palette.setColor(QtGui.QPalette.ColorRole.Text, QtGui.QColor(200, 203, 207))
    palette.setColor(QtGui.QPalette.ColorRole.Button, QtGui.QColor(53, 55, 57))
    palette.setColor(QtGui.QPalette.ColorRole.ButtonText, QtGui.QColor(200, 203, 207))
    palette.setColor(QtGui.QPalette.ColorRole.BrightText, QtGui.QColor(255, 0, 0))
    palette.setColor(QtGui.QPalette.ColorRole.Highlight, QtGui.QColor(75, 110, 175))
    palette.setColor(QtGui.QPalette.ColorRole.HighlightedText, QtGui.QColor(0, 0, 0))
    palette.setColor(QtGui.QPalette.ColorRole.Light, QtGui.QColor(105, 108, 112))
    palette.setColor(QtGui.QPalette.ColorRole.Dark, QtGui.QColor(12, 12, 12))

    qt_app.setPalette(palette)

    # Add font to database
    QtGui.QFontDatabase.addApplicationFont(resource_path("resources/gui/font/TCM_____.ttf"))

    logging.basicConfig(
        level=logging.WARNING,
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        filename=".log",
        filemode='a'
    )

    # Create main application
    autosplit64 = AutoSplit64(qt_app)

    # Exit
    sys.exit(qt_app.exec())
