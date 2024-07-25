import ctypes
import os
import subprocess
import time
import Logger
import json

class JavaScanner:
    def __init__(self, RebuildDatabase=False):
        self.RebuildDatabase = RebuildDatabase

    def scan_java_paths(self) -> list:
        # 加载Everything SDK库
        everything_dll = ctypes.WinDLL('./Dependences/Everything/Everything64.dll')  # 64位操作系统

        self.Logger = Logger.Logger("LineMinecraftLauncher", "1", False, "../Log/LatestLog.log") #日志记录
        self.Logger.Safe("The following information logged by Java Scanner")

        # 定义Everything SDK函数
        everything_dll.Everything_GetResultFullPathNameW.restype = ctypes.c_bool
        everything_dll.Everything_GetResultFullPathNameW.argtypes = [ctypes.c_int, ctypes.c_wchar_p, ctypes.c_int]
        java_paths = []
        if self.RebuildDatabase == True:
            everything_dll.Everything_RebuildDB(True) #重建数据库
            self.Logger.Safe("Database rebuilded")
        else:
            self.Logger.Safe("Database will not rebuild")
        self.start = time.time()
        everything_dll.Everything_SetSearchW("java.exe")  # 设置搜索关键字
        everything_dll.Everything_QueryW(True)  # 执行搜索
        self.Logger.Safe("Searching executed")
        
        num_results = everything_dll.Everything_GetNumResults()  # 获取搜索结果数量
        result_buffer_size = 260  # 文件路径缓冲区大小

        for i in range(num_results):
            result_path = ctypes.create_unicode_buffer(result_buffer_size)
            result_path_size = ctypes.sizeof(result_path)

            if everything_dll.Everything_GetResultFullPathNameW(i, result_path, result_path_size):
                java_paths.append(result_path.value)
        
        return java_paths


    def get_avail_javas(self):
        java_paths = [x for x in self.scan_java_paths() if os.path.basename(x).split(".")[1] == "exe" and os.path.isdir(x) == False]

        avail_java = {}

        for java in java_paths:
            try:
                output = subprocess.check_output([java, "-version"], stderr=subprocess.STDOUT, text=True)
                print(f"{java} is installed and available")
                self.Logger.Safe(f"{java} is installed and available")
                output = output.split("\n")
                avail_java[java] = {
                    "Version": output[0],
                    "Runtime": output[1],
                    "JVM": output[2]
                }
            except subprocess.CalledProcessError:
                self.Logger.Error(f"{java} is not availiable")
            except OSError:
                self.Logger.Error(f"{java} is not availiable")

        with open("Info.json", 'w') as f:
            json.dump(avail_java, f)

        end = time.time()

        print(t := "This query took: " + str(end - self.start) + "s")
        self.Logger.Safe(t)

JS = JavaScanner()
JS.get_avail_javas()