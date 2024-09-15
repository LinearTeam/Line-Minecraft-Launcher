import ctypes
import os
import subprocess
import time
import json
import logging

WORKING_DIR = (os.getcwd()).replace("\\", "/") + "/Core/Shared/GlobalDirectory.json"


class LJavaScanner:
    def __init__(self, rebuildDatabase=False):
        self.rebuildDatabase = rebuildDatabase
        with open(WORKING_DIR, "r") as f:
            self.workingDir = json.load(f)["Root"]

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(filename)s][%(levelname)s]: %(message)s",
            filename=(f"{self.workingDir}/Log/LatestLog.log"),
            filemode="a",
        )

    def scanJavaPaths(self) -> list:
        # 加载Everything SDK库
        everything = ctypes.WinDLL(
            self.workingDir + "\\Core\\api\\Everything\\Everything64.dll"
        )  # 64位操作系统
        logging.info(
            f"Loaded Everything dll at {self.workingDir}\\Core\\api\\Everything\\Everything64.dll"
        )

        # 定义Everything SDK函数
        everything.Everything_GetResultFullPathNameW.restype = ctypes.c_bool
        everything.Everything_GetResultFullPathNameW.argtypes = [
            ctypes.c_int,
            ctypes.c_wchar_p,
            ctypes.c_int,
        ]
        javaPaths = []
        if self.rebuildDatabase == True:
            logging.info("Rebuilding dataBase")
            everything.Everything_RebuildDB(True)  # 重建数据库
            logging.info("Database rebuilded")
        self.startTime = time.time()
        everything.Everything_SetSearchW("java.exe")  # 设置搜索关键字
        everything.Everything_QueryW(True)  # 执行搜索
        logging.info("Searching executed")

        numResults = everything.Everything_GetNumResults()  # 获取搜索结果数量
        resultBufferSize = 260  # 文件路径缓冲区大小

        for i in range(numResults):
            resultPath = ctypes.create_unicode_buffer(resultBufferSize)
            resultPathSize = ctypes.sizeof(resultPath)

            if everything.Everything_GetResultFullPathNameW(
                i, resultPath, resultPathSize
            ):
                javaPaths.append(resultPath.value)

        return javaPaths

    def getAvailJavas(self):
        javaPaths = [
            x
            for x in self.scanJavaPaths()
            if os.path.basename(x).split(".")[1] == "exe" and os.path.isdir(x) == False
        ]

        availJava = {}

        for java in javaPaths:
            try:
                output = subprocess.check_output(
                    [java, "-version"], stderr=subprocess.STDOUT, text=True
                )
                print(f"{java} is installed and available")
                logging.info(f"{java} is installed and available")
                output = output.split("\n")
                availJava[java] = {
                    "version": output[0],
                    "runtime": output[1],
                    "jvm": output[2],
                }
            except subprocess.CalledProcessError:
                logging.warning(f"{java} is not Available")
            except OSError:
                logging.warning(f"{java} is not Available")

        with open("Info.json", "w") as f:
            json.dump(availJava, f)

        endTime = time.time()

        print(duration := "This query took: " + str(endTime - self.startTime) + "s")
        logging.info(duration)


JS = LJavaScanner()
JS.getAvailJavas()
