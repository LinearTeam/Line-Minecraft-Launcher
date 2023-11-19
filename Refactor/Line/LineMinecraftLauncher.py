import ctypes
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

from qframelesswindow import *
from qfluentwidgets import FluentIcon as FIF
from qfluentwidgets import MessageBox as MsgBox

import webbrowser

from Core import MicrosoftLoginProcessor
from Core import GlobalIOController

class LineMinecraftLauncher(FramelessWindow, LineMainUI):
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        sys.excepthook = self.crash_report
        self.setTitleBar(StandardTitleBar(self))
        self.poper.setCurrentIndex(0)
        self.setWindowTitle("Line Minecraft Launcher")
        self.TokenRefresher = MicrosoftLoginProcessor.MultiThreadTokenRefresher(None)
        self.TokenRefresher.AccessToken.connect(self.receive_token)
        self.TokenRefresher.start()
        
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
        self.AddAccount.clicked.connect(self.microsoft_login_process)
        self.Login.clicked.connect(lambda: self.change_page(6))
        self.MicrosoftLogin.clicked.connect(lambda: self.change_page(7))
        self.VerifyRedirectedUrl.clicked.connect(self.drive_login)
        
    def change_page(self, PageIndex: int):#处理页面切换
        self.poper.setCurrentIndex(PageIndex)
        
    def msgbox_handler(self, Body):#处理自定义的消息窗口
        try:
            msg = MsgBox(Body[0], Body[1], self)
            msg.exec_()
        except:
            pass
        
    def microsoft_login_process(self):#处理微软登录
        url = "https://login.live.com/oauth20_authorize.srf\
            ?client_id=00000000402b5328\
            &response_type=code\
            &scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL\
            &redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
            
        webbrowser.open(url)
        
    def drive_login(self):#驱动登录
        
        RedirectedUrlText = self.RedirectedUrl.text() #获取重定向的url
        try:
            if len(RedirectedUrlText) != 0:
                begin = RedirectedUrlText.find("code=") + 5
                end = RedirectedUrlText.find("&lc")
                code = str("")
            
                for stage in range(begin, end):
                    code += RedirectedUrlText[stage] #提取code
                    
                self.Handler = MicrosoftLoginProcessor.MultiThreadMicrosoftLoginHandler(code, None) #实例化登录处理器
                self.Handler.finished.connect(self.msgbox_handler) #当finished槽信号被emit时， 处理返回结果
                self.Handler.start() #启动线程
                self.RedirectedUrl.clear()
            else:
                self.msgbox_handler(["错误", "登录时遇到错误，请检查URL是否正确或网络是否可用"])
                self.RedirectedUrl.clear()
        except:
            self.msgbox_handler(["错误", "登录时遇到错误，请检查URL是否正确或网络是否可用"])
            self.RedirectedUrl.clear()
          
    def crash_report(self, ExceptType, ExceptValue, TraceBack):
        LogFilePath = os.getcwd() + "\\Log\\" + "LatestCrash" + ".log"
        ErrorInfo = str("")
        for i in traceback.format_exception(ExceptType, ExceptValue, TraceBack):
            ErrorInfo += i + "\n"
        with open(LogFilePath, 'w') as f:
            f.write(
                "Line Minecraft Launcher has crashed.\n"
                "ExceptType:" + str(ExceptType) + "\n"
                "ExceptValue:" + str(ExceptValue) + "\n"
                "TraceBack:" + ErrorInfo
            )
        os.startfile(LogFilePath)
        
    def receive_token(self, AccessToken):
        print(AccessToken)
        
    
if __name__ == "__main__":
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    app = QApplication(sys.argv)
    LineMinecraftLauncherInstance = LineMinecraftLauncher()
    LineMinecraftLauncherInstance.setWindowIcon(QIcon("./Interface/Icons/LMC.ico"))
    LineMinecraftLauncherInstance.show()
    sys.exit(app.exec_())