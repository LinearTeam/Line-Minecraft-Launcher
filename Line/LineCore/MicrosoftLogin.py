from pkg_resources import get_supported_platform
import requests
import json

def get_auth_token(auth_code):
    ret = json.loads(requests.post(
        url="https://login.live.com/oauth20_token.srf",
        data={
            "client_id": "00000000402b5328",
            "code": auth_code,
            "grant_type": "authorization_code",
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "scope": "service::user.auth.xboxlive.com::MBI_SSL"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).text)
    return ret["access_token"]

def refresh_auth_token(refresh_token):
    ret = json.loads(requests.post(
        url="https://login.live.com/oauth20_token.srf",
        data={
            "client_id": "00000000402b5328",
            "code": refresh_token,
            "grant_type": "refresh_token",
            "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
            "scope": "service::user.auth.xboxlive.com::MBI_SSL"
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    ).text)
    return ret["refresh_token"]

def xbl_auth(access_token):
    ret = json.loads(requests.post(
        url="https://user.auth.xboxlive.com/user/authenticate",
        data={
            "Properties": {
                "AuthMethod": "RPS",
                "SiteName": "user.auth.xboxlive.com",
                "RpsTicket": f'd={access_token}'
            },
            "RelyingParty": "http://auth.xboxlive.com",
            "TokenType": "JWT"
        },
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
    ).text)
    xbl_token = ret["Token"]
    user_hash = ret["DisplayClaims"]["xui"]["uhs"]
    return (xbl_token, user_hash)

def xsts_auth(xbl_token):
    ret = json.loads(requests.post(
        url="https://xsts.auth.xboxlive.com/xsts/authorize", 
        data={
            "Properties": {
                "SandboxId": "RETAIL",
                "UserTokens": [xbl_token]
            },
            "RelyingParty": "rp://api.minecraftservices.com/",
            "TokenType": "JWT"
        }, 
        headers={
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
    ).text)
    xsts_token = ret["Token"]
    return xsts_token

def get_jwt(user_hash, xsts_token):
    ret = json.loads(requests.post(
        url="https://api.minecraftservices.com/authentication/login_with_xbox", 
        data={"identityToken": f"XBL3.0 x={user_hash};{xsts_token}"}
    ).text)
    return ret["access_token"]

def check_if_own_game(jwt):
    ret = requests.get(
        url = "https://api.minecraftservices.com/entitlements/mcstore", 
        headers={"Authorization": f"Bearer {jwt}"}
    ).text
    if ret == "" :
        return False
    else:
        return True

def get_user_info(jwt):
    ret = json.loads(requests.get(
        url="https://api.minecraftservices.com/minecraft/profile", 
        headers={"Authorization": f"Bearer {jwt}"}
    ).text)
    uuid = ret["id"]
    user_name = ret["name"]
    return (uuid, user_name)


# under is
# TODO

def get_access_token(auth_code):
    access_token = get_auth_token(auth_code)
    xbl_token, user_hash = xbl_auth(access_token)
    xsts_token = xsts_auth(xbl_token)
    jwt = get_jwt(user_hash, xsts_token)
    if not check_if_own_game(jwt):
        return {}
    uuid, user_name = get_user_info(jwt)
    
    return {
        "username": user_name,
        "uuid": uuid,
        "access_token": jwt
    }
def resp(code, refreshtoken):
    if code is None:
        return refresh_auth_token(refreshtoken)
    else:
        return get_access_token(code)
def judge():
    username = input("loginto")
    
    f = open(f"{line_root_folder}\\login\\userIndex.txt", 'r', encoding='utf-8')
    detect = f.read()
    f.close()
    
    detect = detect.split("\n")
    if username in detect:
        code = None
        f = open(f"{line_root_folder}\\login\\tokens\\" + username + ".txt", 'r', encoding='utf-8')
        refreshtoken = f.read()
        f.close()
        resp(code, refreshtoken)
    else:
        webBroswerLogin()
        
        
def webBroswerLogin(reUrl):
    
    begin = reUrl.find("code=") + 5
    end = reUrl.find("&lc")
    code = str("")
    
    for kind in range(begin, end):
        code += reUrl[kind]
        
    return code