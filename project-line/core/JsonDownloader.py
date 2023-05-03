import sys
import time
from requests import get
import requests
import os
import FileVerifier

def scot(downloadsource, mcdir):
    download_version = input("请输入您要下载的版本:").split()
    print ("启动器正在为您下载文件,稍后......")
    print(downloadsource)
    url = downloadsource + "version/" + download_version[0] + "/json"
    res = requests.get(url)
    content = res.text
    print("文件枝叶建立中.......")
    os.mkdir(mcdir + "\\versions\\" + download_version[0])
    print(mcdir + "\\versions\\" + download_version[0] + "\\" + str(download_version[0]) + ".json")
    f = open(mcdir + "\\versions\\" + download_version[0] + "\\" + str(download_version[0]) + '.json','w')
    f.write(content)
    print ("完成!系统将在3秒开始文件校验")
    print ("若想修改下载器设置,请使用Line Operater")
    f.close
    time.sleep(3)
    #pyp = sys.path
    #os.system(pyp[4] + "\\python.exe" + ' ' + main_path + "\\core\\FileVerifier.py")
    FileVerifier.enter(download_version[0], mcdir)

def create(mcdir):
    os.mkdir(mcdir + "\\" + "versions")

def main(downloadsource, mcdir):
    if not os.path.exists(mcdir + "\\versions"):
        create(mcdir)
        scot(downloadsource, mcdir)
    else:
        scot(downloadsource, mcdir)