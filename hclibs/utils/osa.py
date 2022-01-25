def init(ppf,pdebug):
    global os,debug
    platform=ppf
    debug=pdebug
    OsId = platform.system()
    debug.logging.info(OsId)
