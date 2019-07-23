import os
import json
import requests
from distutils.version import LooseVersion
from threading import Thread
import urllib
import zipfile


from as64core import resource_utils


class UpdaterCore(Thread):
    """
    Listener Callbacks:
        update_complete
        update_error
        download_complete
        download_report
        install_report

    """

    PATCH_FILE = "patch.zip"
    DEFAULT_VERSION_KEY = "version"

    def __init__(self,
                 master_version_url,
                 local_version_path,
                 master_version_key=DEFAULT_VERSION_KEY,
                 local_version_key=DEFAULT_VERSION_KEY):
        super().__init__()

        # Version Data Locations
        self.master_version_url = master_version_url
        self.local_version_path = local_version_path

        # Version Data
        self.master_version = None
        self.local_version = None

        # Version Number Keys
        self.master_version_key = master_version_key
        self.local_version_key = local_version_key

        # Listeners
        self._listener = None

        # Download Flags
        self._abort_download = False

    def run(self):
        self.acquire_master()
        self.load_local()

        if not self.update_available():
            self._listener.update_complete()
            return False

        self._listener.update_found(self.master_version[self.master_version_key])

        try:
            self._listener.download_begin()
        except AttributeError:
            pass

        self.download_patch()

        if self._abort_download:
            self.cleanup()

            try:
                self._listener.update_complete()
            except AttributeError:
                pass

            return False

        self.apply_patch()

        self.cleanup()

        self._listener.update_complete()

        return True

    def acquire_master(self):
        master_raw = requests.get(self.master_version_url)
        self.master_version = json.loads(master_raw.text)

    def load_local(self):
        with open(resource_utils.resource_path(self.local_version_path)) as local:
            self.local_version = json.load(local)

    def update_available(self):
        if not self.master_version:
            self.acquire_master()

        if not self.local_version:
            self.load_local()

        if LooseVersion(self.local_version[self.local_version_key]) < LooseVersion(self.master_version[self.master_version_key]):
            return True
        else:
            return False

    def download_patch(self):
        with open(UpdaterCore.PATCH_FILE, 'wb') as file:
            response = urllib.request.urlopen(self.master_version["location"])
            data = self._chunk_read(response, report_hook=self._chunk_report)

            file.write(data)

        if not self._abort_download:
            try:
                self._listener.download_complete()
            except AttributeError:
                pass

    def apply_patch(self):
        block_size = 8192

        try:
            with open(UpdaterCore.PATCH_FILE, mode="rb") as patch:
                zip_file = zipfile.ZipFile(patch)

                total_size = sum([zip_file_info.file_size for zip_file_info in zip_file.filelist])
                current_bytes = 0

                for file_name in zip_file.namelist():
                    output_file = open(file_name, 'wb')
                    file = zip_file.open(file_name)

                    while True:
                        chunk = file.read(block_size)
                        current_bytes += len(chunk)

                        try:
                            self._listener.install_report(float(current_bytes) / float(total_size) * 100.0)
                        except AttributeError:
                            pass

                        if not chunk:
                            break

                        output_file.write(chunk)

                    file.close()
                    output_file.close()
        except FileNotFoundError:
            try:
                self._listener.update_error("Patch file not found")
            except AttributeError:
                pass
        except PermissionError:
            try:
                self._listener.update_error("Permission Error: Access Denied")
            except AttributeError:
                pass

    def cleanup(self):
        try:
            os.remove(UpdaterCore.PATCH_FILE)
        except FileNotFoundError:
            pass
        except PermissionError:
            pass

    def _chunk_report(self, current_bytes, total_size):
        percent = float(current_bytes) / total_size
        percent = round(percent * 100, 2)

        try:
            self._listener.download_report(percent)
        except AttributeError:
            pass

    def _chunk_read(self, response, chunk_size=8192, report_hook=None):
        total_size = int(response.info().get("Content-Length").strip())
        current_bytes = 0
        data = b""

        while not self._abort_download:
            chunk = response.read(chunk_size)
            current_bytes += len(chunk)

            if not chunk:
                break

            if report_hook:
                report_hook(current_bytes, total_size)

            data += chunk

        return data

    def abort_download(self):
        self._abort_download = True

    def set_listener(self, listener):
        self._listener = listener
