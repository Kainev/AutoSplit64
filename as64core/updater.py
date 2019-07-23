from distutils.version import LooseVersion
import json
import requests
import win32api

from as64core.resource_utils import resource_path


class Updater(object):

    VERSION_URL = 'https://autosplit64.com/.version'

    def __init__(self):
        self._latest_version_info = None
        self._current_version_info = None
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
        if not self._current_version_info:
            self._load_current_version_info()

        if self._current_version_info["ignore_updates"] and not override_ignore:
            return False

        # Get data from latest .version
        if not self._latest_version_info:
            self._load_latest_version_info()

        # Check for update
        if LooseVersion(self._current_version_info["version"]) < LooseVersion(self._latest_version_info["version"]):
            return True
        else:
            return False

    def set_ignore_update(self, ignore):
        if not self._current_version_info:
            self._load_current_version_info()

        self._current_version_info["ignore_update"] = ignore

        with open(".version", "w") as file:
            json.dump(self._current_version_info, file, indent=4)

    def latest_version_info(self):
        if not self._latest_version_info:
            self.check_for_update()

        return self._latest_version_info

    def current_version_info(self):
        if not self._current_version_info:
            self._load_current_version_info()

        return self._current_version_info

    def _load_current_version_info(self):
        with open(resource_path(".version")) as file:
            self._current_version_info = json.load(file)

    def _load_latest_version_info(self):
        version_raw = requests.get(Updater.VERSION_URL)
        self._latest_version_info = json.loads(version_raw.text)

    def set_exit_listener(self, listener):
        self._exit_listener = listener