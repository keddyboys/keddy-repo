# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License

import os,json,urllib,urllib2,xbmcaddon,xbmc,xbmcgui
import links

__name__		= xbmcaddon.Addon().getAddonInfo("id")
addonName		= xbmcaddon.Addon().getAddonInfo("name")
debug 			= xbmcaddon.Addon().getSetting('debug_mode')
addonPath   	= xbmcaddon.Addon().getAddonInfo("path")
language		= xbmcaddon.Addon().getLocalizedString

def getKey(item):
	return item[0]
	
def cleanTitle(title):
	title = title.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&").replace("&#39;", "'").replace("&quot;", "\"").replace("&ndash;", "-").replace('"',"").replace("’","'")
	title = title.strip()
	return title
	
def open_url(url,post=None):
	if post == None: req = urllib2.Request(url)
	else: req = urllib2.Request(url,post)
	req.add_header('User-Agent', 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:10.0a1) Gecko/20111029 Firefox/10.0a1')
	req.add_header('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8')
	try: 
		response = urllib2.urlopen(req)
		link=response.read()
		response.close()
		return link		
	except BaseException as e: log(u"open_url ERROR: %s - %s" % (str(url),str(e).encode('ascii','xmlcharrefreplace')))
	except urllib2.HTTPError, e: log(u"open_url HTTPERROR: %s - %s" % (str(url),str(e.code)))
	except urllib2.URLError, e: log(u"open_url URLERROR: %s - %s" % (str(url),str(e.reason)))
	except httplib.HTTPException, e: log(u"open_url HTTPException: %s" % (str(url)))

def open_url_headers(url,headers):
	request = urllib2.Request(url, headers=headers)
	try: 
		response_body = urllib2.urlopen(request).read()	
		return response_body
	except BaseException as e: log(u"open_url_headers ERROR: %s - %s" % (str(url),str(e).decode('ascii','ignore')))
	except urllib2.HTTPError, e: log(u"open_url_headers HTTPERROR: %s - %s" % (str(url),str(e.code)))
	except urllib2.URLError, e: log(u"open_url_headers URLERROR: %s - %s" % (str(url),str(e.reason)))
	except httplib.HTTPException, e: log(u"open_url_headers HTTPException: %s" % (str(url)))
	
def listsites(sitesfile):
	list = []
	ins = open(sitesfile, "r" )	
	for line in ins: 
		parameters = json.loads(line)
		url=parameters['site']
		enabled=parameters['enabled']		
		list.append(json.loads('{"url":"'+url+'","enabled":"'+enabled+'"}'))						
	return list

def readoneline(file):
	f = open(file,"r")
	line = f.read()
	f.close()
	return line

def readalllines(file):
	f = open(file,"r")
	lines = f.readlines()
	f.close()
	return lines

def readfiletoJSON(file):
	f = open(file,"r")
	line = f.read().strip('\n')
	f.close()	
	return line
	
def writefile(file,mode,string):
	writes = open(file, mode)
	writes.write(string)
	writes.close()

def progressbar(progress,f,totalpass,message,message2=None,message3=None,normal=False):
	if normal: percent = int( ( f / float(totalpass) ) * 100)
	else: percent = int( ( int(totalpass)-f / float(totalpass) ) * 100)
	progress.update( percent, message, message2, message3 )
	if progress.iscanceled():
		progress.close()
		xbmcgui.Dialog().ok('ERROR','Cancelled.')
		return ''

def infoDialog(str, header=addonName):
	try: xbmcgui.Dialog().notification(header, str, addonPath+'icon.png', 3000, sound=False)
	except: xbmc.executebuiltin("Notification(%s,%s, 3000, %s)" % (header, str, addonPath+'icon.png'))

def removecache(cachePath):
	try:
		for root,dir,files in os.walk(cachePath):
			for f in files: os.unlink(os.path.join(root, f))
		os.rmdir(cachePath)
		return language(30022).encode('utf-8')
	except BaseException as e: log(u"removecache ERROR: %s" % (str(e)))

def get_api_language():
	lang = xbmcaddon.Addon().getSetting('pref_language')	
	if lang == "system": lang = xbmc.getLanguage(xbmc.ISO_639_1)
	else: lang = xbmcaddon.Addon().getSetting('pref_language')
	return lang

def settings_open(id):
	import xbmc
	xbmc.executebuiltin('Addon.OpenSettings(%s)' % id)
	
def _log(module, msg):
	s = u"#[%s] - %s" % (module, msg)
	xbmc.log(s.encode('utf-8'), level=xbmc.LOGNOTICE)

def log(msg):
	if debug == 'true': _log(__name__, msg)
