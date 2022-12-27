'''
@author:Hui2007
'''
import socket
import requests
base_url=("https://launchermeta.mojang.com",
"https://bmclapi2.bangbang93.com",
"https://download.mcbbs.net")
sources=(
    {"version_list":base_url[0]},
    {"version_list":"https://bmclapi2.bangbang93.com"},
    {"version_list":"https://www.mcbbs.net"}
    )
TIMEOUT=0.5
class SettingManager:
    '''
    Manage settings.
    '''
    def initt(self):
        '''
        Init in case of no setting file.
        '''
class SourceManager(SettingManager):
    '''
    Manage download source.
    '''
    def has_internet(self):
        '''
        Judge if has iNtErNeT by ip address
        '''
        ip_address =  socket.gethostbyname(socket.gethostname())
        if ip_address == '127.0.0.1':
            return True
        else:
            return False
    def auto_choose(self):
        '''
        Choose the fastest source automatically.
        '''
        res = {}
        for i,source in enumerate(base_url):
            try:
                resp = requests.head(source,timeout=TIMEOUT)
            except requests.exceptions.ReadTimeout:
                continue
            else:
                match resp.status_code:
                    case 200|301|302:
                        res.update({i:resp.elapsed.total_seconds()})
                    case _:
                        continue
        res = sorted(res.items(),key=lambda x:x[1])
        print(res)
        return res[0][0]
    def get(self):
        '''
        Get selected source.
        '''
class GameVersionManager:
    '''
    Manage game versions.
    '''
    def get_version_list(self,v_type=0):
        '''
        @param:v_type int
        -1:Snapshot
        0:All
        1:Release
        2:Old
        3:Special
        4:April
        '''
        match v_type:
            case 0:
                pass
#GameVersionManager.get_version_list()
a=SourceManager()
print(a.auto_choose())