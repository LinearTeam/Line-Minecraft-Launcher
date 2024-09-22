from requests import get
from json import loads
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread

import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import host_provider


class LJsonManifestDownload(QThread):

    finished = pyqtSignal(dict)

    def __init__(self, src):
        super().__init__()
        self.src = src
        self.official_hosts = host_provider.LOfficialHosts()

    def run(self):
        retries = 0
        try:
            while retries < 10:
                try:
                    if self.src == "BMCLAPI":
                        provider = host_provider.LBmclApiSource()
                    else:
                        provider = host_provider.LOfficialSource()

                    versionManifest = loads(
                        get(provider.versionsManifest).text
                    )
                    if self.src == "BMCLAPI":
                        for i in versionManifest["versions"]:
                            i["url"] = i["url"].replace(
                                self.official_hosts.piston,
                                provider.hostsProvider.piston,
                            )
                        self.finished.emit(versionManifest)
                    else:
                        self.finished.emit(versionManifest)
                    break
                except:
                    retries += 1
                    continue
        except:
            pass
