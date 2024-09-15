from requests import get
from json import loads
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QThread


class LJsonManifestDownload(QThread):

    finished = pyqtSignal(dict)

    def __init__(self, src):
        super(LJsonManifestDownload, self).__init__()
        self.src = src

    def run(self):
        retries = 0
        try:
            while retries < 10:
                try:
                    if self.src == "BMCLAPI":
                        host = "https://bmclapi2.bangbang93.com/"
                    else:
                        host = "https://launchermeta.mojang.com/"
                    versionManifest = loads(
                        get(url=host + "mc/game/version_manifest.json").text
                    )
                    if self.src == "BMCLAPI":
                        for i in versionManifest["versions"]:
                            i["url"] = i["url"].replace(
                                "https://piston-meta.mojang.com/",
                                "https://bmclapi2.bangbang93.com/",
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
