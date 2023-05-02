import sys
import os

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from lfacer.modules.mainw import Ui_Line

class win(Ui_Line, QMainWindow):
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
        if loginc == "online":
            pass
        else:
            image = QPixmap(main + "\\lfacer\\resources\\headpic\\steve.png")
            self.headpic.setPixmap(image)
        
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    w = win()
    w.show()
    app.exec_()
