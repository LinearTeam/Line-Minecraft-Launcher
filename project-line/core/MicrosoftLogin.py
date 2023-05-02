import getpass
import os
from requests import post 
from requests import get
from json import loads
from json import dumps
import webbrowser

def create(osname):
    os.mkdir("C:\\Users\\" + osname + "\\linemc")
    os.mkdir("C:\\Users\\" + osname + "\\linemc\\login")
    f = open("C:\\Users\\" + osname + "\\linemc\\login\\loginstatus.txt", 'w', encoding='utf-8')
    f.write("0")
    f.close()

def resp(code, refreshtoken):
    if code is None:
        return refresh(refreshtoken)
    else:
        return getaccesstoken(code)
        
def getaccesstoken(code):
    username_os = getpass.getuser()
    data = {
        "client_id": "00000000402b5328", # 还是Minecraft客户端id
        "code": code, # 第一步中获取的代码
        "grant_type": "authorization_code",
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "scope": "service::user.auth.xboxlive.com::MBI_SSL"
    }#请求的数据
    url = "https://login.live.com/oauth20_token.srf"
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }#请求头

    res = post(url=url, data=data, headers=header)
    dic = loads(res.text)
    print(res.text)
    access_token = dic["access_token"]
    refresh_token = dic["refresh_token"]
    roaming = "C:\\Users\\" + username_os + "\\linemc"
    f = open(roaming + "\\login\\refreshtoken.txt", 'w', encoding='utf-8')
    f.write(refresh_token)
    f.close()
    f = open(roaming + "\\login\\loginstatus.txt", 'w', encoding='utf-8')
    f.write("1")
    f.close()
    data = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": access_token # 第二步中获取的访问令牌
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }
    url = "https://user.auth.xboxlive.com/user/authenticate"
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = dumps(data)
    res = post(url=url, data=data, headers=header)
    Token = loads(res.text)["Token"]
    uhs = str()
    for i in loads(res.text)["DisplayClaims"]["xui"]:
        uhs = i["uhs"]
    data = dumps({
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                Token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    })
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    res = post(url=url, data=data, headers=header)
    dic = loads(res.text)
    XSTS_token = dic["Token"]
    data = dumps({
        "identityToken": "XBL3.0 x=" + uhs + ";" + XSTS_token
    })
    url = "https://api.minecraftservices.com/authentication/login_with_xbox"
    res = post(url=url, data=data)
    dic = loads(res.text)
    jwt = dic["access_token"]#jwt token,也就是Minecraft访问令牌

    header = {
        "Authorization": "Bearer " + jwt
    }
    res = get(url = "https://api.minecraftservices.com/entitlements/mcstore", headers=header)
    if(res.text == ""):
        return {}
    else:
        header = {
            "Authorization": "Bearer " + jwt
        }
        res = get(url="https://api.minecraftservices.com/minecraft/profile", headers=header)
        dic = loads(res.text)
        username = dic["name"]#用户名
        uuid = dic["id"]#uuid
        return {
            "username": username,
            "uuid": uuid,
            "access_token": jwt
        }
        
def refresh(refreshtoken):
    osname = getpass.getuser()
    data = {
        "client_id": "00000000402b5328", # 还是Minecraft客户端id
        "refresh_token": refreshtoken, # 第一步中获取的代码
        "grant_type": "refresh_token",
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "scope": "service::user.auth.xboxlive.com::MBI_SSL"
    }#请求的数据
    url = "https://login.live.com/oauth20_token.srf"
    header = {
        "Content-Type": "application/x-www-form-urlencoded"
    }#请求头

    res = post(url=url, data=data, headers=header)
    dic = loads(res.text)
    print(res.text)
    access_token = dic["access_token"]
    refreshtoken = dic["refresh_token"]
    f = open("C:\\Users\\" + osname + "\\linemc\\login\\refreshtoken.txt", 'w', encoding='utf-8')
    f.write(refreshtoken)
    f.close()
    data = {
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": access_token # 第二步中获取的访问令牌
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    }
    url = "https://user.auth.xboxlive.com/user/authenticate"
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = dumps(data)
    res = post(url=url, data=data, headers=header)
    Token = loads(res.text)["Token"]
    uhs = str()
    for i in loads(res.text)["DisplayClaims"]["xui"]:
        uhs = i["uhs"]
    data = dumps({
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [
                Token
            ]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    })
    url = "https://xsts.auth.xboxlive.com/xsts/authorize"
    header = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    res = post(url=url, data=data, headers=header)
    dic = loads(res.text)
    XSTS_token = dic["Token"]
    data = dumps({
        "identityToken": "XBL3.0 x=" + uhs + ";" + XSTS_token
    })
    url = "https://api.minecraftservices.com/authentication/login_with_xbox"
    res = post(url=url, data=data)
    dic = loads(res.text)
    jwt = dic["access_token"]#jwt token,也就是Minecraft访问令牌

    header = {
        "Authorization": "Bearer " + jwt
    }
    res = get(url = "https://api.minecraftservices.com/entitlements/mcstore", headers=header)
    if(res.text == ""):
        return {}
    else:
        header = {
            "Authorization": "Bearer " + jwt
        }
        res = get(url="https://api.minecraftservices.com/minecraft/profile", headers=header)
        dic = loads(res.text)
        username = dic["name"]#用户名
        uuid = dic["id"]#uuid
        return {
            "username": username,
            "uuid": uuid,
            "access_token": jwt
        }