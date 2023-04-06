import os
from os.path import exists
from json import loads
from json import dumps
from os import system
from os import remove
import sys#这个函数用于把指定的文件给删掉 
import zipfile
import MicrosoftLogin
import time

#巨多for循环警告
#定义要启动的版本信息
classpath = os.getcwd()
f = open(classpath + "\\userdata\\javaw.txt")
javaw_path = f.read()
f.close()
f = open(classpath + "\\userdata\\mcdir.txt")
mcdir = f.read()
f.close()
f = open(classpath + "\\userdata\\version.txt")
version = f.read()
f.close()
f = open(classpath + "\\userdata\\maxmem.txt")
maxmem = f.read()
f.close()
f = open(classpath + "\\userdata\\usernameg.txt")
username = f.read()
f.close()
javaw_path = javaw_path.replace("\\","\\")
mcdir = mcdir.replace("\\","\\")
print(mcdir)
print(javaw_path)
print(version)
print(maxmem)
print(username)

'''
filename:需要解压的文件名
path:解压到的路径
'''
def unpress(filename: str, path: str):#解压文件
    Zip = zipfile.ZipFile(filename)
    for z in Zip.namelist():
        Zip.extract(z, path)
    Zip.close()

def check(version: str, mcdir: str):#返回是否有这个版本
    print(mcdir + "\\versions\\" + version + "\\" +version + ".json")
    if(exists(mcdir + "\\versions\\" + version + "\\" +version + ".json")):
        return True
    else:
        return False

