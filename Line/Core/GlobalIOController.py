import json

class GlobalIOController:
    def __init__(self, Content: str, DataDirectory: str):
        self.Content = Content
        self.DataDirectory = DataDirectory
        
    def write_new_minecraft_directory(self, Dir, Flag) -> None:
        TargetJson = self.DataDirectory + "\\MinecraftDirectories.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginalData = json.load(f)
        OriginalData[Flag] = Dir
        with open(TargetJson, 'w') as f:
            json.dump(OriginalData, f, ensure_ascii=False)
            
    def write_new_user_information_microsoft(self) -> None:
        TargetJson = self.DataDirectory + "\\Accounts.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginalData = json.load(f)
        OriginalData['Microsoft'][self.Content['MCID']] = {
            "Uuid": self.Content['UUID'],
            "Skin": self.Content['Skin'],
            "AccessToken": self.Content['AccessToken'],
            "RefreshToken": self.Content['RefreshToken'],
            "Type": self.Content['Type'],
            "Time": self.Content['Time']    
        }
        with open(TargetJson, 'w') as f:
            json.dump(OriginalData, f , ensure_ascii=False)
            
    def read_latest_username(self) -> str:
        with open(self.DataDirectory + "\\LatestLoadedData.json") as f:
            LatestLoadedData = json.load(f)
        try:
            return LatestLoadedData['User'] if LatestLoadedData['UserType'] == "Microsoft" else None
        except:
            return "NoDataLoaded"
            
            
    def read_refresh_token(self, User) -> str:
        if User == None:
            if self.read_latest_username(User) != None:
                return self.read_refresh_token(User)
            else:
                return "NoDataLoaded"
        elif User != None:
            try:
                with open(self.DataDirectory + "\\Accounts.json") as f:
                    UserInformation = json.load(f)
                try:
                    return UserInformation['Microsoft'][User]['RefreshToken']
                except KeyError:
                    return "0"
            except:
                return "NoDataLoaded"
        
    def overwrite_token(self, Token: str, User: str) -> None:
        TargetJson = self.DataDirectory + "\\Accounts.json"
        with open(TargetJson, 'r') as f:
            OriginalData = json.load(f)
        OriginalData['Microsoft'][User]['AccessToken'] = Token
        with open(TargetJson, 'w') as f:
            json.dump(OriginalData, f, ensure_ascii=False)
            
    def read_latest_loaded_data(self) -> dict:
        TargetJson = self.DataDirectory + "\\LatestLoadedData.json"
        with open(TargetJson, 'r') as f:
            return json.load(f)
        
    def write_loaded_data(self, Data: dict) -> None:
        TargetJson = self.DataDirectory + "\\LatestLoadedData.json"
        with open(TargetJson, 'w') as f:
            json.dump(Data, f, ensure_ascii=False)
            
    def write_new_user_information_offlined(self, Username: str) -> None:
        TargetJson = self.DataDirectory + "\\Accounts.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginalData = json.load(f)
        OriginalData['Offlined'][Username] = {
            "Skin": "Steve"
        }
        with open(TargetJson, 'w') as f:
            json.dump(OriginalData, f , ensure_ascii=False)
            
    def read_saved_users(self, UserType: str) -> list:
        TargetJson = self.DataDirectory + "\\Accounts.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginalData = json.load(f)
        if UserType == "Microsoft":
            return list(OriginalData['Microsoft'].keys())
        else:
            return list(OriginalData['Offlined'].keys())
        
    def read_saved_minecraft_directories(self, Req: str):
        TargetJson = self.DataDirectory + "\\MinecraftDirectories.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginalData = json.load(f)
        if Req == 'Dict':
            return OriginalData
        else:
            Directories = []
            for i in OriginalData:
                Directories.append(OriginalData[i])
            return Directories
    
    def remove_managed_dir(self, TargetKey):
        TargetJson = self.DataDirectory + "\\MinecraftDirectories.json"
        with open(TargetJson, encoding='utf-8') as f:
            OriginalData = json.load(f)
        del OriginalData[TargetKey]
        with open(TargetJson, 'w') as f:
            json.dump(OriginalData, f, ensure_ascii=False)