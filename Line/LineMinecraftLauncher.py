import datetime
import traceback
import logging
import sys
import json
import os
import math
import psutil

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import ctypes

whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Line Minecraft Launcher")

from PyQt5.QtCore import Qt, QThread,pyqtSignal
from PyQt5.QtWidgets import QFileDialog, QApplication
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtWidgets import QListWidgetItem
from qframelesswindow import AcrylicWindow, StandardTitleBar, FramelessDialog
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import MessageBox as MsgBox
from qfluentwidgets import setThemeColor, RoundMenu, Action
from plyer import notification

from Core.Auth import microsft_oauth
from Core.Launcher import global_io_controller
from Core.Download.json_manifest_downloader import LJsonManifestDownload
from Core.Download.json_parser import LParsingJsons
from Core.Download.async_downloader_with_ui import LWindowSupport
from Core.Launch.launch_core import LLaunchThread
from Core.Launcher.auto_memory_manager import LSubmitMemory

from Interface.Interface.Compiled.LineUI import Ui_LineMinecraftlauncher as LineMainUI
from Interface.Interface.Compiled.Naming import Ui_Naming as Naming

# from Core import MicrosoftLoginProcessor
# from Core import Downloader


class LRustDownloader(QThread):


    def __init__(self, threads = "64"):
        super().__init__()
        self.threads = threads

    def run(self):
        os.system(
            "start .\\Core\\api\\Rust\\RustAsyncDownloader.exe "
            + os.getcwd()
            + "\\Core\\api\\Rust\\downloads.json "
            + self.threads
        )


