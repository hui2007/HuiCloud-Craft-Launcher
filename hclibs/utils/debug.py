import logging
def init(psettings):
    global settings
    settings=psettings
    if settings.Config.has_option('Launcher','debug'):
        if settings.Config.getboolean('Launcher','debug'):
            level = logging.DEBUG
            Debug = True
        else:
            level = logging.INFO
            Debug = False
    elif settings.Config.has_option('Version','snapshot'):
        if settings.Config.getboolean('Version','snapshot'):
            level = logging.DEBUG
            Debug = True
    logging.basicConfig(level=level,
                    format='%(asctime)s %(threadName)-10s[%(filename)s:%(lineno)d][%(funcName)s]-%(levelname)s:%(message)s')
    logging.info('init success')