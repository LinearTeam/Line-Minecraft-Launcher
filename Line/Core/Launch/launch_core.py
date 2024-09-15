import os
import shutil
import tempfile
import zipfile
import json
import logging

from json import load
from PyQt5.QtCore import QThread, pyqtSignal

WORKING_DIR = (os.getcwd()).replace("\\", "/") + "/Core/Shared/GlobalDirectory.json"


class LLauncher:
    def __init__(
        self,
        McDir: str,
        McVer: str,
        TargetJava: str,
        Username: str,
        Memory: str,
        UserType="Legacy",
        uuid="00000FFFFFFFFFFFFFFFFFFFFFF165C2",
        AccessToken="00000FFFFFFFFFFFFFFFFFFFFFF165C2",
        windows_width="854",
        windows_height="480",
        JVMAdditionalParameters="",
        McAdditionalParameters="",
        extra=False,
    ):
        self.mcDir = McDir
        self.mcVer = McVer
        self.targetJava = TargetJava
        self.username = Username
        self.userType = UserType
        self.uuid = uuid
        self.accessToken = AccessToken
        self.memory = Memory
        self.windowWidth = windows_width
        self.windowHeight = windows_height
        self.JVMAP = JVMAdditionalParameters
        self.McAP = McAdditionalParameters
        self.extra = extra
        with open(WORKING_DIR, "r") as f:
            self.workingDir = json.load(f)["Root"]

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(filename)s][%(levelname)s]: %(message)s",
            filename=(f"{self.workingDir}/Log/LatestLog.log"),
            filemode="a",
        )

    def launch(self):
        classify = self.classifyVersionJson()
        classpath = classify["cp"]
        self.unpress(classify["natives"])

        commandLine = (
            '"' + self.targetJava + '"'
            + " "
            + "-Xmx"
            + self.memory
            + "m -Xmn512m "
            + "-XX:+UseG1GC "
            + "-XX:-UseAdaptiveSizePolicy "
            + "-XX:-OmitStackTraceInFastThrow "
            + "-Dos.name="
            + '"'
            + "Windows 11"
            + '" '
            + "-Dos.version=11.0 -Dorg.lwjgl.util.DebugLoader=true -Dorg.lwjgl.util.Debug=true "
            + "-Dminecraft.launcher.brand=LMC -Dminecraft.launcher.version=LMC_Insider_{version} "  # "-Dlog4j.configurationFile=" + self.McDir + "/versions/" + self.McVer + "/client-1.12.xml " +\
            + "-Djava.library.path="
            + self.mcDir
            + "/versions/"
            + self.mcVer
            + "/"
            + self.mcVer
            + "-natives "  #         "-Dorg.lwjgl.librarypath=" + self.McDir + "/versions/" + self.McVer + "/" + self.McVer + "-natives "+\
            + "-cp "
            + classpath
            + " "
            + classify["mainClass"]
            + " "
            + "--username {name} "
            + "--version "
            + '"'
            + self.mcVer
            + '"'
            + " "
            + "--gameDir "
            + '"'
            + self.mcDir
            + "/versions/"
            + self.mcVer
            + '"'
            + " "
            + "--assetsDir "
            + '"'
            + self.mcDir
            + "/assets"
            + '" '
            + "--assetIndex "
            + classify["index"]
            + " "
            + "--uuid "
            + self.uuid
            + " "
            + "--accessToken "
            + self.accessToken
            + " "
            + "--userType "
            + self.userType
            + " "
            + "--width "
            + self.windowWidth
            + " "
            + "--height "
            + self.windowHeight
        ).format(version="0.0.1", name='"' + self.username + '"')
        commandLine = commandLine.replace("/", "\\")
        with open("./LatestLaunch.bat", "w") as f:
            f.write(commandLine)
        logging.info(f"Startup script has been generated")
        logging.info(commandLine)
        os.system("powershell.exe " + os.getcwd() + "/LatestLaunch.bat")
        logging.info("Startup script executed")

    def classifyVersionJson(self):
        logging.info("Classify Jsons")
        classpath = str()
        natives = []
        with open(
            self.mcDir + "/versions/" + self.mcVer + "/" + self.mcVer + ".json", "r"
        ) as f:
            versionJson = load(f)
        for i in versionJson["libraries"]:
            if "natives" not in i.keys():
                if "rules" in i.keys():
                    for x in i["rules"]:
                        if "os" in x.keys() and "name" in x["os"].keys():
                            if (
                                "windows" in x["os"]["name"]
                                and x["action"] == "disallow"
                            ):
                                break
                            if (
                                "windows" not in x["os"]["name"]
                                and x["action"] == "allow"
                            ):
                                break
                            classpath += (
                                self.mcDir
                                + "/libraries/"
                                + i["downloads"]["artifact"]["path"]
                                + ";"
                            )
                else:
                    classpath += (
                        self.mcDir
                        + "/libraries/"
                        + i["downloads"]["artifact"]["path"]
                        + ";"
                    )
            if (
                "windows" in i["name"]
                and "arm" not in i["name"]
                and "x86" not in i["name"]
            ):
                natives.append(
                    self.mcDir + "/libraries/" + i["downloads"]["artifact"]["path"]
                )
            elif "natives" in i.keys() and "windows" in i["natives"].keys():
                if "rules" in i.keys():
                    for x in i["rules"]:
                        if "os" in x.keys():
                            if "name" in x["os"].keys():
                                if (
                                    x["action"] == "allow"
                                    and "windows" not in x["os"]["name"]
                                ):
                                    continue
                                if (
                                    "windows" not in x["os"]["name"]
                                    and x["action"] == "disallow"
                                ):
                                    natives.append(
                                        self.mcDir
                                        + "/libraries/"
                                        + i["downloads"]["classifiers"][
                                            i["natives"]["windows"]
                                        ]["path"]
                                    )
                else:
                    natives.append(
                        self.mcDir
                        + "/libraries/"
                        + i["downloads"]["classifiers"][i["natives"]["windows"]]["path"]
                    )
        classpath += self.mcDir + "/versions/" + self.mcVer + "/" + self.mcVer + ".jar"
        assetsIndex = versionJson["assets"]
        mainClass = versionJson["mainClass"]
        logging.info("Jsons classification completed")
        logging.info(f"Assets Version: {assetsIndex}, MainClass at {mainClass}")
        return {
            "cp": classpath,
            "natives": natives,
            "index": assetsIndex,
            "mainClass": mainClass,
        }

    def unpress(self, file_paths):
        target_folder = (
            self.mcDir + "/versions/" + self.mcVer + "/" + self.mcVer + "-natives"
        )
        logging.info(f"Natives folder created at {target_folder}")
        # 确保目标文件夹存在
        if not os.path.exists(target_folder):
            os.makedirs(target_folder)
        for file_path in file_paths:
            # 检查文件是否为jar文件
            if file_path.lower().endswith(".jar"):
                try:
                    with zipfile.ZipFile(file_path, "r") as zip_ref:
                        # 创建一个临时目录
                        with tempfile.TemporaryDirectory() as temp_dir:
                            zip_ref.extractall(temp_dir)
                            # 遍历解压后的文件
                            for root, dirs, files in os.walk(temp_dir):
                                for file in files:
                                    if file.lower().endswith(".dll"):
                                        # 构建源文件路径
                                        source_path = os.path.join(root, file)
                                        # 构建目标文件路径
                                        target_path = os.path.join(target_folder, file)
                                        # 移动DLL文件到目标文件夹
                                        shutil.move(source_path, target_path)
                                        logging.info(f"Unpressed {file_path}")
                except Exception as e:
                    logging.info(f"An error occurred during decompression {file_path}")
                    print(f"处理文件时出错: {file_path}. 错误: {e}")


