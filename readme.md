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
#
### 另外，注意事宜如下：
##### 本启动器的主程序暂未编写
##### 不可启动Fabric/Forge moded的版本
##### 要测试core中的模块，请更改mcdir,javaw,logincategory,version,publicpath等文件中的信息
##### 请手动在.\project-line的根目录下创建.minecraft文件夹
##### 如果您想要使用line-python-core来开发启动器，敬请期待官网教程

# THE END