import json



class LPiston:

    def __init__(self, url):
#        self.officialField = LOfficialHosts()
        self.url = url

    def getPiston(self):
        print(self.url)
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace(LBmclApiHosts().piston.getPiston(), replacedHost)

class LLauncherMeta:
    def __init__(self, url):
        #LOfficialHosts() = LOfficialHosts()
        self.url = url
    
    def getLauncherMeta(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace(LOfficialHosts().launcherMeta.getLauncherMeta(), replacedHost)
    
class LLauncher:
    def __init__(self, url):
        #LOfficialHosts() = LOfficialHosts()
        self.url = url
    
    def getLauncher(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace(LOfficialHosts().launcher.getLauncher(), replacedHost)

class LResources:
    def __init__(self, url):
        #LOfficialHosts() = LOfficialHosts()
        self.url = url
    
    def getResources(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace(LOfficialHosts().resources.getResources(), replacedHost)
    
class LLibraries:
    def __init__(self, url):
        #LOfficialHosts() = LOfficialHosts()
        self.url = url
    
    def getLibraries(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace(LOfficialHosts().libraries.getLibraries(), replacedHost)

class LOfficialHosts:
    def __init__(self) -> None:
        print("initializing")
        self.piston = LPiston("https://piston-meta.mojang.com/")
        self.launcherMeta = LLauncherMeta("https://launchermeta.mojang.com/")
        self.launcher =  LLauncher("https://launcher.mojang.com/")
        self.resources = LResources("https://resources.download.minecraft.net/")
        self.libraries = LLibraries("https://libraries.minecraft.net/")
        print("finished")

class LOfficialSource:
    def __init__(self) -> None:
        self.name = "Official"
        self.hostsProvider = LOfficialHosts()
        self.versionsManifest = f"{self.hostsProvider.piston.getPiston()}mc/game/version_manifest.json"

class LBmclApiHosts:
    def __init__(self) -> None:
        self.piston = LPiston("https://bmclapi2.bangbang93.com/")
        self.launcherMeta = LLauncherMeta("https://bmclapi2.bangbang93.com/")
        self.launcher =  LLauncher("https://bmclapi2.bangbang93.com/")
        self.resources = LResources("https://bmclapi2.bangbang93.com/assets/")
        self.libraries = LLibraries("https://bmclapi2.bangbang93.com/maven/")

class LBmclApiSource:
    def __init__(self) -> None:
        self.name = "BmclApi"
        self.hostsProvider = LBmclApiHosts()
        self.versionsManifest = f"{self.hostsProvider.piston.getPiston()}mc/game/version_manifest.json"