class LMainLaunch(QThread):
    def __init__(
        self,
        mcDir: str,
        mcVer: str,
        targetJava: str,
        username: str,
        memory: str,
        userType="Legacy",
        uuid="00000FFFFFFFFFFFFFFFFFFFFFF165C2",
        accessToken="00000FFFFFFFFFFFFFFFFFFFFFF165C2",
        windowsWidth="854",
        windowsHeight="480",
        jvmAdditionalParameters="",
        mcAdditionalParameters="",
        extra=False,
    ):
        super(LMainLaunch, self).__init__()
        self.mcDir = mcDir
        self.mcVer = mcVer
        self.targetJava = targetJava
        self.username = username
        self.userType = userType
        self.uuid = uuid
        self.accessToken = accessToken
        self.memory = memory
        self.windowWidth = windowsWidth
        self.windowHeight = windowsHeight
        self.jvmAddition = jvmAdditionalParameters
        self.mcAddition = mcAdditionalParameters
        self.extra = extra

    def run(self):
        self.Launcher = LLauncher(
            self.mcDir,
            self.mcVer,
            self.targetJava,
            self.username,
            self.memory,
            self.userType,
            self.uuid,
            self.accessToken,
            self.windowWidth,
            self.windowHeight,
            self.jvmAddition,
            self.mcAddition,
            self.extra,
        )
        self.Launcher.launch()


class LLaunchThread(QThread):

    launched = pyqtSignal(list)

    def __init__(self, arg: dict, online: bool) -> None:
        super().__init__()
        self.launchArgs = arg
        self.online = online

    def run(self):
        if self.online == True:
            if self.launchArgs["extra"] == False:
                self.internalLaunchThread = LLauncher(
                    self.launchArgs["mcDir"],
                    self.launchArgs["mcVer"],
                    self.launchArgs["targetJava"],
                    self.launchArgs["username"],
                    self.launchArgs["memory"],
                    self.launchArgs["userType"],
                    self.launchArgs["uuid"],
                    self.launchArgs["accessToken"],
                )
                self.internalLaunchThread.launch()
            else:
                self.internalLaunchThread = LLauncher(
                    self.launchArgs["mcDir"],
                    self.launchArgs["mcVer"],
                    self.launchArgs["targetJava"],
                    self.launchArgs["username"],
                    self.launchArgs["memory"],
                    self.launchArgs["userType"],
                    self.launchArgs["uuid"],
                    self.launchArgs["accessToken"],
                    self.launchArgs["windowWidth"],
                    self.launchArgs["WindowHeight"],
                    self.launchArgs["jvmAddtionalParameters"],
                    self.launchArgs["mcAddtionalParameters"],
                )
                self.internalLaunchThread.launch()
        else:
            if self.launchArgs["extra"] == False:
                self.internalLaunchThread = LLauncher(
                    self.launchArgs["mcDir"],
                    self.launchArgs["mcVer"],
                    self.launchArgs["targetJava"],
                    self.launchArgs["username"],
                    self.launchArgs["memory"],
                    self.launchArgs["userType"],
                )
                self.internalLaunchThread.launch()
            else:
                self.internalLaunchThread = LLauncher(
                    self.launchArgs["mcDir"],
                    self.launchArgs["mcVer"],
                    self.launchArgs["targetJava"],
                    self.launchArgs["username"],
                    self.launchArgs["memory"],
                    self.launchArgs["userType"],
                    self.launchArgs["windowWidth"],
                    self.launchArgs["windowHeight"],
                    self.launchArgs["jvmAddtionalParameters"],
                    self.launchArgs["mcAddtionalParameters"],
                )
                self.internalLaunchThread.launch()
