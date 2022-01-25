from hclibs.config import settings
from hclibs.utils import debug
from hclibs.utils import osa
from appdirs import AppDirs
Dirs = AppDirs("HCCL", "Hui2007")
import os
import platform
import webview
import eel
settings.init(os,Dirs)
debug.init(settings)
settings.init2(debug)
osa.init(platform,debug)
webview.create_window('Frameless window',
                          'http://pywebview.flowrl.com/hello',
                          frameless=True)
webview.start()
