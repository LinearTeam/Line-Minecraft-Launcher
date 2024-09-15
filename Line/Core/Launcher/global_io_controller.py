import json
import os


class LGlobalIOController:
    def __init__(self):
        with open(
            (os.getcwd()).replace("\\", "/") + "/Core/Shared/GlobalDirectory.json", "r"
        ) as f:
            workingDir = json.load(f)["Root"]
        self.dataDirectory = workingDir + "/data"

    def writeNewMinecraftDirectory(self, dir, flag) -> None:
        targetJson = self.dataDirectory + "/MinecraftDirectories.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        originalData[flag] = dir
        with open(targetJson, "w") as f:
            json.dump(originalData, f, ensure_ascii=False)

    def writeNewUserInformationMicrosoft(self, content) -> None:
        targetJson = self.dataDirectory + "/Accounts.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        originalData["Microsoft"][content["mcid"]] = {
            "uuid": content["uuid"],
            "skin": content["skin"],
            "accessToken": content["accessToken"],
            "refreshToken": content["refreshToken"],
            "type": content["type"],
            "time": content["time"],
        }
        with open(targetJson, "w") as f:
            json.dump(originalData, f, ensure_ascii=False)

    def readMicrosoftUser(self, user: str) -> dict:
        targetJson = self.dataDirectory + "/Accounts.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        return {
            "uuid": originalData["Microsoft"][user]["uuid"],
            "accessToken": originalData["Microsoft"][user]["accessToken"],
        }

    def readLatestUsername(self) -> str:
        with open(self.dataDirectory + "/LatestLoadedData.json") as f:
            LatestLoadedData = json.load(f)
        try:
            return (
                LatestLoadedData["user"]
                if LatestLoadedData["userType"] == "Microsoft"
                else None
            )
        except:
            return "No Data Loaded"

    def readRefreshToken(self, user) -> str:
        if user == None:
            if self.readLatestUsername(user) != None:
                return self.readRefreshToken(user)
            else:
                return "No Data Loaded"
        elif user != None:
            try:
                with open(self.dataDirectory + "/Accounts.json") as f:
                    UserInformation = json.load(f)
                try:
                    return UserInformation["Microsoft"][user]["refreshToken"]
                except KeyError:
                    return "0"
            except:
                return "No Data Loaded"

    def overwriteToken(self, token: str, user: str) -> None:
        targetJson = self.dataDirectory + "/Accounts.json"
        with open(targetJson, "r") as f:
            originalData = json.load(f)
        originalData["Microsoft"][user]["accessToken"] = token
        with open(targetJson, "w") as f:
            json.dump(originalData, f, ensure_ascii=False)

    def readLatestLoadedData(self) -> dict:
        targetJson = self.dataDirectory + "/LatestLoadedData.json"
        with open(targetJson, "r") as f:
            return json.load(f)

    def writeLoadedData(self, Data: dict) -> None:
        targetJson = self.dataDirectory + "/LatestLoadedData.json"
        with open(targetJson, "w") as f:
            json.dump(Data, f, ensure_ascii=False)

    def writeNewUserInformationOfflined(self, username: str) -> None:
        targetJson = self.dataDirectory + "/Accounts.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        originalData["Offlined"][username] = {"skin": "Steve"}
        with open(targetJson, "w") as f:
            json.dump(originalData, f, ensure_ascii=False)

    def readSavedUsers(self, userType: str) -> list:
        targetJson = self.dataDirectory + "/Accounts.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        if userType == "Microsoft":
            return list(originalData["Microsoft"].keys())
        else:
            return list(originalData["Offlined"].keys())

    def readSavedMinecraftDirectories(self, req: str):
        targetJson = self.dataDirectory + "/MinecraftDirectories.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        if req == "Dict":
            return originalData
        else:
            directories = []
            for i in originalData:
                directories.append(originalData[i])
            return directories

    def removeManagedDir(self, targetKey):
        targetJson = self.dataDirectory + "/MinecraftDirectories.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        del originalData[targetKey]
        with open(targetJson, "w") as f:
            json.dump(originalData, f, ensure_ascii=False)

    def readSettings(self):
        targetJson = self.dataDirectory + "/Settings.json"
        with open(targetJson, "r") as f:
            originalData = json.load(f)
        return originalData

    def overwriteSettings(self, keyword, newValue):
        targetJson = self.dataDirectory + "/Settings.json"
        with open(targetJson, encoding="utf-8") as f:
            originalData = json.load(f)
        originalData[keyword] = newValue
        with open(targetJson, "w") as f:
            json.dump(originalData, f, ensure_ascii=False)
