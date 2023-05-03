import sys
import os
import getpass
import webbrowser
import requests
import base64
from json import loads

rp = os.getcwd() + "\\core"
sys.path.append(rp)
import JsonDownloader
import Loader
import MicrosoftLogin

from qframelesswindow import FramelessWindow, StandardTitleBar, AcrylicWindow
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from lfacer.modules.mainw import Ui_Line
from qfluentwidgets import FluentTranslator

class win(Ui_Line, AcrylicWindow):
    
    def verify(self, mcdir, version, javaw_path, maxmem):
        osname = getpass.getuser()
        if not os.path.exists("C:\\Users\\" + osname + "\\linemc"):
            MicrosoftLogin.create(osname)
        #read the status file
        f = open("C:\\Users\\" + osname + "\\linemc\\login\\loginstatus.txt", encoding='utf-8')
        status = f.read()
        f.close()
        #verify
        #can refresh
        if int(status) == 1:
            code = None
            f = open("C:\\Users\\" + osname + "\\linemc\\login\\refreshtoken.txt", encoding='utf-8')
            refreshtoken = f.read()
            f.close()
            return [mcdir, version, javaw_path, maxmem, code, refreshtoken]
        #can't refresh
        else:
            refreshtoken = None
            urlp = "https://login.live.com/oauth20_authorize.srf\
            ?client_id=00000000402b5328\
            &response_type=code\
            &scope=service%3A%3Auser.auth.xboxlive.com%3A%3AMBI_SSL\
            &redirect_uri=https%3A%2F%2Flogin.live.com%2Foauth20_desktop.srf"
            webbrowser.open(urlp)
            re_url = str(input("请输入您位于浏览器顶部重定向后的URL:"))
            begin = re_url.find("code=") + 5
            end = re_url.find("&lc")
            code = str("")
            for kind in range(begin, end):
                code += re_url[kind]#拼接
            return [mcdir, version, javaw_path, maxmem, code, refreshtoken]

    def reload(self):
        main = os.getcwd()
        f = open(main + "\\userdata\\downloadsource.txt", encoding='utf-8')
        downloadsource = f.read()
        f.close()
        main = os.getcwd()
        f = open(main + "\\userdata\\javaw.txt", encoding='utf-8')
        javaw = f.read()
        f.close()
        main = os.getcwd()
        f = open(main + "\\userdata\\logincategory.txt", encoding='utf-8')
        logincategory = f.read()
        f.close()
        main = os.getcwd()
        f = open(main + "\\userdata\\maxmem.txt", encoding='utf-8')
        maxmem = f.read()
        f.close()
        main = os.getcwd()
        f = open(main + "\\userdata\\mcdir.txt", encoding='utf-8')
        mcdir = f.read()
        f.close()
        main = os.getcwd()
        f = open(main + "\\userdata\\usernameg.txt", encoding='utf-8')
        username = f.read()
        f.close()
        main = os.getcwd()
        f = open(main + "\\userdata\\version.txt", encoding='utf-8')
        version = f.read()
        f.close()
        infodist = []
        infodist.append(logincategory) #0
        infodist.append(downloadsource) #1
        infodist.append(javaw) #2
        infodist.append(maxmem) #3
        infodist.append(mcdir) #4
        infodist.append(username) #5
        infodist.append(version) #6
        infodist.append(main) #7
        return infodist
    
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.setTitleBar(StandardTitleBar(self))
        self.titleBar.raise_()
        self.mainstrip()
        
    def mainstrip(self):
        infodist = self.reload()
        self.setWindowTitle("Line Minecraft Launcher")
        
        mcdir = infodist[4]
        javaw = infodist[2]
        maxmem = infodist[3]
        username = infodist[5]
        version = infodist[6]
        loginc = infodist[0]
        dlsource = infodist[1]
        main = infodist[7]
        avlver = os.listdir(mcdir + "\\versions")
        
        for i in avlver:
            self.pickver.addItem(i)
            
        image = QPixmap(main + "\\lfacer\\resources\\background\\" + "0" + ".png")
        self.layed.setPixmap(image)
            
        if loginc == "online":
            info = self.verify(mcdir, version, javaw, maxmem)
            resauth = MicrosoftLogin.resp(info[4], info[5])
            username = resauth['username']
            uuid = resauth['uuid']
            self.usernameinput.setText(username)
            if os.path.exists(main + "\\lfacer\\resources\\headpic\\" + username + ".png"):
                image = QPixmap(main + "\\lfacer\\resources\\headpic\\" + username + ".png")
                self.headpic.setPixmap(image)
            else:
                res = requests.get("https://crafatar.com/avatars/" + uuid + "?size=64")
                f = open(main + "\\lfacer\\resources\\headpic\\" + username + ".png", 'wb')
                f.write(res.content)
                f.close()
                image = QPixmap(main + "\\lfacer\\resources\\headpic\\" + username + ".png")
                self.headpic.setPixmap(image)
        else:
            image = QPixmap(main + "\\lfacer\\resources\\headpic\\steve.png")
            self.headpic.setPixmap(image)
            
        self.pickedpath.setText("当前路径:" + mcdir)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = win()
    w.show()
    app.exec_()