'''
version:游戏版本
javaw_path:javaw.exe路径
maxmem:最大运行内存
username:用户名
mcdir:Minecraft路径
'''
def online(mcdir: str, version: str, javaw_path: str, maxmem: str):#启动游戏
    #微软登录
    res_auth = MicrosoftLogin.verify()
    if not res_auth == {}:
        username = res_auth["username"]
        uuid = res_auth["uuid"]
        access_token = res_auth["access_token"]
        commandLine = str("")#启动命令
        JVM = str("")#JVM参数
        classpath = str("")#普通库文件路径
        mc_args = str("")#mc参数

        if((not javaw_path == "")\
            and (not version == "")\
            and (not maxmem == "")\
            and (not username == "")\
            and (not mcdir == "")):
            print(mcdir)
            if(check(version, mcdir)):
                version_json = open(mcdir + "\\versions\\" + version + "\\" +version + ".json", "r")
                dic = loads(version_json.read())
                version_json.close()
                #将本地库文件解压至natives文件夹
                for lib in dic['libraries']:
                    if "classifiers" in lib['downloads']:
                        for native in lib['downloads']:#这一步是因为本地库里面有多个库,所以要历遍所有库
                            if native == "artifact":
                                dirct_path = mcdir + "\\versions\\" + version + "\\" + version + "-natives"#解压到的目标路径
                                filepath = mcdir + "\\libraries\\" + lib["downloads"][native]['path']#要解压的artifact库
                                unpress(filepath, dirct_path)
                            elif native == 'classifiers':
                                for n in lib['downloads'][native].values():
                                    dirct_path = mcdir + "\\libraries\\" + lib["downloads"][native]['path']
                                    filepath = mcdir + "\\libraries\\" + n["path"]#classifiers的路径
                                    unpress(filepath, dirct_path)
                JVM = '"'+javaw_path+'" -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy' +\
                ' -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True '+\
                '-Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true '+\
                '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump '+\
                '-Dos.name="Windows 10" -Dos.version=10.0 -Djava.library.path="'+\
                mcdir + "\\versions\\" + version + "\\" + version + "-natives" +\
                '" -Dminecraft.launcher.brand=launcher '+\
                '-Dminecraft.launcher.version=1.0.0 -cp'
                classpath += '"'#-cp以引号开头
                #将普通库文件路径传入-cp参数
                for lib in dic["libraries"]:
                    if not 'classifiers' in lib["downloads"]:
                        normal = mcdir + "\\libraries\\" +lib["downloads"]["artifact"]["path"]#普通库路径
                        classpath += normal + ";"#将普通库路径追加到-cp后面
                #将客户端文件传入-cp参数
                classpath = classpath + mcdir + "\\versions\\" + version + "\\" + version + ".jar" + '"'
                #设置最大运行内存
                JVM = JVM + " " + classpath + " -Xmx" + maxmem + " -Xmn256m -Dlog4j.formatMsgNoLookups=true"
                #最大内存由变量maxmem决定,最小内存是256M

                #配置Minecraft参数
                #将主类传入Minecraft参数
                mc_args += dic["mainClass"] + " "
                for arg in dic["arguments"]["game"]:
                    if isinstance(arg, str):
                        mc_args += arg + " "
                    elif isinstance(arg, dict):#无论是什么，只要是在大括号里括着的，都被python认为是字典类型
                        if isinstance(arg["value"], list):
                            for a in arg["value"]:
                                mc_args += a + " "
                        elif isinstance(arg["value"], str):
                            mc_args += arg["value"] + " "
                #装填数据
                mc_args = mc_args.replace("${auth_player_name}", username)#玩家名称
                mc_args = mc_args.replace("${version_name}", version)#版本名称
                mc_args = mc_args.replace("${game_directory}", mcdir)#mc路径
                mc_args = mc_args.replace("${assets_root}", mcdir + "\\assets")#资源文件路径
                mc_args = mc_args.replace("${assets_index_name}",dic["assetIndex"]["id"])#资源索引文件名称
                mc_args = mc_args.replace("${auth_uuid}", uuid)#由于没有写微软登录,所以uuid为空的
                mc_args = mc_args.replace("${auth_access_token}", access_token)#同上
                mc_args = mc_args.replace("${clientid}", version)#客户端id
                mc_args = mc_args.replace("${auth_xuid}", "{}")#离线登录,不填
                mc_args = mc_args.replace("${user_type}", "mca")#用户类型,离线模式是Legacy
                mc_args = mc_args.replace("${version_type}", dic["type"])#版本类型
                mc_args = mc_args.replace("${resolution_width}", "1000")#窗口宽度
                mc_args = mc_args.replace("${resolution_height}", "800")#窗口高度
                mc_args = mc_args.replace("-demo ", "")#去掉-demo参数，退出试玩版
                #组装命令
                commandLine = JVM + " " + mc_args
                #使用bat的方法运行过长的命令条
                bat = open("run.bat", "w")
                bat.write(commandLine)
                bat.close()
                system("run.bat")
                os.remove("run.bat")
    else:
        print("登陆时遇到了错误,请您检查是否购买了Minecraft或创建了档案")
        print("程序将在3秒后以Mic_acc_unknown退出")
        time.sleep(3)
        sys.exit

