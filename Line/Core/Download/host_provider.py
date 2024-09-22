class LOfficialHosts:
    def __init__(self) -> None:
        self.piston = "https://piston-meta.mojang.com/"
        self.launcherMeta = "https://launchermeta.mojang.com/"
        self.launcher =  "https://launcher.mojang.com/"
        self.resources = "https://resources.download.minecraft.net/"
        self.libraries = "https://libraries.minecraft.net/"

class LOfficialSource:
    def __init__(self) -> None:
        self.hostsProvider = LOfficialHosts()
        self.versionsManifest = f"{self.hostsProvider.piston}mc/game/version_manifest.json"

class LBmclApiHosts:
    def __init__(self) -> None:
        self.piston = "https://bmclapi2.bangbang93.com/"
        self.launcherMeta = "https://bmclapi2.bangbang93.com/"
        self.launcher =  "https://bmclapi2.bangbang93.com/"
        self.resources = "https://bmclapi2.bangbang93.com/assets/"
        self.libraries = "https://bmclapi2.bangbang93.com/maven/"

class LBmclApiSource:
    def __init__(self) -> None:
        self.hostsProvider = LBmclApiHosts()
        self.versionsManifest = f"{self.hostsProvider.piston}mc/game/version_manifest.json"