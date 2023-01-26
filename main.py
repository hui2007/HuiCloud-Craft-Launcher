'''
@author:Hui2007
'''
import socket
import json
import os
import logging
import logging.config
import configparser
import uuid
from string import Template
import requests
import appdirs
VERSION=0.1
app_dirs=appdirs.AppDirs('HCCL','HCStudio')
#config_dir=app_dirs.user_config_dir
config_dir='./HCCL'
log_dir=app_dirs.user_log_dir
#cache_dir=app_dirs.user_cache_dir
cache_dir='./HCCL/cache'
logging.config.fileConfig(fname='log_config.ini',disable_existing_loggers=False,encoding='utf8')
TIMEOUT=1.0
class SettingManager:
    '''
    Manage settings.
    '''
    def __init__(self):
        self.s_logger=logging.getLogger('设置')
        self.setting_init()
        self.s_logger.debug('日志初始化成功')
        self.source_settings = configparser.ConfigParser()
        self.source_settings.read('HCCL/source.ini',encoding='utf8')
        self.s_logger.debug('下载源数据读取成功')
    def setting_init(self):
        '''
        Init in case of no setting file.
        '''
        if not os.path.exists(config_dir) or not os.path.exists(os.path.join(config_dir,'HCCL.ini')):
            try:
                os.makedirs(config_dir,exist_ok=True)
                os.makedirs(cache_dir,exist_ok=True)
                os.makedirs(log_dir,exist_ok=True)
                with open(os.path.join(config_dir,'HCCL.ini'),'w+',encoding='utf8') as setting_file:
                    cfp = configparser.ConfigParser()
                    cfp.add_section('launcher')
                    cfp.set('launcher','version',str(VERSION))
                    cfp.set('launcher','id',str(uuid.UUID(int=uuid.getnode())))
                    cfp.set('launcher','source','auto')
                    cfp.set('launcher','gameDir','[\'.minecraft\']')
                    cfp.set('launcher','gameDirI','0')
                    cfp.write(setting_file)
            except PermissionError as error_reason:
                self.s_logger.error('权限不足:%s',error_reason)
            except Exception as error_reason:
                self.s_logger.error('创建文件（夹）失败:%s',error_reason)
            else:
                self.s_logger.info('配置文件初始化成功')
    def get(self,section,key):
        '''
        Get option.
        '''
        self.s_logger.debug('正尝试读取设置:%s中的%s',section,key)
        try:
            with open(os.path.join(config_dir,'HCCL.ini'),'r',encoding='utf8') as setting_file:
                cfp = configparser.ConfigParser()
                cfp.read_file(setting_file)
                res = cfp.get(section,key)
        except FileNotFoundError as error_reason:
            self.s_logger.error('文件不存在:%s',error_reason)
        except PermissionError as error_reason:
            self.s_logger.error('权限不足:%s',error_reason)
        except Exception as error_reason:
            self.s_logger.error('读取失败:%s',error_reason)
        else:
            self.s_logger.info('设置读取成功:%s中的%s为%s',section,key,res)
            return res
    def get_sources(self,s_type):
        '''
        Get source group
        '''
        sources = self.source_settings.items(s_type)
        self.s_logger.debug('[%s]下载源组获取成功:%s',s_type,str(sources))
        return sources
    def get_game_dir(self):
        self.s_logger.info('正尝试获取选中的游戏目录...')
        try:
            self.s_logger.debug('正尝试获取游戏目录列表...')
            gameDirs = self.get('launcher','gameDir')
            self.s_logger.debug('获取游戏目录列表成功')
            gameDirI = int(self.get('launcher','gameDirI'))
        except TypeError as error_reason:
            self.s_logger.error('默认游戏目录索引读取失败，正采用初始值(0)')
