import xbmc,xbmcaddon

__addon__ = xbmcaddon.Addon()
debug = __addon__.getSetting("Debug")

def myLogger(msg, logLevel = xbmc.LOGDEBUG, force = False):     ##### burekas
    #logging.warning(msg)
    if(debug == "true" or force):
        if logLevel == xbmc.LOGDEBUG:
            logLevel = xbmc.LOGINFO #xbmc.LOGWARNING

    if not isinstance(msg, str):
        msg = repr(msg)

    try:
        xbmc.log("#####[AllSubs]##### " + msg, logLevel)
    except UnicodeEncodeError:
        xbmc.log("#####[AllSubs]##### " + msg.encode( "utf-8", "ignore" ), logLevel)