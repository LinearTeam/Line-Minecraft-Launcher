#Line Minecraft Launcher
#####  Line Minecraft Launcher 是一个基于终端和GUI的Minecraft启动器

##### 文件夹中，文件有如下作用：
### FOLDER CORE
#### 
#### 1.downloader 文件下载器（支持多线程
#### 2.FileVerifier 文件校验器以及libraries文件夹枝叶建立
#### 3.JsonDownloader 版本JSON下载器以及versions文件夹枝叶建立
#### 4.Loader 游戏加载器
#### 5.MicrosoftLogin 微软正版登录验证模块
#### 6.publicpath.txt 公共路径.\project-line
#
### FOLDER USERDATA
#### 1.downloadsource 下载源
#### 2.javaw javaw路径（动态，可用java将被列举其中
#### 3.logincategory 登录方式（online及offline
#### 4.mcdir minecraft主路径（动态，可用路径将被列举其中
#### 5.usernameg 游戏中的用户名，仅用于离线登录
#### 6.usernamel 启动器终端用户名
#### 7.version 启动版本（动态，可用版本将被列举其中

### FOLDER lfacer
#### GUI文件及资源

### 另外，注意事宜如下：
##### 请手动在.\project-line的根目录下创建.minecraft文件夹
##### 启动游戏暂不可用/23.5.2
##### GUI已添加测试版，但还无法正常使用
##### 如果您想要使用line-python-core来开发启动器，敬请期待官网教程

### 日志
##### 游戏启动暂不可用
##### UI库使用由zhiyiYo开发的qt-fluent-ui
##### 模块化工作已完成，下次将把数据的存储介质改为json
##### 体验GUI请运行LMC.py，否则运行console.py
##### (不想de启动游戏的bug呜呜呜

# THE END
