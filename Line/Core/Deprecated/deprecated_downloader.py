import os
import logging
import hashlib
import requests
import threading

from PyQt5.QtCore import QThread, pyqtSignal
from Core.Download.downloader_ui import Ui_DownloadingInfo
from qframelesswindow import FramelessDialog
from qfluentwidgets import MessageBox


class DownloadWorker:
    def __init__(
        self,
        files_dict,
        progress_callback,
        remove_item_callback,
        update_item_callback,
        complete,
    ):
        self.total_files = len(files_dict)
        self.files_dict = files_dict
        self.success_count = 0
        self.fail_count = 0
        self.lock = threading.Lock()
        self.pause_event = threading.Event()
        self.pause_event.set()  # Initially not paused
        self.is_paused = False
        self.pc = progress_callback
        self.rm = remove_item_callback
        self.uc = update_item_callback
        self.cp = complete

    def download_file(self, path, url, sha1):
        retries = 0
        while retries < 10:
            if not self.pause_event.is_set():
                self.pause_event.wait()  # Wait until resumed

            try:
                if os.path.exists(path):
                    if self.check_sha1(path, sha1):
                        self.update_counts(success=True)
                        return
                    else:
                        os.remove(path)

                os.makedirs(os.path.dirname(path), exist_ok=True)
                self.pc(self.success_count)
                self.uc(url)
                print(
                    f"正在下载: {url}，剩余文件: {self.total_files - (self.success_count + self.fail_count)}"
                )
                response = requests.get(url, stream=True)
                response.raise_for_status()  # Raise error for bad status codes

                with open(path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                if self.check_sha1(path, sha1):
                    self.update_counts(success=True)
                    self.rm(url)
                    return
                else:
                    os.remove(path)  # Remove file if SHA1 check fails
                    print(f"SHA1 校验失败: {path}")

            except Exception as e:
                logging.error(f"下载失败: {path}，错误: {e}")
                print(f"下载失败: {path}，错误: {e}")

            retries += 1

        self.update_counts(success=False)

    def check_sha1(self, file_path, expected_sha1):
        sha1 = hashlib.sha1()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha1.update(chunk)
        return sha1.hexdigest() == expected_sha1

    def update_counts(self, success):
        with self.lock:
            if success:
                self.success_count += 1
            else:
                self.fail_count += 1

    def download_all(self):
        """
        with ThreadPoolExecutor(max_workers=64) as executor:
            futures = {
                executor.submit(self.download_file, path, data['url'], data['sha1']): path
                for path, data in self.files_dict.items()
            }
            for future in as_completed(futures):
                path = futures[future]
                try:
                    future.result()
                except Exception as e:
                    print(f"处理文件 {path} 时发生错误: {e}")

        self.cp(["成功", f"总文件数: {self.total_files}\n成功数: {self.success_count}\n失败数: {self.fail_count}"])
        """

    def resume(self):
        logging.info("Downloading resumed")
        print("恢复下载...")
        self.pause_event.set()  # Resume downloading
        self.is_paused = False

    def pause(self):
        logging.info("Downloading paused")
        print("暂停下载...")
        self.pause_event.clear()  # Pause downloading
        self.is_paused = True


class DownloadThread(QThread):
    CallUpdateProgress = pyqtSignal(int)
    CallUpdateItem = pyqtSignal(str)
    CallDelItem = pyqtSignal(str)
    CallCompleted = pyqtSignal(list)

    def __init__(self, files_dict):
        super().__init__()
        self.files_dict = files_dict

    def run(self):
        self.worker = DownloadWorker(
            self.files_dict,
            self.CallUpdateProgress.emit,
            self.CallDelItem.emit,
            self.CallUpdateItem.emit,
            self.CallCompleted.emit,
        )
        self.worker.download_all()

    def pause(self):
        self.worker.pause()

    def resume(self):
        self.worker.resume()


class WindowSupport(FramelessDialog, Ui_DownloadingInfo):

    def closeEvent(self, event):
        self.d.quit()  # 退出子线程

    def __init__(self, files_dict, parent):
        super().__init__(parent)
        self.setupUi(self)

        self.setGeometry(
            (parent.width() - self.width()) // 2 + parent.x(),
            (parent.height() - self.height()) // 2 + parent.y(),
            self.width(),
            self.height(),
        )

        logging.basicConfig(
            level=logging.DEBUG,
            format="[%(asctime)s][%(filename)s][%(levelname)s]: [%(message)s]",
            filename="LatestModulesLog.log",
            filemode="a",
        )

        self.files_dict = files_dict
        self.DownloadingProgress.setMaximum(len(self.files_dict))
        self.DownloadingProgress.setMinimum(0)

        self.StartAndPause.clicked.connect(self.judge)
        self.d = DownloadThread(self.files_dict)
        self.d.CallUpdateProgress.connect(self.call_progress_update)
        self.d.CallDelItem.connect(self.call_del_item)
        self.d.CallUpdateItem.connect(self.call_add_item)
        self.d.CallCompleted.connect(self.finish)
        self.d.start()

    def finish(self, arg):
        Dialog = MessageBox(arg[0], arg[1], self)
        if Dialog.exec():
            self.close()
        else:
            self.close()

    def judge(self):
        if self.StartAndPause.isChecked() == True:
            self.StartAndPause.setText("开始")
            self.d.pause()
        else:
            self.StartAndPause.setText("终止")
            self.d.resume()

    def call_progress_update(self, i):
        self.DownloadingProgress.setValue(i)
        self.DownloadingPercent.setText(
            str((round(i / len(self.files_dict), 2)) * 100) + "%"
        )

    def call_del_item(self, url):
        for i in range(self.DownloadingItem.model().rowCount()):
            if url == self.DownloadingItem.item(i).text():
                self.DownloadingItem.removeItemWidget(self.DownloadingItem.item(i))

    def call_add_item(self, url):
        self.DownloadingItem.addItem(url)
