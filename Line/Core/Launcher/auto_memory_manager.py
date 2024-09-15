import time
import psutil
import sys
import os
import math

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtCore import QThread, pyqtSignal


class LSubmitMemory(QThread):
    submittedMemory = pyqtSignal(int)

    def __init__(self, interval=10):
        super().__init__()
        self.interval = interval
        self.stop = False

    def run(self):
        while True:
            if self.stop == False:
                self.submittedMemory.emit(
                    math.floor((psutil.virtual_memory().free / 1024 / 1024) * 0.66)
                )
                time.sleep(self.interval)
            else:
                break

    def pause(self):
        self.stop = True
