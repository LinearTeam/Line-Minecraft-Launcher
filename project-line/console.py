import os
import sys
rp = os.getcwd() + "\\core"
sys.path.append(rp)
import JsonDownloader
import Loader

def reload():
    main = os.getcwd()
    f = open(main + "\\userdata\\downloadsource.txt", encoding='utf-8')
    downloadsource = f.read()
    f.close()
    main = os.getcwd()
    f = open(main + "\\userdata\\javaw.txt", encoding='utf-8')
    javaw = f.read()
    f.close()
    main = os.getcwd()
    f = open(main + "\\userdata\\logincategory.txt", encoding='utf-8')
    logincategory = f.read()
    f.close()
    main = os.getcwd()
    f = open(main + "\\userdata\\maxmem.txt", encoding='utf-8')
    maxmem = f.read()
    f.close()
    main = os.getcwd()
    f = open(main + "\\userdata\\mcdir.txt", encoding='utf-8')
    mcdir = f.read()
    f.close()
    main = os.getcwd()
    f = open(main + "\\userdata\\usernameg.txt", encoding='utf-8')
    username = f.read()
    f.close()
    main = os.getcwd()
    f = open(main + "\\userdata\\version.txt", encoding='utf-8')
    version = f.read()
    f.close()

def starting(logincategory, mcdir, javaw, maxmem, version, username, downloadsource):
    t = input("line:")
    if t == "load":
        Loader.mainstart(logincategory, mcdir, javaw, maxmem, version, username)
    if t == "download":
        JsonDownloader.main(downloadsource, mcdir)