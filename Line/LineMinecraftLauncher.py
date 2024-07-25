import ctypes
import datetime
import os
import traceback
whnd = ctypes.windll.kernel32.GetConsoleWindow()
if whnd != 0:
    ctypes.windll.user32.ShowWindow(whnd, 0)
    ctypes.windll.kernel32.CloseHandle(whnd)
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Line Minecraft Launcher")

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *

import sys

from Interface.Interface.LineUI import Ui_Form as LineMainUI
from Interface.Interface.Naming import Ui_Naming as Naming

from qframelesswindow import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import MessageBox as MsgBox
from qfluentwidgets import Theme, setThemeColor, RoundMenu, Action

import webbrowser

#from Core import MicrosoftLoginProcessor
from Core import MicrosoftOAuth
from Core import GlobalIOController
from Core import Logger

class LineMinecraftLauncher(AcrylicWindow, LineMainUI):
    
    def closeEvent(self, a0) -> None:
        LoadedData = {
            "Username": self.User if self.User != None else "UNDEFINEDUSER",
            "UserType": "Microsoft" if self.LoginTypeSwitcher.isChecked() == True else "Offlined",
            "MinecraftDirectory": self.MinecraftDirectory,
            "MinecraftVersion": self.LaunchVersion,
            "MemorySize": self.MemoryAdjuster.value(),
        }
        self.IOController.write_loaded_data(LoadedData)
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        sys.excepthook = self.crash_report
        self.Logger = Logger.Logger("LineMinecraftLauncher", "1", False, "./Log/LatestLog.log")
        self.setTitleBar(StandardTitleBar(self))
        self.poper.setCurrentIndex(0)
        self.setWindowTitle("Line Minecraft Launcher")
        Pixmap = QPixmap("./Interface/resources/Background_KeQing.jpg")
        self.Background.setScaledContents(True)
        self.Background.setPixmap(Pixmap)
        
        self.IOController = GlobalIOController.GlobalIOController(None, os.getcwd() + "\\Data")
        self.LatestLoadedData = self.IOController.read_latest_loaded_data()
        self.Logger.Safe("IOController initialized")
        try:
            print(self.LatestLoadedData)
            self.User = self.LatestLoadedData['Username']
            self.MinecraftDirectory = self.LatestLoadedData['MinecraftDirectory']
            self.LaunchVersion = self.LatestLoadedData['MinecraftVersion']
            if self.LatestLoadedData['UserType'] == 'Microsoft':
                self.TokenRefresher = MicrosoftOAuth.MinecraftAuthenticator(self.LatestLoadedData['Username'])
                self.TokenRefresher.finished.connect(self.msgbox_handler)
                self.TokenRefresher.start()
                self.LoginTypeSwitcher.setChecked(True)
                self.LoginTypeSwitcher.setText("微软登录")
        except:
            self.Logger.Warning("One or more of the last loaded data is INVALID")
        
        #预处理
        self.MemoryAdjuster.setMaximum(4096)
        self.MemoryAdjuster.setMinimum(128)
        self.MemoryAdjuster.setSingleStep(1)
        self.MemoryAdjuster.setValue(int(self.LatestLoadedData['MemorySize']))
        self.MemorySizeDisplay.setText(str(self.LatestLoadedData['MemorySize']) + "M")
        self.read_users()

        self.MinecraftPathSelector.addItems(self.IOController.read_saved_minecraft_directories(Req="List"))
        self.MinecraftPathSelector.setCurrentIndex([self.MinecraftPathSelector.itemText(x) for x in range(self.MinecraftPathSelector.count())].index(self.MinecraftDirectory))
        
        self.scan_mc()
        
        #初始化导航栏
        
        self.Navigation.addItem(
            routeKey = "Home",
            icon = FIF.HOME,
            text = "首页",
            onClick=lambda: self.change_page(0)
        )
        self.Navigation.addItem(
            routeKey = "Launch",
            icon = FIF.CHEVRON_RIGHT,
            text = "启动",
            onClick=lambda: self.change_page(1)
        )
        self.Navigation.addItem(
            routeKey = "Account",
            icon = FIF.PEOPLE,
            text = "账户",
            onClick=lambda: self.change_page(2)
        )
        self.Navigation.addItem(
            routeKey = "Terminal",
            icon = FIF.COMMAND_PROMPT,
            text = "终端",
            onClick=lambda: self.change_page(3)
        )
        self.Navigation.addItem(
            routeKey = "Download",
            icon = FIF.DOWNLOAD,
            text = "下载",
            onClick=lambda: self.change_page(4)
        )
        self.Navigation.addItem(
            routeKey = "Settings",
            icon = FIF.SETTING,
            text = "设置",
            onClick=lambda: self.change_page(5)
        )
    
        #事件
        self.AddAccount.clicked.connect(self.drive_login)
        self.Login.clicked.connect(lambda: self.change_page(6))
        self.MicrosoftLogin.clicked.connect(lambda: self.change_page(7))
        self.OfflinedLogin.clicked.connect(lambda: self.change_page(8))
        self.ConfirmUsername.clicked.connect(self.offlined_login_process)
        self.MemoryAdjuster.valueChanged.connect(self.update_memory_label)
        self.AddMinecraftDirectory.clicked.connect(self.add_minecraft_directory)
        self.LoginTypeSwitcher.clicked.connect(self.update_login_type)
        self.LaunchingAccountsSelector.currentIndexChanged.connect(self.update_user)
        self.ManageMinecraft.clicked.connect(self.list_saved_minecraft_directories)
        self.MinecraftDirectoriesManagementView.itemClicked.connect(self.show_selected_directory_details)
        self.OpenManagedMinecraftDircetory.clicked.connect(self.open_managed_minecraft_dircetory)
        self.DelManagedDirectory.clicked.connect(self.remove_managed_directory)
        self.MinecraftPathSelector.currentIndexChanged.connect(self.refresh_mc_dir)

    def refresh_mc_dir(self):
        self.MinecraftDirectory = self.MinecraftPathSelector.currentText()
        self.Logger.Safe("Minecraft Path has been set to: " + self.MinecraftDirectory)
        self.scan_mc()

    def scan_mc(self):
        try:
            self.menu = RoundMenu(parent=self)
            self.menu.addActions([Action(FIF.DOCUMENT, x, triggered = lambda: self.version_selected(x)) for x in os.listdir(self.MinecraftDirectory + "/versions") if os.path.isdir(self.MinecraftDirectory + '/versions/' + x) == True])
            self.Launch.setFlyout(self.menu)
            self.Logger.Safe(("{Count} Version(s) has been found").format(Count = len([x for x in os.listdir(self.MinecraftDirectory + "/versions") if os.path.isdir(self.MinecraftDirectory + '/versions/' + x) == True])))
        except Exception as e:
            #self.msgbox_handler(['错误', "此目录不是Minecraft目录! 程序已将其移除，请重新启动启动器!"])
            self.Logger.Error("This Path is not a correct Minecraft Path")
            self.Logger.Error(str(e))
            self.IOController.read_saved_minecraft_directories(Req="Dict")

            

    def version_selected(self, Version):
        self.Launch.setText("启动: " + Version)
        self.LaunchVersion = Version
        self.Logger.Safe("The version to be started(LaunchVersion) is set to: " + self.LaunchVersion)
        
    def remove_managed_directory(self):
        self.IOController.remove_managed_dir(self.ManagementCustomName.text().replace("自定义名称:", ""))
        self.list_saved_minecraft_directories()
        self.Logger.Warning("A Minecraft Path has been removed, this operation is IRREVERIBLE")
        
    def open_managed_minecraft_dircetory(self):
        os.startfile(os.path.abspath(p := self.MinecraftDirectoryManagement.text().replace("版本路径:   ", "") + "/versions"))
        self.Logger.Safe("System opens a Minecraft Directory in " + p)
        
    def show_selected_directory_details(self, item):
        self.MinecraftDirectoryManagement.setText("版本路径:" + item.text().replace(item.text().split("   ")[0], ""))
        self.ManagementCustomName.setText("自定义名称:" + item.text().split("   ")[0])
        VersionsList = os.listdir(item.text().replace(item.text().split("   ")[0], "").replace("/", "\\").replace("   ", "") + "\\versions")
        self.CurrentMinecraftsView.addItems(VersionsList)
        self.change_page(12)
        
    def list_saved_minecraft_directories(self):
        self.MinecraftDirectoriesManagementView.clear()
        SavedMinecraftDir = self.IOController.read_saved_minecraft_directories(Req="List")
        for i in SavedMinecraftDir:
            self.MinecraftDirectoriesManagementView.addItem(list(i.keys())[0] + "   " + list(i.values())[0])
        self.change_page(11)
        
    def update_user(self):
        self.User = self.LaunchingAccountsSelector.currentText()
        self.Logger.Safe(("User has been set to {User}, he(her) logged by {UserType}").format(User=self.User, UserType = self.LatestLoadedData['UserType']))
        
    def read_users(self):
        try:
            self.LaunchingAccountsSelector.clear()
            SavedUsers = self.IOController.read_saved_users(self.LatestLoadedData['UserType'])
            self.LaunchingAccountsSelector.addItems(SavedUsers)
            self.Logger.Safe("Users loaded")
        except:
            pass
        
    def update_login_type(self):
        if self.LoginTypeSwitcher.isChecked() == True:
            self.LoginTypeSwitcher.setText("微软登录")
            self.LatestLoadedData['UserType'] = "Microsoft"
            self.Logger.Safe("User type has been set to Microsoft")
        else:
            self.LoginTypeSwitcher.setText("离线登录")
            self.LatestLoadedData['UserType'] = "Offlined"
            self.Logger.Safe("User type has been set to Offlined")
        self.read_users()
        
    def add_minecraft_directory(self):
        Directory = QFileDialog.getExistingDirectory(None, "选择Minecraft目录", "C:/")
        if not len(Directory) == 0:
            self.NamingDialogInstance = NamingDialog()
            self.NamingDialogInstance.show_dialog()
            self.NamingDialogInstance.Confirm.clicked.connect(lambda: self.get_custom_name(Directory))
        else:
            self.msgbox_handler(['失败', '未选中'])
            self.Logger.Error("User canceled the operation of adding a path")
            
    def get_custom_name(self, Directory):
        Flag = self.NamingDialogInstance.NameEdit.text()
        self.NamingDialogInstance.close()
        self.MinecraftPathSelector.addItem(Directory)
        self.MinecraftDirectory = Directory
        self.msgbox_handler(['成功!', '目录已添加'])
        self.IOController.write_new_minecraft_directory(Dir = Directory, Flag = Flag)
        self.Logger.Safe(("Called {What}, the directory located at {Where} has been added").foramt(What = Flag, Where = Directory))
        
    def update_memory_label(self):
        self.MemorySizeDisplay.setText(str(self.MemoryAdjuster.value()) + "M")
        self.Logger.Safe("Memory has set to " + str(self.MemoryAdjuster.value()) + "M")
        
    def change_page(self, PageIndex: int):#处理页面切换
        self.poper.setCurrentIndex(PageIndex)
        self.Logger.Safe("Switched to page " + str(PageIndex))
        
    def msgbox_handler(self, Body):#处理自定义的消息窗口
        try:
            msg = MsgBox(Body[0], Body[1], self)
            msg.exec_()
            self.Logger.Safe(("A new dialog rised, the title is {Title}, the Body is {Body}").format(Title = Body[0], Body = Body[1]))
        except Exception as e:
            self.Logger.Error("Faild to rise a dialog, unexception was:"+ '"' + str(e) + '"')
        
    def drive_login(self):#驱动登录
        self.Processor = MicrosoftOAuth.MinecraftAuthenticator("NotFound")
        self.Processor.start()
        self.Processor.finished.connect(self.msgbox_handler)
          
    def offlined_login_process(self):
        if self.Username.text() == None:
            self.msgbox_handler(["错误", "用户名不能为空"])
            self.Username.clear()
            self.Logger.Error("Username cannot be empty")
        elif self.Username.text() == "UNDEFINEDUSER":
            self.msgbox_handler(["错误", '"UNDEFINEDUSER"是保留用户名，不能被使用'])
            self.Logger.Error("A is a reserved username and cannot be used")
            self.Username.clear()
        else:
            self.IOController.write_new_user_information_offlined(self.Username.text())
            self.msgbox_handler(["成功", "离线用户" + self.Username.text() + "已添加"])
            self.Logger.Safe(self.Username.text() + "has added")
            self.Username.clear()
          
    def crash_report(self, ExceptType, ExceptValue, TraceBack):
        LogFilePath = os.getcwd() + "\\Log\\" + "LatestCrash" + ".log"
        self.Logger.Error(("One or more FATAL errors have occurred, the crash report has been written to {FILE}, and the logger will stop working").format(FILE = LogFilePath))
        self.Logger.LOGGER_STOP_WORKING()
        ErrorInfo = str("")
        for i in traceback.format_exception(ExceptType, ExceptValue, TraceBack):
            ErrorInfo += i + "\n"
        with open(LogFilePath, 'w') as f:
            f.write(
                "Line Minecraft Launcher has crashed.\n"
                "Date:" + str(datetime.datetime.now()) + "\n"
                "ExceptType:" + str(ExceptType) + "\n"
                "ExceptValue:" + str(ExceptValue) + "\n"
                "TraceBack:" + ErrorInfo + "\n"
                "Log:" + os.path.abspath(self.Logger.LogFile)
            )

        os.startfile(LogFilePath)

class NamingDialog(FramelessDialog, Naming):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        
    def show_dialog(self):
        self.show()



    
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    setThemeColor(QColor(108, 95, 154))
    app = QApplication(sys.argv)
    LineMinecraftLauncherInstance = LineMinecraftLauncher()
    LineMinecraftLauncherInstance.setWindowIcon(QIcon("./Interface/Icons/LMC.ico"))
    LineMinecraftLauncherInstance.show()
    sys.exit(app.exec_())