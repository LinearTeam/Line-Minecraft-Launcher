import datetime
import os
from requests import post, get
from json import dumps, loads
from PyQt5.QtCore import QThread
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from LocalServer import start_server
import GlobalIOController
import Logger
from PyQt5.QtCore import pyqtSignal


class MicrosoftOAuthenticator:
    def __init__(self, RefreshToken: str = 0):
        self.RefreshToken = RefreshToken
        self.Logger = Logger.Logger("LineMinecraftLauncher", "1", False, "./Log/LatestLog.log")

    def auth(self):
        if self.RefreshToken == "0":
            try:
                self.get_access_token()
                self.Logger.Safe("A new account {0} has added".format(self.__UserInformation["MCID"]))
                return ["成功", "账户{0}已添加".format(self.__UserInformation["MCID"])]
            except Exception as e:
                self.Logger.Error("Unable to get Minecraft archive information" + str(e))
                return ['失败', "无法获取到Minecraft档案信息，请排除: \n 1.网络连接错误 \n 2.未购买Minecraft Java \n 3.已购买游戏，但未注册档案"]
        else:
            try:
                self.refresh_access_token()
                self.Logger.Safe("Token refreshed")
                return ['提示', '用户{0}的Access Token已刷新'.format(self.__UserInformation["MCID"])]
            except Exception as e:
                self.Logger.Error("Faild to refresh token, please check your network connection\n Error Info:" + str(e))
                return ["错误", "无法刷新令牌，请检查你的网络连接。\n错误信息:"  + str(e)]
            

    def refresh_access_token(self): #Step #0
        self.Logger.Safe("Refreshing token")
        self.url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

        self.header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        self.__data = {
            "client_id": "1cbfda79-fc84-47f9-8110-f924da9841ec",
            "scope": "XboxLive.signin offline_access",
            "refresh_token": self.RefreshToken,
            "redirect_uri": "http://127.0.0.1:40935",
            "grant_type": "refresh_token"
        }

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)
        self.__NewRefreshToken = self.__dic['refresh_token']
        self.__AccessToken = self.__dic['access_token']
        self.xbox_live_verification()


    def get_access_token(self): #Step 1

        self.Logger.Safe("Getting access token")

        code = start_server()

        self.url = "https://login.microsoftonline.com/consumers/oauth2/v2.0/token"

        self.header = {
            "Content-Type": "application/x-www-form-urlencoded"
        }

        self.__data = {
            "client_id": "1cbfda79-fc84-47f9-8110-f924da9841ec",
            "scope": "XboxLive.signin offline_access",
            "code": code,
            "redirect_uri": "http://127.0.0.1:40935",
            "grant_type": "authorization_code"
        }

        del code
        
        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)
        self.__AccessToken = self.__dic["access_token"]
        self.__NewRefreshToken = self.__dic["refresh_token"]#By the way, get the refresh token
        self.xbox_live_verification()

        #Microsoft OAuth Passed


    def xbox_live_verification(self): #Step2

        self.Logger.Safe("Passing Xbox Live Verification")

        self.url = "https://user.auth.xboxlive.com/user/authenticate"

        self.header = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.__data = {
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": "d=" + self.__AccessToken
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        }
        self.__data = dumps(self.__data)

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)

        self.__XboxLiveToken = self.__dic['Token']


        self.__uhs = str()
        for i in self.__dic["DisplayClaims"]["xui"]:
            self.__uhs = i["uhs"]

        self.get_xsts_token()

        #XBL Passed

    def get_xsts_token(self): #Step 3
        
        self.Logger.Safe("Getting XSTS token")

        self.url = "https://xsts.auth.xboxlive.com/xsts/authorize"

        self.header = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

        self.__data = {
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [
                    self.__XboxLiveToken
                ]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }

        self.__data = dumps(self.__data)

        self.__res = post(url=self.url, headers=self.header, data=self.__data)
        self.__dic = loads(self.__res.text)

        self.__XstsToken = self.__dic['Token']

        self.minecraft_verification()
        
        #XSTS Passed

    def minecraft_verification(self): #Step 4
        
        self.Logger.Safe("Passing Minecraft Verification")

        self.url = "https://api.minecraftservices.com/authentication/login_with_xbox"

        self.__data = {
            "identityToken": "XBL3.0 x=" + self.__uhs + ";" + self.__XstsToken
        }

        self.__res = post(url=self.url, data=dumps(self.__data))
        self.__dic = loads(self.__res.text)

        self.__jwt = self.__dic['access_token']

        del self.header
        del self.url

        self.get_minecraft_archive()


    def get_minecraft_archive(self): #Step 5

        self.Logger.Safe("Organizing Minecraft archive information")

        url = "https://api.minecraftservices.com/minecraft/profile"
        __header = {
            "Authorization": "Bearer " + self.__jwt
        }
        __res = get(url=url, headers=__header)
        __dic = loads(__res.text)
        self.__UserInformation = {
            "UUID": __dic['id'],
            "MCID": __dic['name'],
            "Skin": __dic['skins'],
            "AccessToken": self.__jwt,
            "RefreshToken": self.__NewRefreshToken,
            "Type": "Mojang",
            "Time": str(datetime.datetime.today())
        }
        self.IOController = GlobalIOController.GlobalIOController(self.__UserInformation, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\Data")
        self.IOController.write_new_user_information_microsoft()
        self.Logger.Safe("Well done")

class MinecraftAuthenticator(QThread):

    finished = pyqtSignal(list)

    def __init__(self, user: str):
        super(MinecraftAuthenticator, self).__init__()
        self.__user = user

    def run(self):
        self.__IOController = GlobalIOController.GlobalIOController(None, os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "\\Data")
        self.__RefreshToken = self.__IOController.read_refresh_token(self.__user)
        inherit = MicrosoftOAuthenticator(self.__RefreshToken)
        res = inherit.auth()
        if res is not None:
            self.finished.emit(res)
        else:
            self.finished.emit(['refreshed'])