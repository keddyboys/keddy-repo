# -*- coding: UTF-8 -*-

import xbmcaddon,xbmc,os
try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

dataPath		= xbmc.translatePath(xbmcaddon.Addon().getAddonInfo("profile")).decode("utf-8")
addonCache		= os.path.join(dataPath,'cache.db')
language		= xbmcaddon.Addon().getLocalizedString

def create_tables():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("CREATE TABLE IF NOT EXISTS watched (""title TEXT, ""label TEXT, ""overlay TEXT, ""UNIQUE(title)"");")
        dbcon.commit()
    except BaseException as e: _log(u"localdb.create_tables ##Error: %s" % str(e))

def get_watched(title,label,overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT overlay FROM watched WHERE title = '%s'" % (title))
        found = dbcur.fetchone()
        if not found:
            save_watched(title,label,overlay)
            #_log(u"returned overlay: %s" % str(overlay))
            return overlay
        else:
            #_log(u"returned found: %s" % str(found[0]))
            return found[0]
    except BaseException as e: _log(u"localdb.get_watched ##Error: %s" % str(e))

def save_watched(title,label,overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO watched Values (?, ?, ?)", (title, label, overlay))
        dbcon.commit()
    except BaseException as e: _log(u"localdb.save_watched ##Error: %s" % str(e))

def update_watched(title, label, overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcon.execute("UPDATE watched SET overlay = '%s' WHERE title = '%s'" % (overlay, title))
        dbcon.commit()
    except BaseException as e: _log(u"localdb.update_watched ##Error: %s" % str(e))

def delete_watched():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM watched")
        dbcur.execute("VACUUM")		
        dbcon.commit()
    except BaseException as e: _log(u"localdb.delete_watched ##Error: %s" % str(e))

def _log(msg):
    s = u"%s" % (msg)
    xbmc.log(s.encode('utf-8'), level=xbmc.LOGNOTICE)