class NetManager(SettingManager):
    '''
    Manage net.
    '''
    def __init__(self):
        super().__init__()
        self.n_logger = logging.getLogger('网络')
        self.n_logger.debug('日志初始化成功')
    def has_internet(self):
        '''
        Judge if has iNtErNeT by ip address
        '''
        ip_address =  socket.gethostbyname(socket.gethostname())
        if ip_address == '127.0.0.1':
            self.n_logger.debug('本地网络连接正常')
            return True
        else:
            self.n_logger.warning('本地网络连接失败')
            return False
    def auto_choose(self,urls):
        '''
        Choose the fastest source automatically.
        '''
        res = {}
        self.n_logger.debug('*** 自动选择下载源开始 ***')
        for i,source in enumerate(urls):
            try:
                url = 'http://'+requests.urllib3.util.parse_url(source[1]).netloc
                self.n_logger.debug('正在向下载源%s发出请求(超时:%f秒)...',i,TIMEOUT)
                resp = requests.head(url,timeout=TIMEOUT)
                '''
            except requests.exceptions.RequestException as error_reason:
                self.n_logger.debug('下载源%s请求失败:%s',i,error_reason)
                continue
            '''
            except Exception as error_reason:
                self.n_logger.debug('下载源%s请求失败:%s',i,error_reason)
                continue
            else:
                match resp.status_code:
                    case 200|301|302|404:
                        self.n_logger.debug('下载源%s请求成功，状态码:%d，用时:%fs',i,resp.status_code,resp.elapsed.total_seconds())
                        res.update({i:resp.elapsed.total_seconds()})
                    case _:
                        self.n_logger.debug('下载源%s请求不成功，状态码:%d，用时:%fs',i,resp.status_code,resp.elapsed.total_seconds())
                        continue
        self.n_logger.debug('全部源请求已完成，正在进行排序...')
        self.n_logger.debug('排序前:%s',str(res))
        res = sorted(res.items(),key=lambda x:x[1])
        self.n_logger.debug('排序后:%s',str(res))
        self.n_logger.debug('下载源%s选择成功',res[0][0])
        self.n_logger.debug('*** 自动选择下载源结束 ***')
        return res[0][0]
    def source_get(self,s_type):
        '''
        Get selected source.
        '''
        self.n_logger.debug('正在获取下载源...')
        source_setting = SettingManager.get(self,'launcher','source')
        sources = SettingManager.get_sources(self,s_type)
        match source_setting:
            case 'auto':
                i = self.auto_choose(sources)
                source = sources[int(i)][1]
            case _:
                try:
                    i = source_setting
                    source = sources[int(i)][1]
                except (IndexError,ValueError) as error_reason:
                    self.n_logger.error('下载源设置无效，已使用默认设置(auto):%s',error_reason)
                    i = self.auto_choose(sources)
                    source = sources[int(i)][1]
        self.n_logger.info('获取到的下载源为%s:%s',i,source)
        return source
    def fix_url(self,p_dict,source):
        '''
        Fix broken url
        '''
        self.n_logger.debug('正尝试替换字符串...')
        self.n_logger.debug('替换前:%s',source)
        base_url = Template(source)
        url = base_url.substitute(p_dict)
        self.n_logger.debug('替换后:%s',url)
        return url
    def get(self,url):
        '''
        @param:url str
        Get content from provided url
        '''
        try:
            self.n_logger.info('正在对%s 发起请求(超时:%f秒)...',url,TIMEOUT)
            resp = requests.get(url,timeout=TIMEOUT)
        except Exception as error_reason:
            self.n_logger.error('请求%s 失败:%s',url,error_reason)
        else:
            s_code = resp.status_code
            match s_code:
                case 200:
                    self.n_logger.info('对%s 请求成功，内容长度为%d，正在返回内容...',url,len(resp.text))
                    return resp.text
                case _:
                    self.n_logger.error('对%s 请求不成功，状态码:%s',url,resp.status_code)
class GameVersionManager(NetManager):
    '''
    Manage game versions.
    '''
    def __init__(self):
        super().__init__()
        self.v_logger = logging.getLogger('版本')
        self.v_logger.debug('日志初始化成功')
    def get_version_list(self,v_type_n):
        '''
        @param:v_type int
        -1:Snapshot
        0:All
        1:Release
        2:Old
        3:Special
        4:Latest
        '''
        v_types=['snapshot','release','old_alpha','old_beta']
        cont = NetManager.get(self,NetManager.source_get(self,'version_list'))
        v_list = json.loads(cont)
        with open(os.path.join(cache_dir,'version_list.json'),'w',encoding='utf8') as ver_list_file:
            json.dump(v_list,ver_list_file)
        match v_type_n:
            case -1:
                v_type = v_types[0]
            case 0:
                v_type = v_types[0:4]
            case 1:
                v_type = v_types[1]
            case 2:
                v_type = v_types[2:4]
            case 3:
                return
            case 4:
                self.v_logger.info('已返回最新版本数据:%s',str(v_list['latest']))
                return v_list['latest']
            case _:
                v_type = v_types[0:3]
        self.v_logger.debug('已选定获取的版本类型:%s',str(v_type))
        vers = []
        s_vers  = []
        for ver_meta in v_list['versions']:
            ver = {
                        'v_id':ver_meta['id'],
                        'time':ver_meta['time'],
                        'v_sha1':ver_meta['sha1']
                    }
            vers.append(ver)
            if ver_meta['type'] in v_type:
                s_vers.append(ver)
        self.v_logger.info('获取选定类型(%d)版本列表成功，数目为%d，正在返回内容...',v_type_n,len(s_vers))
        return s_vers
    def get_version_json(self,v_meta):
        '''
        Get specified version json.
        '''
        self.v_logger.info('正尝试获取版本JSON文件(%s)...',v_meta['v_id'])
        cont = NetManager.get(self,NetManager.fix_url(self,v_meta,NetManager.source_get(self,'version_json')))
        '''
        with open(os.path.join(cache_dir,'1.json'),'w',encoding='utf8') as ver_list_file:
            ver_list_file.write(cont)
        '''
if __name__ == '__main__':
    a=SettingManager()
    print(a.get_game_dir())
