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
        dbcur.execute("CREATE TABLE IF NOT EXISTS watch (""title TEXT, ""label TEXT, ""overlay TEXT, ""UNIQUE(title)"");")
        dbcon.commit()
    except BaseException as e: _log(u"local2db.create_tables ##Error: %s" % str(e))

def get_watch(title,label,overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("SELECT overlay FROM watch WHERE title = '%s'" % (title))
        found = dbcur.fetchone()
        if not found:
            save_watch(title,label,overlay)
            #_log(u"returned overlay: %s" % str(overlay))
            return overlay
        else:
            #_log(u"returned found: %s" % str(found[0]))
            return found[0]
    except BaseException as e: _log(u"local2db.get_watch ##Error: %s" % str(e))

def save_watch(title,label,overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcur = dbcon.cursor()
        dbcur.execute("INSERT INTO watch Values (?, ?, ?)", (title, label, overlay))
        dbcon.commit()
    except BaseException as e: _log(u"local2db.save_watch ##Error: %s" % str(e))

def update_watch(title, label, overlay):
    try:
        dbcon = database.connect(addonCache)
        dbcon.text_factory = str
        dbcon.execute("UPDATE watch SET overlay = '%s' WHERE title = '%s'" % (overlay, title))
        dbcon.commit()
    except BaseException as e: _log(u"local2db.update_watch ##Error: %s" % str(e))

def delete_watch():
    try:
        dbcon = database.connect(addonCache)
        dbcur = dbcon.cursor()
        dbcur.execute("DELETE FROM watch")
        dbcur.execute("VACUUM")		
        dbcon.commit()
    except BaseException as e: _log(u"local2db.delete_watch ##Error: %s" % str(e))

def _log(msg):
    s = u"%s" % (msg)
    xbmc.log(s.encode('utf-8'), level=xbmc.LOGNOTICE)
