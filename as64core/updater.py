import win32api

from as64updater.update_core import UpdaterCore


class Updater(object):

    VERSION_URL = 'https://autosplit64.com/.master_version'
    LOCAL_VERSION_PATH = ".version"

    def __init__(self):
        self._updater = UpdaterCore(master_version_url=Updater.VERSION_URL,
                                    local_version_path=Updater.LOCAL_VERSION_PATH)
        self._exit_listener = None

    def install_update(self):
        try:
            self._exit_listener.exit()
        except AttributeError:
            pass

        try:
            win32api.WinExec(r'Updater.exe')
        except:
            pass

    def check_for_update(self, override_ignore=False):
        # Load data from local installs .version
        if self._updater.get_local()["ignore_updates"] and not override_ignore:
            return False

        return self._updater.update_available()

    def set_ignore_update(self, ignore):
        self._updater.set_ignore_update(ignore)

    def latest_version_info(self):
        return self._updater.get_master()

    def current_version_info(self):
        return self._updater.get_local()

    def set_exit_listener(self, listener):
        self._exit_listener = listener
