import json
import time
import aiohttp
import asyncio
import aiofiles
import hashlib
import os
import logging

WORKING_DIR = (os.getcwd()).replace("\\", "/") + "/Core/Shared/GlobalDirectory.json"


class LAsyncDownloader(object):
    def __init__(self, progressCallback=None, maxConcurrentDownloads=64):
        self.progressCallback = progressCallback
        self.max = maxConcurrentDownloads

        with open(WORKING_DIR, "r") as f:
            self.workingDir = json.load(f)["Root"]

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(filename)s][%(levelname)s]: %(message)s",
            filename=(f"{self.workingDir}/LatestLog.log"),
            filemode="a",
        )

    async def downloadFile(self, session, url, dest, sha1, retries=10):
        while True:
            async with self.semaphore:
                await self.pauseEvent.wait()
                if not os.path.exists(dest):
                    os.makedirs(os.path.dirname(dest), exist_ok=True)
                    for attempt in range(retries):
                        try:
                            await self.pauseEvent.wait()
                            async with session.get(url) as response:
                                if response.status == 200:
                                    await self.pauseEvent.wait()
                                    async with aiofiles.open(dest, "wb") as f:
                                        await self.pauseEvent.wait()
                                        async for (
                                            chunk
                                        ) in response.content.iter_chunked(102400):
                                            # f.write(await response.read())
                                            await f.write(chunk)
                                            await self.pauseEvent.wait()
                                    print(
                                        f"Downloaded: {dest}, {self.totalCounts - self.successfulCounts} remaining"
                                    )
                                    await self.pauseEvent.wait()

                                    # 校验 SHA1
                                    if self.checkSha1(dest, sha1):
                                        print(f"SHA1 match: {dest}")
                                    else:
                                        print(f"SHA1 mismatch for {dest}")
                                    self.successfulCounts += 1
                                    self.progressCallback(self.successfulCounts)
                                    return  # 下载成功，退出
                                else:
                                    print(
                                        f"Failed to download {url}: {response.status}"
                                    )
                        except Exception as e:
                            print(f"Attempt {attempt + 1} failed: {e}")

                        print(f"Retrying {url} ({attempt + 1}/{retries})...")

                    print(f"Failed to download {url} after {retries} attempts.")
                else:
                    if not self.checkSha1(dest, sha1):
                        os.remove(dest)
                        for attempt in range(retries):
                            try:
                                await self.pauseEvent.wait()
                                async with session.get(url) as response:
                                    if response.status == 200:
                                        await self.pauseEvent.wait()
                                        with open(dest, "wb") as f:
                                            await self.pauseEvent.wait()
                                            f.write(await response.read())
                                        await self.pauseEvent.wait()
                                        print(
                                            f"Downloaded: {dest}, {self.totalCounts - self.successfulCounts} remaining"
                                        )
                                        await self.pauseEvent.wait()

                                        # 校验 SHA1
                                        if self.checkSha1(dest, sha1):
                                            print(f"SHA1 match: {dest}")
                                            self.successfulCounts += 1
                                            self.progressCallback(self.successfulCounts)
                                            return  # 下载成功，退出
                                        else:
                                            logging.warning(f"SHA1 mismatch for {dest}")

                                    else:
                                        logging.error(
                                            f"Failed to download {url}: {response.status}"
                                        )
                            except Exception as e:
                                print(f"Attempt {attempt + 1} failed: {e}")

                            print(f"Retrying {url} ({attempt + 1}/{retries})...")

                        print(f"Failed to download {url} after {retries} attempts.")
                    else:
                        self.successfulCounts += 1
                        self.progressCallback(self.successfulCounts)
                        return

    def checkSha1(self, filePath, expectedSha1):
        actual_sha1 = self.calculate_sha1(filePath)
        return actual_sha1 == expectedSha1

    def calculate_sha1(self, filePath):
        sha1 = hashlib.sha1()
        with open(filePath, "rb") as f:
            while chunk := f.read(8192):
                sha1.update(chunk)
        return sha1.hexdigest()

    async def main(self, downloads):
        startTime = time.time()
        self.totalCounts = len(downloads)
        self.successfulCounts = 0
        self.pauseEvent = asyncio.Event()
        self.pauseEvent.set()

        self.semaphore = asyncio.Semaphore(self.max)

        async with aiohttp.ClientSession() as session:
            tasks = []
            for dest, url, expectedSha1 in downloads:
                tasks.append(self.downloadFile(session, url, dest, expectedSha1))

            await asyncio.gather(*tasks)

        endTime = time.time()
        print(f"{str(endTime-startTime)}s")

    def pause(self):
        self.pauseEvent.clear()

    def resume(self):
        self.pauseEvent.set()

    def shutdown(self):
        self.pause()
        try:
            loop = asyncio.get_running_loop()
            tasks = asyncio.all_tasks(loop)
            for task in tasks:
                task.cancel()
        except Exception:
            pass


def formatData(total: dict):
    paths = []
    urls = []
    sha1s = []

    for path in total.keys():
        paths.append(path)
        urls.append(total[path]["url"])
        sha1s.append(total[path]["sha1"])

    common = []
    for i in range(len(paths)):
        common.append(tuple((paths[i], urls[i], sha1s[i])))  # dict -> list[tuple]
    return common
