import threading
import requests

def meta(NotUrl, sh, ClonePath): #主函数，由FileVerifier-LibCreator所提
        threads = []
        print("下载已启动，请勿关闭窗口！")
        for i in range(len(NotUrl)):
                thread = threading.Thread(target=download, args=(NotUrl[i], ClonePath[i]))
                threads.append(thread)
                thread.start() #开启线程
        for thread in threads:
                thread.join()
        print("成功")

def download(NotUrl, ClonePath):
        res = requests.get(NotUrl)
        with open(ClonePath, 'wb') as f:
                f.write(res.content)