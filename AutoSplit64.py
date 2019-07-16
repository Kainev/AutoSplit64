import sys
from threading import Thread
import logging

from PyQt5 import QtCore, QtWidgets, QtGui

from as64_common.resource_utils import resource_path
from as64_ui.app import App

import as64_core
from as64_core.processing import Processor, Transition
from as64_core.processes import (
    ProcessFadein,
    ProcessFadeout,
    ProcessPostFadeout,
    ProcessFlashCheck,
    ProcessReset,
    ProcessStarCount,
    ProcessRunStart,
    ProcessFinalStageEntry,
    ProcessFinalStarSpawn,
    ProcessFinalStarGrab,
    ProcessFindDDDPortal,
    ProcessDDDEntry,
    ProcessLBLJ,
    ProcessIdle
)


class AutoSplit64(QtCore.QObject):
    error = QtCore.pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent=parent)

        # Initialize GUI
        self.app = App()
        self.app.start.connect(lambda: Thread(target=self.start).start())
        self.app.stop.connect(self.stop)
        self.app.destroyed.connect(self.stop)
        self.error.connect(self.app.display_error_message)

    def start(self):
        as64_core.init()

        # TODO: Generate transitions from file
        main_processor = Processor()
        main_init_processor = Processor()
        main_run_processor = Processor()

        ddd_processor = Processor()
        ddd_portal_processor = Processor()
        ddd_entry_processor = Processor()

        lblj_processor = Processor()

        final_processor = Processor()
        final_entry_processor = Processor()
        final_spawn_processor = Processor()
        final_grab_processor = Processor()
        final_idle_processor = Processor()

        # self.core

        # Regular Processes
        process_fadein = ProcessFadein()
        process_fadeout = ProcessFadeout()
        process_reset = ProcessReset()
        process_run_start = ProcessRunStart()
        process_star_count = ProcessStarCount()
        process_post_fadeout = ProcessPostFadeout()
        process_flash_check = ProcessFlashCheck()
        process_idle = ProcessIdle()

        # DDD Processes
        process_ddd_portal = ProcessFindDDDPortal()
        process_ddd_entry = ProcessDDDEntry()

        # LBLJ Processes
        process_lblj = ProcessLBLJ()

        # final bowser processes
        process_final_stage_entry = ProcessFinalStageEntry()
        process_final_star_spawn = ProcessFinalStarSpawn()
        process_final_star_grab = ProcessFinalStarGrab()

        # Set initial processes
        main_processor.initial_process = main_init_processor
        main_init_processor.initial_process = process_run_start
        main_run_processor.initial_process = process_star_count

        ddd_processor.initial_process = ddd_portal_processor
        ddd_portal_processor.initial_process = process_ddd_portal
        ddd_entry_processor.initial_process = process_ddd_entry

        final_processor.initial_process = final_entry_processor
        final_entry_processor.initial_process = process_final_stage_entry
        final_spawn_processor.initial_process = process_final_star_spawn
        final_grab_processor.initial_process = process_final_star_grab
        final_idle_processor.initial_process = process_idle

        # MAIN PROCESSOR TRANSITIONS
        main_processor.add_transition(Transition(main_init_processor, ProcessRunStart.START, main_run_processor))
        main_processor.add_transition(Transition(main_run_processor, ProcessReset.RESET, main_init_processor))

        #
        # INIT_PROCESSOR TRANSITIONS
        #
        main_init_processor.add_transition(Transition(process_run_start, ProcessRunStart.FADEOUT, process_fadeout))
        main_init_processor.add_transition(Transition(process_fadeout, ProcessFadeout.COMPLETE, process_run_start))
        main_init_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))
        main_init_processor.add_transition(Transition(process_reset, ProcessReset.RESET, process_run_start))

        #
        # RUN_PROCESSOR TRANSITIONS
        #
        # Star count
        main_run_processor.add_transition(Transition(process_star_count, ProcessStarCount.FADEOUT, process_fadeout))
        main_run_processor.add_transition(Transition(process_star_count, ProcessStarCount.FADEIN, process_fadein))

        # Fadeout
        main_run_processor.add_transition(Transition(process_fadeout, ProcessFadeout.COMPLETE, process_post_fadeout))
        main_run_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))

        # Fadein
        main_run_processor.add_transition(Transition(process_fadein, ProcessFadein.COMPLETE, process_star_count))

        # Post Fadeout
        main_run_processor.add_transition(Transition(process_post_fadeout, ProcessPostFadeout.FADEOUT, process_fadeout))
        main_run_processor.add_transition(Transition(process_post_fadeout, ProcessPostFadeout.FADEIN, process_fadein))
        main_run_processor.add_transition(Transition(process_post_fadeout, ProcessPostFadeout.FLASH, process_flash_check))
        main_run_processor.add_transition(Transition(process_post_fadeout, ProcessPostFadeout.COMPLETE, process_star_count))

        # Flash Check
        main_run_processor.add_transition(Transition(process_flash_check, ProcessFlashCheck.FADEOUT, process_fadeout))
        main_run_processor.add_transition(Transition(process_flash_check, ProcessFlashCheck.FADEIN, process_fadein))
        main_run_processor.add_transition(Transition(process_flash_check, ProcessFlashCheck.COMPLETE, process_star_count))

        #
        # FINAL_BOWSER_PROCESSOR TRANSITIONS
        #
        final_entry_processor.add_transition(Transition(process_final_stage_entry, ProcessFinalStageEntry.FADEOUT, process_fadeout))
        final_entry_processor.add_transition(Transition(process_fadeout, ProcessFadeout.COMPLETE, process_final_stage_entry))
        final_entry_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))

        final_spawn_processor.add_transition(Transition(process_final_star_spawn, ProcessFinalStarSpawn.FADEOUT, process_fadeout))
        final_spawn_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))

        final_grab_processor.add_transition(Transition(process_final_star_grab, ProcessFinalStarGrab.FADEOUT, process_fadeout))
        final_grab_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))

        final_idle_processor.add_transition(Transition(process_idle, ProcessIdle.FADEOUT, process_fadeout))
        final_idle_processor.add_transition(Transition(process_fadeout, process_fadeout.RESET, process_reset))
        final_idle_processor.add_transition(Transition(process_fadeout, process_fadeout.COMPLETE, process_idle))

        final_processor.add_transition(Transition(final_entry_processor, ProcessFinalStageEntry.ENTERED, final_spawn_processor))
        final_processor.add_transition(Transition(final_spawn_processor, ProcessFadeout.COMPLETE, final_entry_processor))
        final_processor.add_transition(Transition(final_spawn_processor, ProcessFinalStarSpawn.SPAWNED, final_grab_processor))
        final_processor.add_transition(Transition(final_grab_processor, ProcessFadeout.COMPLETE, final_entry_processor))
        final_processor.add_transition(Transition(final_grab_processor, ProcessFadeout.COMPLETE, final_entry_processor))
        final_processor.add_transition(Transition(final_grab_processor, ProcessFinalStarGrab.COMPLETE, final_idle_processor))

        #
        # DDD Processor
        #
        ddd_portal_processor.add_transition(Transition(process_ddd_portal, ProcessFindDDDPortal.FADEOUT, process_fadeout))
        ddd_portal_processor.add_transition(Transition(process_fadeout, ProcessFadeout.COMPLETE, process_ddd_portal))
        ddd_portal_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))

        ddd_entry_processor.add_transition(Transition(process_ddd_entry, ProcessDDDEntry.FADEOUT, process_fadeout))
        ddd_entry_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))

        ddd_processor.add_transition(Transition(ddd_portal_processor, ProcessFindDDDPortal.FOUND, ddd_entry_processor))
        ddd_processor.add_transition(Transition(ddd_entry_processor, ProcessFadeout.COMPLETE, ddd_portal_processor))

        #
        # LBLJ Processor
        #
        lblj_processor.initial_process = process_lblj
        lblj_processor.add_transition(Transition(process_lblj, ProcessLBLJ.FADEOUT, process_fadeout))
        lblj_processor.add_transition(Transition(process_fadeout, ProcessFadeout.COMPLETE, process_lblj))
        lblj_processor.add_transition(Transition(process_fadeout, ProcessFadeout.RESET, process_reset))
        lblj_processor.add_transition(Transition(process_reset, ProcessReset.RESET, process_lblj))


        as64_core.register_split_processor(as64_core.SPLIT_NORMAL, main_processor)
        as64_core.register_split_processor("SPLIT_LBLJ", lblj_processor)
        as64_core.register_split_processor(as64_core.SPLIT_MIPS, ddd_processor)
        as64_core.register_split_processor(as64_core.SPLIT_FINAL, final_processor)
        as64_core.set_update_listener(self.on_update)
        as64_core.set_error_listener(self.on_error)
        as64_core.start()

        self.app.set_started(True)

    def stop(self):
        as64_core.stop()

    def on_update(self, index, star_count, split_star):
        self.app.update_display(index, star_count, split_star)

    def on_error(self, error):
        self.error.emit(error)
        self.app.set_started(False)


