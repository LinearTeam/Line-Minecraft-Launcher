import os
import json
import downloader

def LibCreator(NotPath, sh, NotUrl): #libraries文件夹枝叶建立
    des = [] #需要去除的部分（os.makedirs不可创建文件，只可创建文件夹多级目录）
    pi = 0 #处理项数
    for i in NotPath:       #提取详细内容到des列表中
        content = os.path.basename(NotPath[pi])
        des.append(content)
        pi = pi + 1
    pi = 0 #归零
    ClonePath = NotPath #复制一份NotPath，用于文件创建（ClonePath用于文件写入）
    NotPath = [] #使NotPath归零
    for i in ClonePath:
        cont = "\\" + des[pi]
        new = ClonePath[pi].replace(cont, '')
        NotPath.append(new)
        pi = pi + 1  #去除掉需要去除的部分
    pi = 0
    for i in NotPath:
        os.makedirs(NotPath[pi], exist_ok=True) #创建多级文件夹，exist_ok用于隐藏文件已存在错误
        pi = pi + 1
    downloader.meta(NotUrl, sh, ClonePath) #调用下载主函数meta，详见downloader.py
    
    
def Main():
    main_path = os.getcwd()#获取主路径
    f = open(main_path + "\\publicpath.txt")
    main_path = f.read()
    f.close()
    f = open(main_path + "\\userdata\\mcdir.txt")
    mcdir = f.read()
    f.close()
    f = open(main_path + "\\userdata\\version.txt")
    version = f.read()
    f.close() #获取启动游戏版本以及其路径
    version_json = open(mcdir + "\\versions\\" + version + "\\" + version + ".json", "r")
    dic = json.loads(version_json.read())
    version_json.close() #将版本json转换为Python Dictionary
    lib = dic['libraries']
    ProcessNumber = 0
    #创建空列表
    ur = [] #对应键url
    vp = [] #对应键path
    sh = [] #对应键sha1
    #提取url, path, sha1等键
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
    #将path的/斜杠转换为\斜杠，以便windows检查文件是否存在
    ProcessNumber = 0
    transformedpath = []
    for i in vp:
         v = vp[ProcessNumber]
         v = str(v).replace("/", "\\")
         transformedpath.append(v)
         ProcessNumber = int(ProcessNumber) + 1
    #提取不存在文件的路径及其url
    ProcessItem = 0
    #创建空列表
    NotUrl = [] #对应url
    NotPath = [] #对应path
    for i in transformedpath:
        pci = main_path + "\\" + ".minecraft\\libraries\\" + str(transformedpath[ProcessItem])
        if not os.path.exists(pci):
            NotPath.append(pci)
            NotUrl.append(ur[ProcessItem])
            ProcessItem = int(ProcessItem) + 1
        else:
            ProcessItem = int(ProcessItem) + 1
    LibCreator(NotPath, sh, NotUrl) #前往文件创建
    #将数据传递到download函数
Main()