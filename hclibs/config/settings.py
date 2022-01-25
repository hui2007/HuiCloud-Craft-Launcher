import configparser
DefaultConfig = '''[Launcher]
Source=auto
ThreadNum=64
[Version]
Version=0.0.1
Snapshot=true
'''
def init(pos,pDirs):
    global os,Dirs,ConfigDir,Config
    os=pos
    Dirs = pDirs
    ConfigDir = os.path.join(Dirs.user_config_dir,'HCCL.ini')
    if not os.path.exists(ConfigDir):
        try:
            os.makedirs(Dirs.user_config_dir)
        except FileExistsError:
            pass
        with open(ConfigDir,'w+',encoding='utf-8') as ConfigFile:
            ConfigFile.write(DefaultConfig)
    Config = configparser.ConfigParser()
    Config.read(ConfigDir,encoding='utf-8')
def init2(pdebug):
    global debug
    debug = pdebug
    debug.logging.info('fuck')
def get(Section,Option,Type='str'):
    global Config
    Key = None
    try:
        if Config.has_section(Section):
            if Config.has_option(Section,Option):
                if Type=='str':
                    Key = Config.get(Section,Option)
                elif Type=='int':
                    Key  = Config.getint(Section,Option)
                elif Type=='float':
                    Key  = Config.getfloat(Section,Option)
                elif Type=='bool':
                    Key  = Config.getboolean(Section,Option)
    except ValueError:
        pass
    return Key
def set(Section,Option,Key):
    global Config
    try:
        Config.set(Section,Option,Key)
        with open(ConfigDir,'w+') as ConfigFile:
            Config.write(ConfigFile)
    except PermissionError:
        return False
    except configparser.NoSectionError:
        return False
    else:
        return True
    