def offline(mcdir: str, version: str(), javaw_path: str(), maxmem: str(), username: str()):#启动游戏
    commandLine = str("")#启动命令
    JVM = str("")#JVM参数
    classpath = str("")#普通库文件路径
    mc_args = str("")#mc参数

    if((not javaw_path == "")\
        and (not version == "")\
        and (not maxmem == "")\
        and (not username == "")\
        and (not mcdir == "")):
        print(mcdir)
        if(check(version, mcdir)):
            version_json = open(mcdir + "\\versions\\" + version + "\\" +version + ".json", "r")
            dic = loads(version_json.read())
            version_json.close()
            #将本地库文件解压至natives文件夹
            for lib in dic["libraries"]:
                if "classifiers" in lib['downloads']:
                    for native in lib['downloads']:#这一步是因为本地库里面有多个库,所以要历遍所有库
                        if native == "artifact":
                            dirct_path = mcdir + "\\versions\\" + version + "\\" + version + "-natives"#解压到的目标路径
                            filepath = mcdir + "\\libraries\\" + lib["downloads"][native]['path']#要解压的artifact库
                            unpress(filepath, dirct_path)
                        elif native == 'classifiers':
                            for n in lib['downloads'][native].values():
                                dirct_path = mcdir + "\\versions\\" + version + "\\" + "-natives"
                                filepath = mcdir + "\\libraries\\" + n["path"]#classifiers的路径
                                unpress(filepath, dirct_path)
            JVM = '"'+javaw_path+'" -XX:+UseG1GC -XX:-UseAdaptiveSizePolicy' +\
            ' -XX:-OmitStackTraceInFastThrow -Dfml.ignoreInvalidMinecraftCertificates=True '+\
            '-Dfml.ignorePatchDiscrepancies=True -Dlog4j2.formatMsgNoLookups=true '+\
            '-XX:HeapDumpPath=MojangTricksIntelDriversForPerformance_javaw.exe_minecraft.exe.heapdump '+\
            '-Dos.name="Windows 10" -Dos.version=10.0 -Djava.library.path="'+\
            mcdir + "\\versions\\" + version + "\\" + version + "-natives" +\
             '" -Dminecraft.launcher.brand=line '+\
            '-Dminecraft.launcher.version=1.0.0 -cp'
            classpath += '"'
            #将普通库文件路径传入-cp参数
            for lib in dic["libraries"]:
                if not 'classifiers' in dic["downloads"]:
                    normal = mcdir + "\\libraries\\" +lib["downloads"]["artifact"]["path"] #普通库路径
                    classpath += normal + ";"#将普通库路径追加到-cp后面
            #将客户端文件传入-cp参数
            classpath = classpath + mcdir + "\\versions\\" + version + "\\" + version + ".jar" + '"'
            #设置最大运行内存
            JVM = JVM + " " + classpath + " -Xmx" + maxmem + " -Xmn256m -Dlog4j.formatMsgNoLookups=true"
            #最大内存由变量maxmem决定,最小内存是256M

            #配置Minecraft参数
            #将主类传入Minecraft参数
            mc_args += dic["mainClass"] + " "
            for arg in dic["arguments"]["game"]:
                if isinstance(arg, str):
                    mc_args += arg + " "
                elif isinstance(arg, dict):#无论是什么，只要是在大括号里括着的，都被python认为是字典类型
                    if isinstance(arg["value"], list):
                        for a in arg["value"]:
                            mc_args += a + " "
                    elif isinstance(arg["value"], str):
                        mc_args += arg["value"] + " "
            #装填数据
            mc_args = mc_args.replace("${auth_player_name}", username)#玩家名称
            mc_args = mc_args.replace("${version_name}", version)#版本名称
            mc_args = mc_args.replace("${game_directory}", mcdir)#mc路径
            mc_args = mc_args.replace("${assets_root}", mcdir + "\\assets")#资源文件路径
            mc_args = mc_args.replace("${assets_index_name}",dic["assetIndex"]["id"])#资源索引文件名称
            mc_args = mc_args.replace("${auth_uuid}", "{}")#还没有写微软登录,所以uuid为空
            mc_args = mc_args.replace("${auth_access_token}", "{}")#同上
            mc_args = mc_args.replace("${clientid}", version)#客户端id
            mc_args = mc_args.replace("${auth_xuid}", "{}")#离线登录,不填
            mc_args = mc_args.replace("${user_type}", "Legacy")#用户类型,离线模式是Legacy
            mc_args = mc_args.replace("${version_type}", dic["type"])#版本类型
            mc_args = mc_args.replace("${resolution_width}", "1000")#窗口宽度
            mc_args = mc_args.replace("${resolution_height}", "800")#窗口高度
            mc_args = mc_args.replace("-demo ", "")#去掉-demo参数，退出试玩版
            #拼接命令
            commandLine = JVM + " " + mc_args
            #使用bat的方法运行过长的命令条
            bat = open("run.bat", "w")
            bat.write(commandLine)
            bat.close
            system("run.bat")
            os.remove("run.bat")

f = open(classpath + "\\userdata\\logincategory.txt")
logincategory = f.read()
f.close()
if logincategory == "offline":
    offline(mcdir, version, javaw_path, maxmem, username)
else:
    online(mcdir, version, javaw_path, maxmem)