import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import datetime

from requests import post
from requests import get
from json import loads
from json import dumps
from PyQt5.QtCore import QThread
from PyQt5.QtCore import pyqtSignal

import Core.Launcher.global_io_controller as global_io_controller


class MicrosoftLoginHandler:

    def __init__(self, Code, RefreshToken):
        self.Code = Code
        self.RefreshToken = RefreshToken

    def Login(self):

        if self.Code is None:
            return self.refresh_access_token()
        else:
            return self.get_access_token()

    def get_access_token(self):
        data = {
            "client_id": "00000000402b5328",  # 还是Minecraft客户端id
            "code": self.Code,  # 第一步中获取的代码
            "grant_type": "authorization_code",
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "scope": "service::user.auth.xboxlive.com::MBI_SSL",
        }  # 请求的数据
        url = "https://login.live.com/oauth20_token.srf"
        header = {"Content-Type": "application/x-www-form-urlencoded"}  # 请求头

        res = post(url=url, data=data, headers=header)
        dic = loads(res.text)
        AccessToken = dic["access_token"]
        NewRefreshToken = dic["refresh_token"]
        data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": AccessToken,  # 第二步中获取的访问令牌
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        }
        url = "https://user.auth.xboxlive.com/user/authenticate"
        header = {"Content-Type": "application/json", "Accept": "application/json"}
        data = dumps(data)
        res = post(url=url, data=data, headers=header)
        Token = loads(res.text)["Token"]
        uhs = str()
        for i in loads(res.text)["DisplayClaims"]["xui"]:
            uhs = i["uhs"]
        data = dumps(
            {
                "Properties": {"SandboxId": "RETAIL", "UserTokens": [Token]},
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT",
            }
        )
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        header = {"Content-Type": "application/json", "Accept": "application/json"}
        res = post(url=url, data=data, headers=header)
        dic = loads(res.text)
        XSTS_token = dic["Token"]
        data = dumps({"identityToken": "XBL3.0 x=" + uhs + ";" + XSTS_token})
        url = "https://api.minecraftservices.com/authentication/login_with_xbox"
        res = post(url=url, data=data)
        dic = loads(res.text)
        jwt = dic["access_token"]  # jwt token,也就是Minecraft访问令牌

        header = {"Authorization": "Bearer " + jwt}
        res = get(
            url="https://api.minecraftservices.com/entitlements/mcstore", headers=header
        )
        if res.text == "":
            return {}
        else:
            header = {"Authorization": "Bearer " + jwt}
            res = get(
                url="https://api.minecraftservices.com/minecraft/profile",
                headers=header,
            )
            dic = loads(res.text)
            RequestUser = dic["name"]  # 用户名
            uuid = dic["id"]  # uuid
            UserInformation = {
                "Username": RequestUser,
                "Uuid": uuid,
                "AccessToken": jwt,
                "RefreshToken": NewRefreshToken,
                "Type": "Mojang",
                "Time": str(datetime.datetime.today()),
            }
            self.IOController = global_io_controller.LGlobalIOController(
                UserInformation,
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\Data",
            )
            self.IOController.writeNewUserInformationMicrosoft()
            return ["成功", "账户{0}已添加".format(UserInformation["Username"])]

    def refresh_access_token(self):
        data = {
            "client_id": "00000000402b5328",  # 还是Minecraft客户端id
            "refresh_token": self.RefreshToken,  # 第一步中获取的代码
            "grant_type": "refresh_token",
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "scope": "service::user.auth.xboxlive.com::MBI_SSL",
        }  # 请求的数据
        url = "https://login.live.com/oauth20_token.srf"
        header = {"Content-Type": "application/x-www-form-urlencoded"}  # 请求头

        res = post(url=url, data=data, headers=header)
        dic = loads(res.text)
        access_token = dic["access_token"]
        NewRefreshToken = dic["refresh_token"]
        data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": access_token,  # 第二步中获取的访问令牌
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT",
        }
        url = "https://user.auth.xboxlive.com/user/authenticate"
        header = {"Content-Type": "application/json", "Accept": "application/json"}
        data = dumps(data)
        res = post(url=url, data=data, headers=header)
        Token = loads(res.text)["Token"]
        uhs = str()
        for i in loads(res.text)["DisplayClaims"]["xui"]:
            uhs = i["uhs"]
        data = dumps(
            {
                "Properties": {"SandboxId": "RETAIL", "UserTokens": [Token]},
                "RelyingParty": "rp://api.minecraftservices.com/",
                "TokenType": "JWT",
            }
        )
        url = "https://xsts.auth.xboxlive.com/xsts/authorize"
        header = {"Content-Type": "application/json", "Accept": "application/json"}
        res = post(url=url, data=data, headers=header)
        dic = loads(res.text)
        XSTS_token = dic["Token"]
        data = dumps({"identityToken": "XBL3.0 x=" + uhs + ";" + XSTS_token})
        url = "https://api.minecraftservices.com/authentication/login_with_xbox"
        res = post(url=url, data=data)
        dic = loads(res.text)
        jwt = dic["access_token"]  # jwt token,也就是Minecraft访问令牌

        header = {"Authorization": "Bearer " + jwt}
        res = get(
            url="https://api.minecraftservices.com/entitlements/mcstore", headers=header
        )
        if res.text == "":
            return {}
        else:
            header = {"Authorization": "Bearer " + jwt}
            res = get(
                url="https://api.minecraftservices.com/minecraft/profile",
                headers=header,
            )
            dic = loads(res.text)
            RequestUser = dic["name"]  # 用户名
            uuid = dic["id"]  # uuid
            UserInformation = {
                "Username": RequestUser,
                "Uuid": uuid,
                "AccessToken": jwt,
                "RefreshToken": NewRefreshToken,
                "Type": "Mojang",
                "Time": str(datetime.datetime.today()),
            }
            self.IOController = global_io_controller.LGlobalIOController(
                UserInformation,
                os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\Data",
            )
            self.IOController.writeNewUserInformationMicrosoft()
            return {
                "Token": UserInformation["AccessToken"],
                "User": UserInformation["Username"],
            }


class MultiThreadMicrosoftLoginHandler(QThread):

    finished = pyqtSignal(list)

    def __init__(self, Code, RefreshToken):
        super().__init__()
        self.Code = Code
        self.RefreshToken = RefreshToken

    def run(self):
        self.Handler = MicrosoftLoginHandler(self.Code, self.RefreshToken)
        self.finished.emit(self.Handler.Login())


class MultiThreadTokenRefresher(QThread):

    finished = pyqtSignal(dict)

    def __init__(self, User):
        super().__init__()
        self.User = User

    def run(self):
        self.IOController = global_io_controller.LGlobalIOController(
            None, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\Data"
        )
        self.RefreshToken = self.IOController.readRefreshToken(self.User)
        if self.RefreshToken != "NotFound":
            self.Handler = MicrosoftLoginHandler(None, self.RefreshToken)
            self.finished.emit(self.Handler.refresh_access_token())
        else:
            self.finished.emit({"User": "Not Found"})
