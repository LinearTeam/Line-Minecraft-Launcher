class LPiston:

    def __init__(self, url):
        self.url = url

    def getPiston(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace("https://piston-meta.mojang.com/", replacedHost).replace("https://piston-data.mojang.com/", replacedHost)

class LLauncherMeta:
    def __init__(self, url):
        self.url = url
    
    def getLauncherMeta(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace("https://launchermeta.mojang.com/", replacedHost)
    
class LLauncher:
    def __init__(self, url):
        self.url = url
    
    def getLauncher(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace("https://launcher.mojang.com/", replacedHost)

class LResources:
    def __init__(self, url):
        self.url = url
    
    def getResources(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace("https://resources.download.minecraft.net/", replacedHost)
    
class LLibraries:
    def __init__(self, url):
        self.url = url
    
    def getLibraries(self):
        return self.url
    
    def replace(self, replacedHost: str):
        return self.url.replace("https://libraries.minecraft.net/", replacedHost)

class LOfficialHosts:
    def __init__(self) -> None:
        self.piston = LPiston("https://piston-meta.mojang.com/")
        self.launcherMeta = LLauncherMeta("https://launchermeta.mojang.com/")
        self.launcher =  LLauncher("https://launcher.mojang.com/")
        self.resources = LResources("https://resources.download.minecraft.net/")
        self.libraries = LLibraries("https://libraries.minecraft.net/")

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

class LLineMirrorHosts:
    def __init__(self) -> None:
        self.piston = LPiston("https://lm.icecreamteam.win:440/launcher/")
        self.launcherMeta = LLauncherMeta("https://lm.icecreamteam.win:440/launchermeta/")
        self.launcher =  LLauncher("https://lm.icecreamteam.win:440/launcher/")
        self.resources = LResources("https://lm.icecreamteam.win:440/assets/")
        self.libraries = LLibraries("https://lm.icecreamteam.win:440/libraries/")

class LLineMirrorSource:
    def __init__(self) -> None:
        self.name = "LineMirror"
        self.hostsProvider = LLineMirrorHosts()
        self.versionsManifest = "https://lm.icecreamteam.win:440/mc/game/version_manifest.json"