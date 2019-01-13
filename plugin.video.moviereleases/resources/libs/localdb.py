# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License

import xbmcaddon,xbmc,os
import basic
try: from sqlite3 import dbapi2 as database
except: from pysqlite2 import dbapi2 as database

dataPath		= xbmc.translatePath(xbmcaddon.Addon().getAddonInfo("profile")).decode("utf-8")
addonCache		= os.path.join(dataPath,'cache.db')
language		= xbmcaddon.Addon().getLocalizedString

def create_tables():
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		dbcur.execute("CREATE TABLE IF NOT EXISTS indexing (""imdbid TEXT, ""pageid TEXT, ""label TEXT, ""UNIQUE(imdbid)"");")
		dbcur.execute("CREATE TABLE IF NOT EXISTS cache (""imdbid TEXT, ""tmdbid TEXT, ""label TEXT, ""originallabel TEXT, ""poster TEXT, ""fanart_image TEXT, ""year TEXT, ""info TEXT, ""UNIQUE(imdbid)"");")
		dbcon.commit()
	except BaseException as e: basic.log(u"localdb.create_tables ##Error: %s" % str(e))
	
def get_index(imdbid,index,label):
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		dbcur.execute("SELECT * FROM indexing WHERE imdbid = '%s'" % (imdbid))
		found = dbcur.fetchone()
		if not found: 
			save_index(imdbid,index,label)
			return False
		else: 
			if found[1] == index: return False
			return True
	except BaseException as e: basic.log(u"localdb.get_index ##Error: %s" % str(e))

def get_cache(id,an=None):
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		if an:
                    dbcur.execute("SELECT * FROM cache WHERE label = '%s'" % (id[1]))
                else:
                    if str(id).startswith('tt'): dbcur.execute("SELECT * FROM cache WHERE imdbid = '%s'" % (id))
                    else: dbcur.execute("SELECT * FROM cache WHERE tmdbid = '%s'" % (id))
		found = dbcur.fetchone()
		if not found: return False
		else: return found
	except BaseException as e: basic.log(u"localdb.get_cache ##Error: %s" % str(e))
	
def save_index(imdbid,index,label):
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		dbcur.execute("INSERT INTO indexing Values (?, ?, ?)", (imdbid,index, label))
		dbcon.commit()
	except BaseException as e: basic.log(u"localdb.save_index ##Error: %s" % str(e))

def save_cache(imdbid,tmdbid,label,originallabel,poster,fanart_image,year,info,an=None):
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		if an and poster == '':
                    try: dbcur.execute("INSERT INTO cache Values (?, ?, ?, ?, ?, ?, ?, ?)", (label,tmdbid,label,originallabel,poster,fanart_image,year,info))
                    except: pass
                else:
                    dbcur.execute("INSERT INTO cache Values (?, ?, ?, ?, ?, ?, ?, ?)", (imdbid,tmdbid,label,originallabel,poster,fanart_image,year,info))
		dbcon.commit()
	except BaseException as e: basic.log(u"localdb.save_cache ##Error: %s" % str(e))
	
def delete_index():
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		dbcur.execute("DELETE FROM indexing")
		dbcur.execute("VACUUM")		
		dbcon.commit()
	except BaseException as e: basic.log(u"localdb.delete_index ##Error: %s" % str(e))
	
def delete_cache():
	try:
		dbcon = database.connect(addonCache)
		dbcur = dbcon.cursor()
		dbcur.execute("DELETE FROM cache")
		dbcur.execute("VACUUM")
		dbcon.commit()
		return language(30022).encode('utf-8')
	except BaseException as e: basic.log(u"localdb.delete_cache ##Error: %s" % str(e))
