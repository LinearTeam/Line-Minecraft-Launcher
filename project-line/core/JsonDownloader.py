import sys
import time
from requests import get
import requests
import os

def scot():
    main_path = os.getcwd()
    download_version = input("请输入您要下载的版本:").split()
    print ("启动器正在为您下载文件,稍后......")
    print(downloadsource)
    url = downloadsource + "version/" + download_version[0] + "/json"
    res = requests.get(url)
    content = res.text
    print("文件枝叶建立中.......")
    os.mkdir(main_path + "\\.minecraft\\versions\\" + download_version[0])
    print(main_path + "\\.minecraft\\versions\\" + download_version[0] + "\\" + str(download_version[0]) + ".json")
    f = open(main_path + "\\.minecraft\\versions\\" + download_version[0] + "\\" + str(download_version[0]) + '.json','w')
    f.write(content)
    print ("完成!系统将在3秒开始文件校验")
    print ("若想修改下载器设置,请使用Line Operater")
    f.close
    time.sleep(3)
    os.system("填入你的python路径(后续会写自动获取)" + ' ' + main_path + "\\core\\FileVerifier.py")
    sys.exit()

def create():
    main_path = os.getcwd()
    os.mkdir(main_path + "\\.minecraft\\" + "versions")
    scot()
main_path = os.getcwd()
f = open(main_path + "\\userdata\\downloadsource.txt")
downloadsource = f.read()
f.close
if not os.path.exists(main_path + "\\.minecraft\\versions"):
    os.mkdir(main_path + "\\.minecraft\\versions")
    scot()
else:
    scot()
#A
