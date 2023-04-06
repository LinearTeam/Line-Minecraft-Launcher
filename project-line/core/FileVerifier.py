import os
import json
import httpx

def download(NotUrl, sh):
    #多线程下载未完
    print(NotUrl)

def Verify(transformedpath, ur, sh):
    main_path = os.getcwd()
    ProcessItem = 0
    NotUrl = []
    NotPath = []
    for i in transformedpath:
        pci = main_path + "\\" + str(transformedpath[ProcessItem])
        if not os.path.exists(pci):
            NotPath.append(pci)
            NotUrl.append(ur[ProcessItem])
            ProcessItem = int(ProcessItem) + 1
        else:
            ProcessItem = int(ProcessItem) + 1
    download(NotUrl, sh)

def Main():
    main_path = os.getcwd()
    f = open(main_path + "\\userdata\\mcdir.txt")
    mcdir = f.read()
    f.close()
    f = open(main_path + "\\userdata\\version.txt")
    version = f.read()
    f.close()
    print(mcdir)
    print(version)
    version_json = open(mcdir + "\\versions\\" + version + "\\" +version + ".json", "r")
    dic = json.loads(version_json.read())
    version_json.close()
    lib = dic['libraries']
    ProcessNumber = 0
    ur = []
    vp = []
    sh = []
    #警告!,从这里开始,[巨多for循环警告!]
    for i in lib:
        ProcessItem = lib[ProcessNumber]
        ProcessDownloads = ProcessItem['downloads']
        ProcessArtifact = ProcessDownloads['artifact']
        VerifyPath = ProcessArtifact['path']
        VerifySha1 = ProcessArtifact['sha1']
        VerifyUrl = ProcessArtifact['url']
        ur.append(VerifyUrl)
        sh.append(VerifySha1)
        vp.append(VerifyPath)
        ProcessNumber = int(ProcessNumber) + 1
    ProcessNumber = 0
    transformedpath = []
    for i in vp:
         v = vp[ProcessNumber]
         v = str(v).replace("/", "\\")
         transformedpath.append(v)
         ProcessNumber = int(ProcessNumber) + 1
    Verify(sh, transformedpath, ur)
Main()