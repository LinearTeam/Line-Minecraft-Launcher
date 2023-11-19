import json

class GlobalIOController:
    def __init__(self, Content, DataDirectory):
        self.Content = Content
        self.DataDirectory = DataDirectory
        
    def write_new_minecraft_directory(self):
        TargetJson = self.DataDirectory + "\\MinecraftDirectories.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginData = json.load(f)
        OriginData[self.Content['CustomName']] = self.Content['Path']
        with open(TargetJson, 'w') as f:
            json.dump(OriginData, f, ensure_ascii=False)
            
    def write_new_user_information_microsoft(self):
        TargetJson = self.DataDirectory + "\\Accounts.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginData = json.load(f)
        OriginData['Microsoft'][self.Content['Username']] = {
            "Uuid": self.Content['Uuid'],
            "AccessToken": self.Content['AccessToken'],
            "RefreshToken": self.Content['RefreshToken'],
            "Type": self.Content['Type'],
            "Time": self.Content['Time']    
        }
        with open(TargetJson, 'w') as f:
            json.dump(OriginData, f , ensure_ascii=False)
            
    def read_latest_username(self):
        with open(self.DataDirectory + "\\LatestLoadedData.json") as f:
            LatestLoadedData = json.load(f)
        try:
            return LatestLoadedData['User']
        except:
            return "NoDataLoaded"
            
            
    def read_refresh_token(self, User):
        if User is None:
            User = self.read_latest_username()
        else:
            pass
        try:
            with open(self.DataDirectory + "\\Accounts.json") as f:
                UserInformation = json.load(f)
            try:
                return UserInformation['Microsoft'][User]['RefreshToken']
            except KeyError:
                return "NotFound"
        except:
            return "NoDataLoaded"