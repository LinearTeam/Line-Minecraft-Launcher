import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime
import logging
import Core.Launcher.global_io_controller as global_io_controller

from requests import post, get
from json import dumps, loads, load
from PyQt5.QtCore import QThread
from Core.Auth.local_server_provider import startServer
from PyQt5.QtCore import pyqtSignal

WORKING_DIR = (os.getcwd()).replace("\\", "/") + "/Core/Shared/GlobalDirectory.json"


class LMicrosoftOAuthenticator:
    def __init__(self, refreshToken: str = 0):
        self.refreshToken = refreshToken
        with open(WORKING_DIR, "r") as f:
            self.WorkingDir = load(f)["Root"]

        logging.basicConfig(
            level=logging.INFO,
            format="[%(asctime)s][%(filename)s][%(levelname)s]: %(message)s",
            filename=(f"{self.WorkingDir}/Log/LatestLog.log"),
            filemode="a",
        )

    def auth(self):
        if self.refreshToken == "0":
            try:
                self.getAccessToken()
                return ["成功", "账户{0}已添加".format(self.__UserInformation["mcid"])]
            except Exception as e:
                return [
                    "失败",
                    "无法获取到Minecraft档案信息，请排除: \n 1.网络连接错误 \n 2.未购买Minecraft Java \n 3.已购买游戏，但未注册档案",
                ]
        else:
            try:
                self.refreshAccessToken()
                return [
                    "提示",
                    "用户{0}的Access Token已刷新".format(
                        self.__UserInformation["mcid"]
                    ),
                    "windows",
                ]
            except Exception as e:
                return [
                    "错误",
                    "无法刷新令牌，请检查你的网络连接。\n错误信息:" + str(e),
                    "windows",
                ]

    def refreshAccessToken(self):  # Step #0
        logging.info(f"Refreshing token")
        self.url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

        self.header = {"Content-Type": "application/x-www-form-urlencoded"}

        self.__data = {
            "client_id": "1cbfda79-fc84-47f9-8110-f924da9841ec",
            "scope": "XboxLive.signin offline_access",
            "refresh_token": self.refreshToken,
            "redirect_uri": "http://127.0.0.1:40935",
            "grant_type": "refresh_token",
        }

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)
        self.__newRefreshToken = self.__dic["refresh_token"]
        self.__accessToken = self.__dic["access_token"]
        self.xboxLiveVerification()

    def getAccessToken(self):  # Step 1

        logging.info("Getting access token")

        code = startServer()

        self.url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

        self.header = {"Content-Type": "application/x-www-form-urlencoded"}

        self.__data = {
            "client_id": "1cbfda79-fc84-47f9-8110-f924da9841ec",
            "scope": "XboxLive.signin offline_access",
            "code": code,
            "redirect_uri": "http://127.0.0.1:40935",
            "grant_type": "authorization_code",
        }

        del code

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)
        self.__accessToken = self.__dic["access_token"]
        self.__newRefreshToken = self.__dic[
            "refresh_token"
        ]  # By the way, get the refresh token
        self.xboxLiveVerification()

        # Microsoft OAuth Passed

    def xboxLiveVerification(self):  # Step2

        logging.info("Passing Xbox Live verification")

        self.url = "https://user.auth.xboxlive.com/user/authenticate"

        self.header = {"Content-Type": "application/json", "Accept": "application/json"}

        self.__data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d=" + self.__accessToken,
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        }
        self.__data = dumps(self.__data)

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)

        self.__XboxLiveToken = self.__dic["Token"]

        self.__uhs = str()
        for i in self.__dic["DisplayClaims"]["xui"]:
            self.__uhs = i["uhs"]

        self.getXstsToken()

        # XBL Passed

    def getXstsToken(self):  # Step 3

        logging.info("Getting XSTS Token")

        self.url = "https://xsts.auth.xboxlive.com/xsts/authorize"

        self.header = {"Content-Type": "application/json", "Accept": "application/json"}

        self.__data = {
            "Properties": {"SandboxId": "RETAIL", "UserTokens": [self.__XboxLiveToken]},
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT",
        }

        self.__data = dumps(self.__data)

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)

        self.__xstsToken = self.__dic["Token"]

        self.minecraftVerification()

        # XSTS Passed

    def minecraftVerification(self):  # Step 4

        logging.info("Passing Minecraft verification")

        self.url = "https://api.minecraftservices.com/authentication/login_with_xbox"

        self.__data = {
            "identityToken": "XBL3.0 x=" + self.__uhs + ";" + self.__xstsToken
        }

        self.__res = post(url=self.url, data=dumps(self.__data))
        self.__dic = loads(self.__res.text)

        self.__jwt = self.__dic["access_token"]

        del self.header
        del self.url

        self.getMinecraftArchive()

    def getMinecraftArchive(self):  # Step 5

        logging.info("Getting Minecraft profiles")

        url = "https://api.minecraftservices.com/minecraft/profile"
        __header = {"Authorization": "Bearer " + self.__jwt}
        __res = get(url=url, headers=__header)
        __dic = loads(__res.text)
        self.__UserInformation = {
            "uuid": __dic["id"],
            "mcid": __dic["name"],
            "skin": __dic["skins"],
            "accessToken": self.__jwt,
            "refreshToken": self.__newRefreshToken,
            "type": "Mojang",
            "time": str(datetime.datetime.today()),
        }
        logging.info(
            f"New tokens available, uuid {self.__UserInformation['uuid']}, time {self.__UserInformation['time']}"
        )
        self.IoController = global_io_controller.LGlobalIOController()
        self.IoController.writeNewUserInformationMicrosoft(self.__UserInformation)


class LMinecraftAuthenticator(QThread):

    finished = pyqtSignal(list)

    def __init__(self, user: str):
        super(LMinecraftAuthenticator, self).__init__()
        self.__user = user

    def run(self):
        self.__IoController = global_io_controller.LGlobalIOController()
        self.__refreshToken = self.__IoController.readRefreshToken(self.__user)
        inherit = LMicrosoftOAuthenticator(self.__refreshToken)
        res = inherit.auth()
        if res is not None:
            self.finished.emit(res)
