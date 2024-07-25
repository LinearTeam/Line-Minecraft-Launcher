import os
import requests
import threading
import json


def json_analyze(mcdir, ver, download_source):
    with open(
        mcdir + "/versions/" + ver + "/" + ver + ".json", 'r', encoding='utf-8'
    ) as f:
        ver_json = f.read()

    ver_json = json.loads(ver_json)

    key_libraries = ver_json['libraries']

    paths = []
    urls = []

    for i in key_libraries:
        key_downloads = i['downloads']

        if "classifiers" in key_downloads:
            if "natives-windows" in key_downloads['classifiers']:
                if "artifact" in key_downloads:
                    key_windows = key_downloads['classifiers']['natives-windows']

                    path = key_windows['path']
                    path = path.replace("/", "\\")
                    path = mcdir + "\\libraries\\" + path
                    paths.append(path)

                    url = key_windows['url']
                    urls.append(url)

                    pathart = mcdir + "/libraries/" + \
                        key_downloads['artifact']['path']
                    pathart = path.replace("/", "\\")
                    paths.append(pathart)

                    urlart = key_downloads['artifact']['url']
                    urls.append(urlart)
        return [urls, paths]

    if download_source == "BMCLAPI":
        ex_urls = urls
        urls = []

        for i in ex_urls:
            i = i.replace("https://libraries.minecraft.net/",
                          "https://bmclapi2.bangbang93.com/maven/")
            urls.append(i)
    else:
        pass

    key_client_url = ver_json['downloads']['client']['url']

    if download_source == "BMCLAPI":
        new_url = "https://bmclapi2.bangbang93.com/version/" + ver + "/client"
        urls.append(new_url)
    else:
        urls.append(key_client_url)

    paths.append((mcdir + "\\versions\\" + ver +
                 "\\").replace("/", "\\") + ver + ".jar")

    return [urls, paths]


def library_creator(mcdir, ver, download_source):
    urls_and_paths = json_analyze(mcdir, ver, download_source)
    paths = urls_and_paths[1]
    for i in paths:
        directory = os.path.dirname(i)
        os.makedirs(directory, exist_ok=True)
    total_info = download(urls_and_paths[0], paths)
    return total_info


class work():
    success = 0
    failed = 0
    failed_detail = []

    def work_function(
        self,
        url,
        path
    ):
        try:

            header = {
                "user-agent": "Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1 Edg/109.0.0.0"
            }

            response = requests.get(url, headers=header)

            with open(
                path,
                'wb'
            ) as f:
                f.write(response.content)

            print("echo:" + f"下载完成: {url}")
            self.success += 1

        except Exception as e:

            self.failed += 1
            self.failed_detail.append(url + " 错误信息 " + str(e))

    def total(self):
        total_args = {
            "success": str(self.success),
            "failed": str(self.failed),
            "details": self.failed_detail
        }
        return total_args


def download(urls, paths):
    threads = []

    relize = work()

    for url, path in zip(urls, paths):
        thread = threading.Thread(
            target=relize.work_function, args=(url, path))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    total_info = relize.total()
    return total_info