class LLineMinecraftLauncher(AcrylicWindow, LineMainUI):

    def closeEvent(self, a0) -> None:
        logging.info("LMC Shutdown")
        loadedData = {
            "username": self.user if self.user != "" else "No Data Loaded",
            "userType": (
                "Microsoft"
                if self.LoginTypeSwitcher.isChecked() == True
                else "Offlined"
            ),
            "minecraftDirectory": self.minecraftDirectory,
            "minecraftVersion": self.launchVersion,
            "memorySize": self.MemoryAdjuster.value(),
        }
        self.IoController.writeLoadedData(loadedData)

    def __init__(self):
        """
        嗯~滋滋→嗯~噔噔↗磁枯～蹦～叮叮～噔噔噔噔噔噔～
        一样的天空。✌却一样只有错过π_π
        一样的歌✌还是唱着他多爱她☹
        呲～蹦蹦↗
        一样快死心❤️
        一样的剧情☹
        却还是期待着✌
        她嘴里的那句我爱你♥
        她说 去。。的花海π_π
        呲呲～噔↗☹(心碎
        """
        super().__init__()
        self.setupUi(self)
        sys.excepthook = self.crashReport

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(filename)s][%(levelname)s][%(lineno)d]: %(message)s",
            filename="./Log/LatestLog.log",
            filemode="w",
        )


        logging.info("A new Line Minecraft Launcher instance started")

        self.setTitleBar(StandardTitleBar(self))
        self.poper.setCurrentIndex(0)
        #Pixmap = QPixmap("./Interface/resources/Background_KeQing.jpg")

        with open("./Core/Shared/GlobalDirectory.json", "w") as f:
            json.dump({"Root": (os.getcwd()).replace("\\", "/")}, f)
        # 24:30
        #self.Background.setScaledContents(True)
        #self.Background.setPixmap(Pixmap)
        self.RefreshVersions.setIcon(FIF.UPDATE)

        self.IoController = global_io_controller.LGlobalIOController()
        self.latestLoadedData = self.IoController.readLatestLoadedData()
        try:
            print(self.latestLoadedData)

            self.user = ""
            self.minecraftDirectory = ""
            self.launchVersion = ""
            self.user = self.latestLoadedData["username"]
            self.minecraftDirectory = self.latestLoadedData["minecraftDirectory"]
            self.launchVersion = self.latestLoadedData["minecraftVersion"]
            if self.latestLoadedData["userType"] == "Microsoft":
                self.TokenRefresher = microsft_oauth.LMinecraftAuthenticator(
                    self.latestLoadedData["username"]
                )
                self.TokenRefresher.finished.connect(self.msgboxHandler)
                self.TokenRefresher.start()
                self.LoginTypeSwitcher.setChecked(True)
                self.LoginTypeSwitcher.setText("微软登录")
        except:
            logging.warning("No user or available path loaded last time")

        # 预处理
        try:
            self.MemoryAdjuster.setMaximum(
                math.floor(psutil.virtual_memory().total / 1024 / 1024)
            )
            self.MemoryAdjuster.setMinimum(128)
            self.MemoryAdjuster.setSingleStep(1)
            if int(self.latestLoadedData["memorySize"]) > math.floor(
                psutil.virtual_memory().total / 1024 / 1024
            ):
                self.MemoryAdjuster.setValue(0)
            else:
                self.MemoryAdjuster.setValue(int(self.latestLoadedData["memorySize"]))
                self.MemorySizeDisplay.setText(
                    str(self.latestLoadedData["memorySize"]) + "M"
                )
        except Exception as e:
            self.AutoMemoryManagement.setChecked(True)
            self.switchAutoMemoryManagement()
        self.readUsers()
        try:
            self.MinecraftPathSelector.addItems(
                self.IoController.readSavedMinecraftDirectories(req="List")
            )
            self.MinecraftPathSelector.setCurrentIndex(
                [
                    self.MinecraftPathSelector.itemText(x)
                    for x in range(self.MinecraftPathSelector.count())
                ].index(self.minecraftDirectory)
            )
        except:
            pass
        self.scanMc()
        try:
            if self.latestLoadedData["minecraftVersion"] in self.versionsInPath:
                fs = self.generateAction()
                for i in fs:
                    if self.latestLoadedData["minecraftVersion"] == i[1]:
                        i[0]()
            else:
                pass
        except:
            pass

        # Setup settings
        self.DownloadSourceSelector.addItems(
            ["官方源(数据最新, 速度也可能最快)", "BMCLAPI(速度快，同步快)", "Line Mirror(测试中，速度一般，同步较慢)"]
        )
        self.DownloaderSelector.addItems(["Python", "Rust"])
        self.settings = self.IoController.readSettings()
        self.downloaderType = self.settings["downloaderType"]
        self.downloadSrc = self.settings["downloadSrc"]
        self.DownloadSourceSelector.setCurrentIndex(
            [
                self.DownloadSourceSelector.itemText(x)
                for x in range(self.DownloadSourceSelector.count())
            ].index(
                "官方源(数据最新, 速度也可能最快)"
                if self.downloadSrc == "Official"
                else "BMCLAPI(速度快，同步快)" if self.downloadSrc == "BmclApi"
                else "Line Mirror(测试中，速度一般，同步较慢)"
            )
        )
        self.DownloaderSelector.setCurrentIndex(
            [
                self.DownloaderSelector.itemText(x)
                for x in range(self.DownloaderSelector.count())
            ].index("Python" if self.downloaderType == "python" else "Rust")
        )
        
        self.driveDownloadManifest()
        

        # 初始化导航栏

        self.Navigation.addItem(
            routeKey="Home",
            icon=FIF.HOME,
            text="首页",
            onClick=lambda: self.changePage(0),
        )
        self.Navigation.addItem(
            routeKey="Launch",
            icon=FIF.CHEVRON_RIGHT,
            text="启动",
            onClick=lambda: self.changePage(1),
        )
        self.Navigation.addItem(
            routeKey="Account",
            icon=FIF.PEOPLE,
            text="账户",
            onClick=lambda: self.changePage(2),
        )
        self.Navigation.addItem(
            routeKey="Terminal",
            icon=FIF.COMMAND_PROMPT,
            text="终端",
            onClick=lambda: self.changePage(3),
        )
        self.Navigation.addItem(
            routeKey="Download",
            icon=FIF.DOWNLOAD,
            text="下载",
            onClick=lambda: self.changePage(4),
        )
        self.Navigation.addItem(
            routeKey="Settings",
            icon=FIF.SETTING,
            text="设置",
            onClick=lambda: self.changePage(5),
        )

        # 事件
        self.ClearOfflinedUsername.clicked.connect(
            lambda: self.OfflinedUsernameEdit.clear()
        )
        self.OfflinedUsernameEdit.textEdited.connect(self.charFilter)
        self.Download.clicked.connect(lambda: self.changePage(6))
        self.MicrosoftLogin.clicked.connect(lambda: self.changeLoginPage(1))
        self.OfflinedLogin.clicked.connect(lambda: self.changeLoginPage(0))
        self.MemoryAdjuster.valueChanged.connect(self.updateMemoryLabel)
        self.AddMinecraftDirectory.clicked.connect(self.addMinecraftDirectory)
        self.LoginTypeSwitcher.clicked.connect(self.updateLoginType)
        self.LaunchingAccountsSelector.currentIndexChanged.connect(self.updateUser)
        self.ManageMinecraft.clicked.connect(self.listSavedMinecraftDirectories)
        self.MinecraftDirectoriesManagementView.itemClicked.connect(
            self.showSelectedDirectoryDetails
        )
        self.MinecraftPathSelector.currentIndexChanged.connect(self.refreshMcDir)
        self.DownloadSourceSelector.currentIndexChanged.connect(self.setupDownloadSrc)
        self.RefreshVersions.clicked.connect(self.driveDownloadManifest)
        self.ShowOldVersions.clicked.connect(self.updateVersionsView)
        self.ShowSnapshotVersions.clicked.connect(self.updateVersionsView)
        self.SearchInVersionsView.textEdited.connect(self.updateSearchedVersionsView)
        self.VersionsView.itemClicked.connect(self.transferVersionInfo)
        self.ConfirmStartMicrosoftLogin.clicked.connect(self.driveLogin)
        self.ConfirmOfflinedUsername.clicked.connect(self.offlinedLoginProcess)
        self.InstallationName.textEdited.connect(self.validationChecker)
        self.ConfirmDownload.clicked.connect(self.driveDownload)
        self.Launch.clicked.connect(self.launchMinecraft)
        self.AutoMemoryManagement.clicked.connect(self.switchAutoMemoryManagement)
        self.DownloaderSelector.currentIndexChanged.connect(self.setupDownloader)

    def setupDownloader(self):
        self.downloaderType = (
            "python" if self.DownloaderSelector.currentIndex() == 0 else "rust"
        )
        self.IoController.overwriteSettings("downloaderType", self.downloaderType)

    def setMemory(self, value: int):
        print(f"Submitted {str(value)}M")
        self.MemoryAdjuster.setValue(value)
        self.updateMemoryLabel()

    def switchAutoMemoryManagement(self):
        if self.AutoMemoryManagement.isChecked():
            self.MemoryAdjuster.setEnabled(False)
            self.MemoryManager = LSubmitMemory(1)
            self.MemoryManager.submittedMemory.connect(self.setMemory)
            self.MemoryManager.start()
        else:
            self.MemoryAdjuster.setEnabled(True)
            self.MemoryManager.pause()

    def launchMinecraft(self):
        try:
            self.Launch.setDisabled(True)
            launchArgs = {
                "mcDir": self.MinecraftPathSelector.currentText(),
                "mcVer": self.launchVersion,
                "targetJava": "C:/Program Files (x86)/Common Files/Oracle/Java/java8path/java.exe",
                "memory": str(self.MemoryAdjuster.value()),
                "username": self.LaunchingAccountsSelector.currentText(),
                "userType": (
                    "msa" if self.LoginTypeSwitcher.isChecked() == True else "Legacy"
                ),
                "uuid": "",
                "accessToken": "",
                "windowWidth": "",
                "windowHeight": "",
                "jvmAddtionalParameters": "",
                "mcAddtionalParameters": "",
                "extra": False,
            }
            if (
                self.LaunchingAccountsSelector.currentText()
                == self.latestLoadedData["username"]
                and self.LoginTypeSwitcher.isChecked() == True
            ):
                info = self.IoController.readMicrosoftUser(
                    self.LaunchingAccountsSelector.currentText()
                )
                launchArgs["uuid"] = info["uuid"]
                launchArgs["accessToken"] = info["accessToken"]
                self.LaunchThread = LLaunchThread(launchArgs, True)
                self.LaunchThread.start()
            elif (
                self.LaunchingAccountsSelector.currentText()
                != self.latestLoadedData["username"]
                and self.LoginTypeSwitcher.isChecked() == True
            ):
                self.TokenRefresher = microsft_oauth.LMinecraftAuthenticator(
                    self.LaunchingAccountsSelector.currentText()
                )
                self.TokenRefresher.finished.connect(self.msgboxHandler)
                self.TokenRefresher.start()
                while True:
                    if self.TokenRefresher.isFinished() == True:
                        info = self.IoController.readMicrosoftUser(
                            self.LaunchingAccountsSelector.currentText()
                        )
                        launchArgs["uuid"] = info["uuid"]
                        launchArgs["accessToken"] = info["accessToken"]
                        self.LaunchThread = LLaunchThread(launchArgs, True)
                        self.LaunchThread.start()
                        break
            else:
                self.LaunchThread = LLaunchThread(launchArgs, False)
                self.LaunchThread.start()
            self.Launch.setEnabled(True)
        except Exception as e:
            self.msgboxHandler(["错误", "无法启动该版本，请检查日志"])
            logging.error(
                f"Cannot run a new Minecraft Instance, Version: {self.launchVersion}, cause {str(e)}"
            )
            self.Launch.setEnabled(True)

    def callbackDownload(self, stat):
        if stat == 1:
            self.changePage(0)
            self.msgboxHandler(["完成", "下载已经完成", "windows"])
            self.refreshMcDir()
        else:
            logging.error("Something went wrong during callback download")

    def driveDownload(self):
        if self.stopDownload == False:
            if self.downloaderType == "python":
                logging.info(
                    f"Downloading {self.parsedInformation['version']} to {self.MinecraftPathSelector.currentText()}"
                )
                total = LParsingJsons(
                    self.MinecraftPathSelector.currentText(),
                    self.parsedInformation["version"],
                    self.parsedInformation["url"],
                    self.InstallationName.text(),
                    self.downloadSrc,
                ).download_version_json()
                self.downloaderWithUI = LWindowSupport(total, self)
                self.downloaderWithUI.show()
                self.downloaderWithUI.exec_()
            else:
                Query = MsgBox(
                    "稍等",
                    "您使用了Rust下载器, 请不要关闭主程序, 下载完成后会自动跳转\n请在网页中查看更多信息, 如果确认请按OK",
                    self
                )
                if Query.exec():
                    total = LParsingJsons(
                        self.MinecraftPathSelector.currentText(),
                        self.parsedInformation["version"],
                        self.parsedInformation["url"],
                        self.InstallationName.text(),
                        self.downloadSrc,
                    ).download_version_json()
                    del total
                    self.downloaderWithoutUi = LRustDownloader()
                    self.downloaderWithoutUi.start()
                else:
                    pass
            if self.downloaderType != "python":
                self.changePage(0)
            else:
                self.changePage(0)
                self.msgboxHandler(["完成", "下载已经完成", "windows"])
                self.refreshMcDir()   
        else:
            Query = MsgBox(
                "警告",
                f"这个版本已经存在于{self.minecraftDirectory}中，如果您执意继续，将补全此版本\n 您确定要继续吗?",
                self
            )
            if Query.exec():
                if self.downloaderType == "python":
                    logging.info(
                        f"Downloading {self.parsedInformation['version']} to {self.MinecraftPathSelector.currentText()}"
                    )
                    total = LParsingJsons(
                        self.MinecraftPathSelector.currentText(),
                        self.parsedInformation["version"],
                        self.parsedInformation["url"],
                        self.InstallationName.text(),
                        self.downloadSrc,
                    ).download_version_json()
                    self.downloaderWithUI = LWindowSupport(total, self)
                    self.downloaderWithUI.show()
                    self.downloaderWithUI.exec_()
                else:
                    Query = MsgBox(
                        "稍等",
                        "您使用了Rust下载器, 请不要关闭主程序, 下载完成后会自动跳转\n请在网页中查看更多信息, 如果确认请按OK",
                        self,
                    )
                    if Query.exec():
                        total = LParsingJsons(
                            self.MinecraftPathSelector.currentText(),
                            self.parsedInformation["version"],
                            self.parsedInformation["url"],
                            self.InstallationName.text(),
                            self.downloadSrc,
                        ).download_version_json()
                        del total
                        self.downloaderWithoutUi = LRustDownloader()
                        self.downloaderWithoutUi.start()
                    else:
                        self.changePage(6)
                if self.downloaderType != "python":
                    while True:
                        if self.downloaderWithoutUi.isFinished() == True:
                            self.changePage(0)
                            self.msgboxHandler(["完成", "下载已经完成", "windows"])
                            self.refreshMcDir()
                            break
                else:
                    self.changePage(0)
                    self.msgboxHandler(["完成", "下载已经完成", "windows"])
                    self.refreshMcDir()   
            else:
                self.changePage(6)
            self.refreshMcDir()

    def validationChecker(self):
        try:
            if self.InstallationName.text() not in [
                x
                for x in os.listdir(self.minecraftDirectory + "/versions")
                if os.path.isdir(self.minecraftDirectory + "/versions/" + x) == True
            ]:
                self.IsNameAvailable.setText("可用")
                self.IsNameAvailable.setStyleSheet("color: green")
                self.stopDownload = False
            else:
                self.IsNameAvailable.setText("名称已存在")
                self.IsNameAvailable.setStyleSheet("color: red")
                self.stopDownload = True
                logging.warning(
                    "This name is existing in the Minecraft Directory which you selected in Launching page"
                )
        except:
            self.IsNameAvailable.setText("可用")
            self.IsNameAvailable.setStyleSheet("color: green")
            self.stopDownload = False

    def charFilter(self):
        acceptableChars = set(
            "0123456789qwertyuiopasdfghjklzxcvbnmQAZWSXEDCRFVTGBYHNUJMIKOLP_"
        )
        self.OfflinedUsernameEdit.setText(
            allowedContent := self.OfflinedUsernameEdit.text().replace(" ", "")
        )
        validation = set(allowedContent)
        if validation.issubset(acceptableChars):
            pass
        else:
            self.OfflinedUsernameEdit.clear()
            logging.warning("Cleared an invalid username")

    def transferVersionInfo(self, version: QListWidgetItem):
        for i in self.classify.values():
            try:
                url = i[version.text()]["url"]
                releaseTime = i[version.text()]["ReleaseTime"]
            except:
                pass
        self.parsedInformation = {
            "version": version.text(),
            "url": url,
            "releaseTime": releaseTime,
        }
        self.InstallationName.setText(self.parsedInformation["version"])
        try:
            if self.InstallationName.text() not in [
                x
                for x in os.listdir(self.minecraftDirectory + "/versions")
                if os.path.isdir(self.minecraftDirectory + "/versions/" + x) == True
            ]:
                self.IsNameAvailable.setText("可用")
                self.IsNameAvailable.setStyleSheet("color: green")
                self.stopDownload = False
            else:
                self.IsNameAvailable.setText("名称已存在")
                self.IsNameAvailable.setStyleSheet("color: red")
                self.stopDownload = True
                logging.warning(
                    "This name is existing in the Minecraft Directory which you selected in Launching page"
                )
        except:
            self.IsNameAvailable.setText("可用")
            self.IsNameAvailable.setStyleSheet("color: green")
            self.stopDownload = False
        self.changePage(7)

    def updateSearchedVersionsView(self):
        self.VersionsView.clear()
        keyword = self.SearchInVersionsView.text()
        if keyword != "":
            for i in self.versionItems:
                if keyword in i:
                    self.VersionsView.addItem(i)
        else:
            self.updateVersionsView()

    def updateVersionsView(self):
        self.VersionsView.clear()
        if (
            self.ShowSnapshotVersions.isChecked() == False
            and self.ShowOldVersions.isChecked() == False
        ):
            self.VersionsView.addItems([x for x in self.classify["release"].keys()])
        if (
            self.ShowSnapshotVersions.isChecked() == True
            and self.ShowOldVersions.isChecked() == False
        ):
            self.VersionsView.addItems(
                [x for x in self.classify["snapshot"].keys()]
                + [x for x in self.classify["release"].keys()]
            )
        if (
            self.ShowSnapshotVersions.isChecked() == False
            and self.ShowOldVersions.isChecked() == True
        ):
            self.VersionsView.addItems(
                [x for x in self.classify["release"].keys()]
                + [x for x in self.classify["oldBeta"].keys()]
                + [x for x in self.classify["oldAlpha"].keys()]
            )
        if (
            self.ShowSnapshotVersions.isChecked() == True
            and self.ShowOldVersions.isChecked() == True
        ):
            self.VersionsView.addItems(
                [x for x in self.classify["snapshot"].keys()]
                + [x for x in self.classify["release"].keys()]
                + [x for x in self.classify["oldBeta"].keys()]
                + [x for x in self.classify["oldAlpha"].keys()]
            )
        self.versionItems = []
        for i in range(self.VersionsView.model().rowCount()):
            text = self.VersionsView.item(i).text()
            self.versionItems.append(text)

    def driveDownloadManifest(self):
        self.VersionsView.clear()
        self.msgboxHandler(["提示", "请稍后，正在刷新版本列表", "windows"])
        logging.info("Refreshing Minecraft versions list")
        try:
            self.thread = LJsonManifestDownload(self.downloadSrc)
            self.thread.finished.connect(self.listMcVersions)
            self.thread.start()
        except:
            self.msgboxHandler(
                ["错误", "无法刷新版本，请排查：\n 1.网络未连接 \n 2.过于频繁地刷新"]
            )
            logging.error(
                "Failed to refresh the versions list, did you lose your internet connection?"
            )

    def listMcVersions(self, VersionsManifest):
        print("callback")
        self.classify = {"release": {}, "snapshot": {}, "oldBeta": {}, "oldAlpha": {}}
        for i in VersionsManifest["versions"]:
            if i["type"] == "release":
                self.classify["release"][i["id"]] = {
                    "url": i["url"],
                    "ReleaseTime": i["releaseTime"],
                }
            elif i["type"] == "snapshot":
                self.classify["snapshot"][i["id"]] = {
                    "url": i["url"],
                    "ReleaseTime": i["releaseTime"],
                }
            elif i["type"] == "old_beta":
                self.classify["oldBeta"][i["id"]] = {
                    "url": i["url"],
                    "ReleaseTime": i["releaseTime"],
                }
            elif i["type"] == "old_alpha":
                self.classify["oldAlpha"][i["id"]] = {
                    "url": i["url"],
                    "ReleaseTime": i["releaseTime"],
                }
        if (
            self.ShowSnapshotVersions.isChecked() == False
            and self.ShowOldVersions.isChecked() == False
        ):
            self.VersionsView.addItems([x for x in self.classify["release"].keys()])
        if (
            self.ShowSnapshotVersions.isChecked() == True
            and self.ShowOldVersions.isChecked() == False
        ):
            self.VersionsView.addItems(
                [x for x in self.classify["snapshot"].keys()]
                + [x for x in self.classify["release"].keys()]
            )
        if (
            self.ShowSnapshotVersions.isChecked() == False
            and self.ShowOldVersions.isChecked() == True
        ):
            self.VersionsView.addItems(
                [x for x in self.classify["release"].keys()]
                + [x for x in self.classify["oldBeta"].keys()]
                + [x for x in self.classify["oldAlpha"].keys()]
            )
        if (
            self.ShowSnapshotVersions.isChecked() == True
            and self.ShowOldVersions.isChecked() == True
        ):
            self.VersionsView.addItems(
                [x for x in self.classify["snapshot"].keys()]
                + [x for x in self.classify["release"].keys()]
                + [x for x in self.classify["oldBeta"].keys()]
                + [x for x in self.classify["oldAlpha"].keys()]
            )
        self.versionItems = []
        for i in range(self.VersionsView.model().rowCount()):
            text = self.VersionsView.item(i).text()
            self.versionItems.append(text)

    def setupDownloadSrc(self):
        self.downloadSrc = (
            "Official" if self.DownloadSourceSelector.currentIndex() == 0 else "BmclApi" if self.DownloadSourceSelector.currentIndex() == 1 else "LineMirror"
        )
        logging.info(f"Download Source has been set to {self.downloadSrc}")
        self.IoController.overwriteSettings("downloadSrc", self.downloadSrc)

    def refreshMcDir(self):
        self.minecraftDirectory = self.MinecraftPathSelector.currentText()
        self.scanMc()

    def generateAction(self):
        def wrapper(version):
            def action():
                self.Launch.setText("启动: " + version)
                self.launchVersion = version
            return action
        fs = []
        for i in os.listdir(self.minecraftDirectory + "/versions"):
            if os.path.isdir(self.minecraftDirectory + '/versions/' + i) == True:
                fs.append((wrapper(i), i))
        return fs
    
    def scanMc(self):
        try:
            self.menu = RoundMenu(parent=self)
            fs = self.generateAction()
            for i in fs:
                self.menu.addAction(Action(FIF.DOCUMENT, i[1], triggered=i[0]))
            self.Launch.setFlyout(self.menu)
            self.versionsInPath = [
                x
                for x in os.listdir(self.minecraftDirectory + "/versions")
                if os.path.isdir(self.minecraftDirectory + "/versions/" + x) == True
            ]
            count = len(
                [
                    x
                    for x in os.listdir(self.minecraftDirectory + "/versions")
                    if os.path.isdir(self.minecraftDirectory + "/versions/" + x) == True
                ]
            )
            logging.info(f"{count} available Minecraft(s) in {self.minecraftDirectory}")
        except:
            logging.exception("This is not a CORRECT Minecraft Path")

    def removeManagedDirectory(self):
        self.IoController.removeManagedDir(
            self.ManagementCustomName.text().replace("自定义名称:", "")
        )
        self.listSavedMinecraftDirectories()

    def openManagedMinecraftDircetory(self):
        os.startfile(
            os.path.abspath(
                p := self.MinecraftDirectoryManagement.text().replace(
                    "版本路径:   ", ""
                )
                + "/versions"
            )
        )

    def showSelectedDirectoryDetails(self, item):
        self.MinecraftDirectoryManagement.setText(
            "版本路径:" + item.text().replace(item.text().split("   ")[0], "")
        )
        self.ManagementCustomName.setText("自定义名称:" + item.text().split("   ")[0])
        versionsList = os.listdir(
            item.text()
            .replace(item.text().split("   ")[0], "")
            .replace("/", "\\")
            .replace("   ", "")
            + "\\versions"
        )
        self.CurrentMinecraftsView.addItems(versionsList)
        self.changePage(11)

    def listSavedMinecraftDirectories(self):
        self.MinecraftDirectoriesManagementView.clear()
        savedMinecraftDir = self.IoController.readSavedMinecraftDirectories(req="List")
        for i in savedMinecraftDir:
            self.MinecraftDirectoriesManagementView.addItem(
                list(i.keys())[0] + "   " + list(i.values())[0]
            )
        self.changePage(10)

    def updateUser(self):
        self.user = self.LaunchingAccountsSelector.currentText()
        if self.LoginTypeSwitcher.isChecked() == True:
            self.TokenRefresher = microsft_oauth.LMinecraftAuthenticator(self.user)
            self.TokenRefresher.finished.connect(self.msgboxHandler)
            self.TokenRefresher.start()

    def readUsers(self):
        try:
            self.LaunchingAccountsSelector.clear()
            savedUsers = self.IoController.readSavedUsers(
                self.latestLoadedData["userType"]
            )
            self.LaunchingAccountsSelector.addItems(savedUsers)
        except:
            pass

    def updateLoginType(self):
        if self.LoginTypeSwitcher.isChecked() == True:
            self.LoginTypeSwitcher.setText("微软登录")
            self.latestLoadedData["userType"] = "Microsoft"
        else:
            self.LoginTypeSwitcher.setText("离线登录")
            self.latestLoadedData["userType"] = "Offlined"
        self.readUsers()

    def addMinecraftDirectory(self):
        directory = QFileDialog.getExistingDirectory(None, "选择Minecraft目录", "C:/")
        if not len(directory) == 0:
            self.NamingDialogInstance = LNamingDialog(self)
            self.NamingDialogInstance.showDialog()
            self.NamingDialogInstance.Confirm.clicked.connect(
                lambda: self.getCustomName(directory)
            )
            logging.info("A new Minecraft path added")
        else:
            self.msgboxHandler(["失败", "未选中"])
            logging.info("Path Unselected")

    def getCustomName(self, directory):
        Flag = self.NamingDialogInstance.NameEdit.text()
        self.NamingDialogInstance.close()
        self.MinecraftPathSelector.addItem(directory)
        self.minecraftDirectory = directory
        self.msgboxHandler(["成功!", "目录已添加"])
        self.IoController.writeNewMinecraftDirectory(dir=directory, flag=Flag)

    def updateMemoryLabel(self):
        self.MemorySizeDisplay.setText(str(self.MemoryAdjuster.value()) + "M")

    def changePage(self, pageIndex: int):  # 处理页面切换
        if pageIndex == 2:
            self.changeLoginPage(0)
        self.poper.setCurrentIndex(pageIndex)

    def changeLoginPage(self, pageIndex: int):
        self.PopUpAniStackedWidget.setCurrentIndex(pageIndex)

    def msgboxHandler(self, body: list):  # 处理自定义的消息窗口
        RaiseType = "general"
        body.append(RaiseType)
        if body[2] == "general":
            try:
                msg = MsgBox(body[0], body[1], self)
                msg.exec_()
            except Exception as e:
                logging.error("Failed to raise a general notification")
        elif body[2] == "windows":
            try:
                notification.notify(
                    title="Line Minecraft Launcher " + body[0],
                    message=body[1],
                    app_icon="./Interface/Icons/LMC.ico",
                    timeout=1,
                )
            except:
                logging.error("Failed to raise a windows style notification")
        else:
            logging.error("Unknown message type")

    def driveLogin(self):  # 驱动登录
        self.Processor = microsft_oauth.LMinecraftAuthenticator("NotFound")
        self.Processor.start()
        self.Processor.finished.connect(self.msgboxHandler)
        self.msgboxHandler(["请稍后", "Line正在添加账户，请勿重复点击登录..."])
        logging.info("Driving login")

    def offlinedLoginProcess(self):
        if self.OfflinedUsernameEdit.text() == None:
            self.msgboxHandler(["错误", "用户名不能为空"])
            self.OfflinedUsernameEdit.clear()
        else:
            self.IoController.writeNewUserInformationOfflined(
                self.OfflinedUsernameEdit.text()
            )
            self.msgboxHandler(
                ["成功", "离线用户" + self.OfflinedUsernameEdit.text() + "已添加"]
            )

            self.OfflinedUsernameEdit.clear()

    def crashReport(self, exceptType, exceptValue, traceBack):
        logFilePath = os.getcwd() + "\\Log\\" + "LatestCrash" + ".log"
        errorInfo = str("")
        logging.fatal(
            "Line Minecraft Launcher has CRASHED, Logger will stop working, log wrote successfully"
        )
        for i in traceback.format_exception(exceptType, exceptValue, traceBack):
            errorInfo += i + "\n"
        with open(logFilePath, "w") as f:
            f.write(
                "Line Minecraft Launcher has crashed.\n"
                "Date:" + str(datetime.datetime.now()) + "\n"
                "ExceptType:" + str(exceptType) + "\n"
                "ExceptValue:" + str(exceptValue) + "\n"
                "TraceBack:" + errorInfo + "\n"
            )

        os.startfile(logFilePath)


class LNamingDialog(FramelessDialog, Naming):
    def __init__(self, parent):
        super().__init__()
        self.setupUi(self)
        self.setGeometry(
            (parent.width() - self.width()) // 2 + parent.x(),
            (parent.height() - self.height()) // 2 + parent.y(),
            self.width(),
            self.height(),
        )

    def showDialog(self):
        self.show()


if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    setThemeColor(QColor(108, 95, 154))
    app = QApplication(sys.argv)
    LineMinecraftLauncher = LLineMinecraftLauncher()
    LineMinecraftLauncher.show()
    sys.exit(app.exec_())