if __name__ == "__main__":
    # Create QT Application
    qt_app = QtWidgets.QApplication(sys.argv)

    # Configure QT Application Style
    qt_app.setStyle('Fusion')

    palette = QtGui.QPalette()
    palette.setColor(QtGui.QPalette.Window, QtGui.QColor(36, 38, 50))
    #palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(152, 163, 191))
    palette.setColor(QtGui.QPalette.WindowText, QtGui.QColor(182, 193, 221))
    palette.setColor(QtGui.QPalette.Base, QtGui.QColor(15, 23, 30))
    palette.setColor(QtGui.QPalette.AlternateBase, QtGui.QColor(53, 55, 57))
    palette.setColor(QtGui.QPalette.ToolTipBase, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.ToolTipText, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Text, QtCore.Qt.white)
    palette.setColor(QtGui.QPalette.Button, QtGui.QColor(53, 55, 57))
    palette.setColor(QtGui.QPalette.ButtonText, QtGui.QColor(212, 223, 251))
    palette.setColor(QtGui.QPalette.BrightText, QtCore.Qt.red)
    palette.setColor(QtGui.QPalette.Highlight, QtGui.QColor(75, 110, 175))
    palette.setColor(QtGui.QPalette.HighlightedText, QtCore.Qt.black)
    palette.setColor(QtGui.QPalette.Light, QtGui.QColor(105, 108, 112))
    palette.setColor(QtGui.QPalette.Dark, QtGui.QColor(12, 14, 16))

    qt_app.setPalette(palette)

    # Add font to database
    QtGui.QFontDatabase.addApplicationFont(resource_path("resources/font/TCM_____.ttf"))

    # Print silent exceptions. DEBUGGING PURPOSES.
    """sys._excepthook = sys.excepthook


    def exception_hook(exc_type, value, traceback):
        print(exc_type, value, traceback)
        sys._excepthook(exc_type, value, traceback)
        sys.exit(1)


    sys.excepthook = exception_hook"""


    class StreamToLogger(object):
        def __init__(self, logger, log_level=logging.INFO):
            self.logger = logger
            self.log_level = log_level
            self.linebuf = ''

        def write(self, buf):
            for line in buf.rstrip().splitlines():
                self.logger.log(self.log_level, line.rstrip())

            sys.exit(1)

        def flush(self):
            pass


    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s:%(levelname)s:%(name)s:%(message)s',
        filename=".log",
        filemode='a'
    )

    stderr_logger = logging.getLogger('STDERR')
    sl = StreamToLogger(stderr_logger, logging.ERROR)
    #sys.stderr = sl

    # Create main application
    autosplit64 = AutoSplit64(qt_app)

    # Exit
    sys.exit(qt_app.exec_())
