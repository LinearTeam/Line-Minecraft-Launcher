import ctypes
import sys
import os
import webbrowser
import requests

rp = os.getcwd() + "\\LineCore"
sys.path.append(rp)
import LineCore.MicrosoftLogin

from qfluentwidgets import MessageBox
from qframelesswindow import StandardTitleBar, AcrylicWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Lfacer.modules.mainw import Ui_Line

class win(AcrylicWindow, Ui_Line):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setTitleBar(StandardTitleBar(self))
        self.listening()
    
    def listening(self):
        background = QPixmap("./Lfacer/resources/background/0.png")
        self.layed.setPixmap(background)
        self.cpa.clicked.connect(lambda: self.processClicked("cpa"))
        self.cpl_4.clicked.connect(lambda: self.processClicked("cpl4"))
        self.cpd.clicked.connect(lambda: self.processClicked("cpd"))
        self.miclog.clicked.connect(lambda: self.processClicked("Nmiclog"))
        self.miclog_2.clicked.connect(lambda: self.processClicked("Nomiclog"))
        self.startbros.clicked.connect(lambda: self.processEvent("LoginatFirst"))
        self.confirmUrl.clicked.connect(lambda: self.processClicked("returnUrl"))
        
    def processClicked(self, who):
        if who == "cpa":
            self.stackedoutwidget.setCurrentIndex(1)
        if who == "cpl4":
            self.stackedoutwidget.setCurrentIndex(0)
        if who == "cpd":    
            self.stackedoutwidget.setCurrentIndex(3)
            requests.get("https://piston-meta.mojang.com/mc/game/version_manifest.json")
        if who == "Nmiclog":
            self.dp.setCurrentIndex(1)
        if who == "Nomiclog":
            self.dp.setCurrentIndex(0)
        if who == "returnUrl":
            loadContent = self.urlInput.text()
            if len(loadContent) == 0:
                opti = MessageBox("失败!", "您没有输入URL", self)
                opti.exec_()
            else:
                try:
                    code = LineCore.MicrosoftLogin.webBroswerLogin(loadContent)
                    opti = MessageBox("稍等...", "账户添加中", self)
                    returnedGroup = LineCore.MicrosoftLogin.resp(code, None)
                    opti = MessageBox("成功!", "账户已添加,请在用户选择栏中选中", self)
                    self.pickuser.addItem(returnedGroup['username'])
                    self.radioOffline.setChecked(False)
                    self.radioMicrosoft.setChecked(True)
                    self.urlInput.setText("")
                    opti.exec_()
                except KeyError:
                    opti = MessageBox("错误!", "无法登录，您可能输入了一个错误的URL!", self)
                    self.urlInput.setText("")
                    opti.exec_()
                finally:
                    opti = MessageBox("错误!", "未知错误发生!", self)
            
    def processEvent(self, what):
        if what == "LoginatFirst":
            url = "https://login.live.com/oauth20_authorize.srf\
            ?client_id=00000000402b5328\
            &response_type=code\
            &scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL\
            &redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
            
            webbrowser.open(url)
            
    
if __name__ == "__main__":
    app = QApplication(sys.argv)
    whnd = ctypes.windll.kernel32.GetConsoleWindow()
    if whnd != 0:
        ctypes.windll.user32.ShowWindow(whnd, 0)
        ctypes.windll.kernel32.CloseHandle(whnd)
    w = win()
    w.show()
    sys.exit(app.exec_())