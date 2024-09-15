from json import dump, load
import os
import requests


class LParsingJsons:
    def __init__(self, mcDir, mcVer, url, customName, src="Mojang"):
        self.mcDir = mcDir
        self.mcVer = mcVer
        self.parsedFiles = {}
        self.src = src
        self.url = url
        self.customName = customName

    def download_version_json(self):
        try:
            filePath = (
                self.mcDir
                + "/versions/"
                + self.customName
                + "/"
                + self.customName
                + ".json"
            )
            os.makedirs(os.path.dirname(filePath), exist_ok=True)
            response = requests.get(self.url, stream=True)
            response.raise_for_status()  # 确保请求成功

            # 保存文件
            while True:
                with open(filePath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)

                with open(filePath, "r") as f:
                    originalData = load(f)
                originalData["id"] = self.customName
                with open(filePath, "w") as f:
                    dump(originalData, f)

                with open(
                    self.mcDir
                    + "/versions/"
                    + self.customName
                    + "/"
                    + self.customName
                    + ".json",
                    "r",
                ) as f:
                    versionJson = load(f)
                url = versionJson["assetIndex"]["url"]
                filePath = (
                    self.mcDir
                    + "/assets/indexes/"
                    + versionJson["assetIndex"]["id"]
                    + ".json"
                )
                os.makedirs(os.path.dirname(filePath), exist_ok=True)

                response = requests.get(url, stream=True)
                response.raise_for_status()  # 确保请求成功

                # 保存文件
                with open(filePath, "wb") as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                break

            return self.parsingVersionJson()
        except Exception as e:
            print(f"下载失败: {filePath}, 错误: {e}")

    def parsingVersionJson(self):
        natives = []
        with open(
            self.mcDir
            + "/versions/"
            + self.customName
            + "/"
            + self.customName
            + ".json",
            "r",
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
                            self.parsedFiles[
                                self.mcDir
                                + "/libraries/"
                                + i["downloads"]["artifact"]["path"]
                            ] = {
                                "url": i["downloads"]["artifact"]["url"],
                                "sha1": i["downloads"]["artifact"]["sha1"],
                            }
                else:
                    self.parsedFiles[
                        self.mcDir + "/libraries/" + i["downloads"]["artifact"]["path"]
                    ] = {
                        "url": i["downloads"]["artifact"]["url"],
                        "sha1": i["downloads"]["artifact"]["sha1"],
                    }
            if (
                "windows" in i["name"]
                and "arm" not in i["name"]
                and "x86" not in i["name"]
            ):
                natives.append(
                    self.mcDir
                    + "/libraries/"
                    + i["downloads"]["artifact"]["path"]
                    + ";"
                    + i["downloads"]["artifact"]["url"]
                    + ";"
                    + i["downloads"]["artifact"]["sha1"]
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
                                        + ";"
                                        + i["downloads"]["classifiers"][
                                            i["natives"]["windows"]
                                        ]["url"]
                                        + ";"
                                        + i["downloads"]["classifiers"][
                                            i["natives"]["windows"]
                                        ]["sha1"]
                                    )
                else:
                    natives.append(
                        self.mcDir
                        + "/libraries/"
                        + i["downloads"]["classifiers"][i["natives"]["windows"]]["path"]
                        + ";"
                        + i["downloads"]["classifiers"][i["natives"]["windows"]]["url"]
                        + ";"
                        + i["downloads"]["classifiers"][i["natives"]["windows"]]["sha1"]
                    )
        natives = list(filter(None, natives))

        self.organizedNatives = {}
        for i in natives:
            term = i.split(";")
            self.organizedNatives[term[0]] = {"url": term[1], "sha1": term[2]}

        self.total = {}
        self.total.update(self.parsedFiles)
        self.total.update(self.organizedNatives)
        try:
            self.total.update(
                {
                    self.mcDir
                    + "/versions/"
                    + self.customName
                    + "/"
                    + self.customName
                    + ".jar": {
                        "url": (
                            versionJson["downloads"]["client"]["url"]
                            if self.src == "Mojang"
                            else "https://bmclapi2.bangbang93.com"
                            + "/"
                            + "version/"
                            + self.mcVer
                            + "/client"
                        ),
                        "sha1": versionJson["downloads"]["client"]["sha1"],
                    },
                    self.mcDir
                    + "/versions/"
                    + self.customName
                    + "/"
                    + versionJson["logging"]["client"]["file"]["id"]: {
                        "url": versionJson["logging"]["client"]["file"]["url"],
                        "sha1": versionJson["logging"]["client"]["file"]["sha1"],
                    },
                }
            )
        except:
            self.total.update(
                {
                    self.mcDir
                    + "/versions/"
                    + self.customName
                    + "/"
                    + self.customName
                    + ".jar": {
                        "url": (
                            versionJson["downloads"]["client"]["url"]
                            if self.src == "Mojang"
                            else "https://bmclapi2.bangbang93.com"
                            + "/"
                            + "version/"
                            + self.mcVer
                            + "/client"
                        ),
                        "sha1": versionJson["downloads"]["client"]["sha1"],
                    }
                }
            )
        if self.src == "BMCLAPI":
            host = "https://bmclapi2.bangbang93.com"
            for i in self.total.values():
                i["url"] = i["url"].replace(
                    "https://libraries.minecraft.net", host + "/maven"
                )
                i["url"] = i["url"].replace("https://piston-meta.mojang.com", host)
            self.total = self.total
        else:
            self.total = self.total

        with open(
            self.mcDir + "/assets/indexes/" + versionJson["assetIndex"]["id"] + ".json",
            "r",
        ) as f:
            assetsJson = load(f)
        assets = {}
        for i in assetsJson.values():
            try:
                for x in i.values():
                    assets[
                        self.mcDir + "/assets/objects/" + x["hash"][0:2] + "/" + x["hash"]
                    ] = {
                        "url": (
                            "https://resources.download.minecraft.net/"
                            + x["hash"][0:2]
                            + "/"
                            + x["hash"]
                            if self.src == "Mojang"
                            else host + "/assets" + "/" + x["hash"][0:2] + "/" + x["hash"]
                        ),
                        "sha1": x["hash"],
                    }
                self.total.update(assets)
            except:
                pass
        with open(os.getcwd() + "\\Core\\api\\Rust\\downloads.json", "w") as f:
            dump(self.total, f)
        print(self.total)
        return self.total
