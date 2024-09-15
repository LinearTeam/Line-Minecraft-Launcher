import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import asyncio
import logging
import json

from qframelesswindow import FramelessDialog
from qfluentwidgets import MessageBox
from PyQt5.QtCore import QThread, pyqtSignal

from Core.Download.downloader_ui import Ui_DownloadingInfo
from Core.Download.async_downloader import formatData, LAsyncDownloader

WORKING_DIR = (os.getcwd()).replace("\\", "/") + "/Core/Shared/GlobalDirectory.json"


class LDownloadThread(QThread):
    callUpdateProgress = pyqtSignal(int)
    callCompleted = pyqtSignal(list)

    def __init__(self, files):
        super().__init__()
        self.files = formatData(files)

    async def main(self):
        await self.asyncDownloader.main(self.files)

    def run(self):
        self.asyncDownloader = LAsyncDownloader(self.callUpdateProgress.emit)
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(self.main())
        self.callCompleted.emit(
            [
                "下载完成",
                f"文件总数:{self.asyncDownloader.totalCounts}\n成功数:{self.asyncDownloader.successfulCounts}\n失败数:{self.asyncDownloader.totalCounts -self.asyncDownloader.successfulCounts}",
            ]
        )


class LWindowSupport(FramelessDialog, Ui_DownloadingInfo):

    def __init__(self, files, parent=None):
        super().__init__()
        with open(WORKING_DIR, "r") as f:
            self.workingDir = json.load(f)["Root"]

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(filename)s][%(levelname)s]: %(message)s",
            filename=(f"{self.workingDir}/Log/LatestDownloadingLog.log"),
            filemode="w",
        )

        self.setupUi(self)

        try:
            self.setGeometry(
                (parent.width() - self.width()) // 2 + parent.x(),
                (parent.height() - self.height()) // 2 + parent.y(),
                self.width(),
                self.height(),
            )
        except:
            pass

        self.files = files
        self.DownloadingProgress.setMaximum(len(self.files))
        self.DownloadingProgress.setMinimum(0)

        self.StartAndPause.clicked.connect(self.judge)
        self.Shutdown.clicked.connect(self.shutdown)

        self.downloadThread = LDownloadThread(self.files)
        self.downloadThread.callUpdateProgress.connect(self.callProgressUpdate)
        self.downloadThread.callCompleted.connect(self.finish)
        self.downloadThread.start()

    def shutdown(self):
        logging.info("Download dialog closed")
        self.downloadThread.asyncDownloader.shutdown()
        self.downloadThread.quit()
        self.close()

    def judge(self):
        if self.StartAndPause.isChecked() == True:
            self.downloadThread.asyncDownloader.pause()
            self.StartAndPause.setText("开始")
        else:
            self.StartAndPause.setText("暂停")
            self.downloadThread.asyncDownloader.resume()

    def finish(self, arg):
        Dialog = MessageBox(arg[0], arg[1], self)
        print(
            f"Downloading finished, {self.downloadThread.asyncDownloader.totalCounts} in total, {self.downloadThread.asyncDownloader.successfulCounts} file(s) succeed, {self.downloadThread.asyncDownloader.totalCounts - self.downloadThread.asyncDownloader.successfulCounts} files(s) failed"
        )
        logging.info(
            f"Downloading finished, {self.downloadThread.asyncDownloader.totalCounts} in total, {self.downloadThread.asyncDownloader.successfulCounts} file(s) succeed, {self.downloadThread.asyncDownloader.totalCounts - self.downloadThread.asyncDownloader.successfulCounts} files(s) failed"
        )
        if Dialog.exec():
            self.shutdown()
        else:
            self.shutdown()

    def callProgressUpdate(self, i):
        self.DownloadingProgress.setValue(i)
        self.DownloadingPercent.setText(
            str(round((i * 100) / len(self.files), 2)) + "%"
        )
