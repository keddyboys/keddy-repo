# -*- coding: utf-8 -*-
import datetime
import os
import re
import sys
import urllib
import urllib2
import urlparse
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import json

settings = xbmcaddon.Addon(id='plugin.video.filmeserialeonlineorg')
__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', '')).decode("utf-8")
search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
sys.path.append (__resource__)
import local2db
base_url = 'http://www.filmenoi.biz'
if __addon__.getSetting("resolver") == "0":
    try:
        import urlresolver
    except:
        pass
else:
    try:
        import urlresolver9 as urlresolver
    except:
        pass

local2db.create_tables()

def ROOT():
    addDir('Filme', 'http://www.filmeserialeonline.org/filme-online/', 6, movies_thumb, 'recente', 'filme')
    addDir('Filme an 2016', 'http://filmenoi.biz/an/2016', 6, movies_thumb, 'filme')
    addDir('Filme an 2017', 'http://filmenoi.biz/an/2016', 6, movies_thumb, 'filme')
    addDir('Episoade adăugate Recent', 'http://www.filmeserialeonline.org/episodul', 6, movies_thumb, 'recente', 'episoade')
    addDir('Căutare', base_url, 3, movies_thumb)
    
def striphtml(data):
    p = re.compile('<.*?>')
    cleanp = re.sub(p, '', data)
    return cleanp

def cauta_film(url):
    link = get_search(url)
                   
    regex_menu = '''<div class="eTitle"(.+?)</div></td></tr></table><br />'''
    regex_submenu = '''<a href="(.+?)".+?>(.+?)</a>'''
    for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
        match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
        for legatura, nume in match:
		    #nume = nume.replace('&#8217;','\'')
            addDir(striphtml(nume), legatura, 5, movies_thumb)	

    match = re.compile('"swchItem"', re.IGNORECASE).findall(link)
    if len(match) > 0:
        new = re.compile('/\?q=.+?t=\d+;p=(\d+);md').findall(url)
        if new:
            nexturl = re.sub('p=\d+', 'p=' + (str(int(new[0]) + 1)), url)
        else:
            nexturl = url + ';t=0;p=2;md='
      
        print "NEXT " + nexturl
      
        addNext('Next', nexturl, 2, next_thumb)
            
 
def video_list(url, name, iconimage=None, descriere=None):
    link = get_search(url)
    thumb = iconimage
    regex_lnk = '''(?:"movieplay"|"player\d+").+?iframe.+?src="((?:[htt]|[//]).+?)"'''
    match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
    for link1 in match_lnk:
            if link1.startswith("//"):
                link1 = 'http:' + link1 #//ok.ru fix
            parsed_url1 = urlparse.urlparse(link1)
            if parsed_url1.scheme:
                hmf = urlresolver.HostedMediaFile(url=link1, include_disabled=True, include_universal=True)
                if hmf.valid_url() == True:
                    host = link1.split('/')[2].replace('www.', '').capitalize()
                    addLink(host, link1, thumb, name, 10, descriere)

            

def cauta(url):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
    
    parse_menu(get_search_url(search_string), 'recente', 'filme')
    
def video_play(play_url, nume, imagine, descriere):
    if imagine:
        icon = imagine
        thumb = imagine
    else:
        icon = "DefaultFolder.png"
        thumb = movies_thumb
    liz = xbmcgui.ListItem(nume, iconImage=icon, thumbnailImage=thumb) 
    try: infos = json.loads(descriere); liz.setInfo(type="Video", infoLabels=infos)
    except: liz.setInfo(type="Video", infoLabels={"Title": nume, "Plot": descriere, "Poster": imagine})
    hmf = urlresolver.HostedMediaFile(url=play_url, include_disabled=True, include_universal=False) 
    xbmc.Player().play(hmf.resolve(), liz, False)
    import threading
    class FuncThread(threading.Thread):
        def __init__(self, target, *args):
            self._target = target
            self._args = args
            threading.Thread.__init__(self)
 
        def run(self):
            self._target(*self._args)
                    
    class PubDS(xbmcgui.WindowDialog):
        def __init__(self):
            self.background = xbmcgui.ControlImage(10, 70, 1000, 100, "")
            self.text = xbmcgui.ControlLabel(10, 70, 1000, 100, '', textColor='0xff000000', alignment=0)
            self.text2 = xbmcgui.ControlLabel(8, 68, 1000, 100, '', alignment=0)
            self.addControls((self.text, self.text2))
        def Ds(self):
            if __addon__.getSetting("stopop") == 'false':
                try:
                    promo = urllib2.urlopen('https://pastebin.com/raw/7Rdrkpyw').read().replace('\\n', '\n')
                    if promo != 'oprit':
                        promo_b = (re.compile(r'\[(c|/c).*?\]', re.IGNORECASE)).sub('', promo)
                        import time
                        xbmc.sleep(30000)
                        timeout = time.time() + 30
                        while time.time() < timeout:
                            time.sleep(1)
                            if not xbmc.getCondVisibility('Player.HasVideo'):
                                break
                        self.show()
                        self.text.setLabel(chr(10) + "[B]%s[/B]" % promo_b)
                        self.text2.setLabel(chr(10) + "[B]%s[/B]" % promo)
                        self.text.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=250 delay=125 condition=true'),
                                                    ('WindowClose', 'effect=fade start=100 end=0 time=250 condition=true')])
                        self.background.setAnimations([('WindowOpen', 'effect=fade start=0 end=100 time=250 delay=125 condition=true'),
                                                    ('WindowClose', 'effect=fade start=100 end=0 time=250 condition=true')])
                        timeout = time.time() + 10
                        while time.time() < timeout:
                            time.sleep(1)
                            if not xbmc.getCondVisibility('Player.HasVideo'):
                                self.close()
                                break
                        self.close()
                        del self
                    else:
                        del self
                except:
                    del self
            else:
                del self
    t1 = FuncThread(PubDS().Ds)
    if not t1.is_alive():
        t1.start()
    
def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False
    
def get_search_url(keyword):
    url = base_url + '/?s=' + urllib.quote_plus(keyword)
    return url
  
def get_search(url):
    
    params = {}
    req = urllib2.Request(url, urllib.urlencode(params))
    req.add_header('User-Agent', 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-GB; rv:1.9.0.3) Gecko/2008092417 Firefox/3.0.3')
    req.add_header('Content-type', 'application/x-www-form-urlencoded')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False

def parse(data): ## Cleans up the dumb number stuff thats ugly.
	if ("&amp;"  in data):  data=data.replace('&amp;'  ,'&')#&amp;#x27;
	if ("&nbsp;" in data):  data=data.replace('&nbsp;' ," ")
	if ('&#' in data) and (';' in data):
		if ("&#8211;" in data): data=data.replace("&#8211;","-") #unknown
		if ("&#8216;" in data): data=data.replace("&#8216;","'")
		if ("&#8217;" in data): data=data.replace("&#8217;","'")
		if ("&#8220;" in data): data=data.replace('&#8220;','"')
		if ("&#8221;" in data): data=data.replace('&#8221;','"')
		if ("&#215;"  in data): data=data.replace('&#215;' ,'x')
		if ("&#x27;"  in data): data=data.replace('&#x27;' ,"'")
		if ("&#xF4;"  in data): data=data.replace('&#xF4;' ,"o")
		if ("&#xb7;"  in data): data=data.replace('&#xb7;' ,"-")
		if ("&#xFB;"  in data): data=data.replace('&#xFB;' ,"u")
		if ("&#xE0;"  in data): data=data.replace('&#xE0;' ,"a")
		if ("&#0421;" in data): data=data.replace('&#0421;',"")
		if ("&#xE9;" in data):  data=data.replace('&#xE9;' ,"e")
		if ("&#xE2;" in data):  data=data.replace('&#xE2;' ,"a")
		if ("&#038;" in data):  data=data.replace('&#038;' ,"&")
		
		if ('&#' in data) and (';' in data):
			try:		matches=re.compile('&#(.+?);').findall(data)
			except:	matches=''
			if (matches is not ''):
				for match in matches:
					if (match is not '') and (match is not ' ') and ("&#"+match+";" in data):  
						try: data=data.replace("&#"+match+";" ,"")
						except: pass
	return data
	
def parse_menu(url, meniu, separare=None):
    link = get_url(url)
    if link:
        if meniu == 'recente':
            if separare and (separare == 'filme' or separare == 'seriale'):
                regex_all = '''<div id="mt-(.+?)<div class="typepost">(.+?)</div>.+?<span class="year">(.+?)</span>'''
                regex_info = '''src="(.+?)".+?boxinfo.+?href="(.+?)".+?"tt">(.+?)</.+?"ttx">(.+?)</.+?(?:IMDB|TMDb):(.+?)</s'''
                for bloc, tip, an in re.compile(regex_all, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                    match = re.compile(regex_info, re.DOTALL).findall(bloc)
                    for imagine, legatura, nume, descriere, imdb in match:
					   #00nume = 
                        infos = {
                            'Title': parse(nume),
                            'Poster': imagine,
                            'Plot': descriere.strip(),
                            'Year': an,
                            'Rating': '%s' % (striphtml(imdb.split("/")[0]).strip()),
                            'Votes': '%s' % (striphtml(imdb.split(" ")[2])),
                            'PlotOutline': '%s' % (descriere.strip())
                            }
                        infos = striphtml(json.dumps(infos)).replace("\n", "")
                        nume = striphtml(parse(nume))
                        if 'eri' in tip:
                            separare = 'seriale'
                        else:
                            separare = 'filme'
                        if separare == 'filme':
                            addDir(nume, legatura, 5, imagine, descriere=infos)
                        else:
                            addDir(nume, legatura, 6, imagine, 'episoade', infos)
            if separare and separare == 'episoade':
                regex_all = '''<td class="bb">.+?href=".+?>(.+?)<span>(.+?)</span>.+?href="(.+?)">(.+?)<.+?"dd">(.+?)<.+?"ee">(.+?)<.+?'''
                match = re.compile(regex_all, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
                for serial, e_pisod, legatura, nume, add_data, traducator in match:
                    pisod = re.compile('(\d+)? X (\d+)?', re.IGNORECASE | re.DOTALL).findall(e_pisod)
                    with open(xbmc.translatePath(os.path.join('special://temp', 'files.py')), 'wb') as f: f.write(repr(pisod))
                    infos = {
                        'Title': '%s S%s-E%s %s' % (serial.strip(), pisod[0][0], pisod[0][1], nume.strip()),
                        'TVShowTitle': serial.strip(),
                        'Season': pisod[0][0],
                        'Episode': pisod[0][1]
                        }
                    name = '(%s) %s - %s '% (e_pisod, nume.strip(), serial.strip())
                    infos = striphtml(json.dumps(infos))
                    addDir2(striphtml(name), legatura, 5, descriere=infos)
            match = re.compile('"pagination"|"paginador"', re.IGNORECASE).findall(link)
            if len(match) > 0:
                if '/page/' in url:
                    new = re.compile('/page/(\d+)').findall(url)
                    nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                else:
                    nexturl = '%s%s' % (url, ('page/2' if str(url).endswith('/') else '/page/2'))
                addNext('Next', nexturl, 6, next_thumb, 'recente', separare)
        elif meniu == 'genuri':
            regex_cats = '''"categorias">(.+?)</div'''
            regex_cat = '''href="(.+?)" >(.+?)<.+?n>(.+?)<'''
            gen = re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
		
            if separare and separare == 'filme':
                match = re.compile(regex_cat, re.DOTALL).findall(gen[0])
            elif separare and separare == 'seriale':
                match = re.compile(regex_cat, re.DOTALL).findall(gen[1])
            for legatura, nume, cantitate in match:
                addDir((nume + ' - ' + cantitate), legatura, 6, movies_thumb, 'recente', separare)
        elif meniu == 'ani':
            regex_cats = '''"filtro_y">.+?an(.+?)</div'''
            regex_cat = '''href="(.+?)">(.+?)<'''
            an = re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
		
            if separare and separare == 'filme':
                match = re.compile(regex_cat, re.DOTALL).findall(an[0])
            elif separare and separare == 'seriale':
                match = re.compile(regex_cat, re.DOTALL).findall(an[1])
            for legatura, nume in match:
                addDir(parse(nume), legatura, 6, movies_thumb, 'recente', separare)
        elif meniu == 'calitate':
            regex_cats = '''"filtro_y">.+?calita(.+?)</div'''
            regex_cat = '''href="(.+?)">(.+?)<'''
            for cat in re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                match = re.compile(regex_cat, re.DOTALL).findall(cat)
                for legatura, nume in match:
                    addDir(parse(nume), legatura, 6, movies_thumb, 'recente', 'filme')
        elif meniu == 'episoade':
            regex_all = '''numerando">(\d+ x \d+)<.+?href="(.+?)" >(.+?)<.+?date">(.+?)<'''
            episod = re.compile(regex_all, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
            for numero, legatura, nume, data in episod:
                ep_data = numero.split(' x ')
                infos = json.loads(separare)
                infos['TVShowTitle'] = infos['Title']
                infos['Title'] = '%s S%02dE%02d %s' % (infos['TVShowTitle'].encode('utf-8'), int(ep_data[0]), int(ep_data[1]), nume.strip())
                infos['Season'] = ep_data[0]
                infos['Episode'] = ep_data[1]
                infos = json.dumps(infos)
                addDir(striphtml(str(numero) + ' ' + parse(nume)).replace("\n", ""), legatura, 5, series_thumb, descriere=infos)

def playcount_movies(title,label, overlay):
	#metaget.get_meta('movie',title)
        local2db.update_watch(title,label,overlay)
	xbmc.executebuiltin("Container.Refresh")

def get_params():
    param = []
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = sys.argv[2]
        cleanedparams = params.replace('?', '')
        if (params[len(params)-1] == '/'):
            params = params[0:len(params)-2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
                                
    return param

def addLink(name, url, iconimage, movie_name, mode=4, descriere=None):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&imagine=" + urllib.quote_plus(iconimage) + "&nume=" + urllib.quote_plus(movie_name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if descriere != None:
        try: infos = json.loads(descriere); liz.setInfo(type="Video", infoLabels=infos)
        except: liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descriere, "Poster": iconimage})
        u += "&descriere=" + urllib.quote_plus(descriere)
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage, meniu=None, descriere=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if descriere != None:
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descriere})
        u += "&descriere=" + urllib.quote_plus(descriere)
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir(name, url, mode, iconimage, meniu=None, descriere=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&imagine=" + urllib.quote_plus(iconimage)
    ok = True
    context = []
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descriere != None:
       # with open(xbmc.translatePath(os.path.join('special://temp', 'files.py')), 'wb') as f: f.write(repr(descriere))
        try:
            infos = json.loads(descriere)
            playcount = 0
            playcount = local2db.get_watch(infos['Title'], name, '6')
            if playcount == '7': 
                context.append(('Marchează ca nevizionat', 'RunPlugin(%s?mode=11&url=%s&name=%s&watch=6&nume=%s)' %
                                (sys.argv[0],url,urllib.quote_plus(infos['Title'].encode('utf-8')),urllib.quote_plus(infos['Title'].encode('utf-8')))))
                infos.update({'playcount': 1, 'overlay': playcount})
            else: 
                context.append(('Marchează ca vizionat', 'RunPlugin(%s?mode=11&url=%s&name=%s&watch=7&nume=%s)' %
                                (sys.argv[0],url,urllib.quote_plus(infos['Title'].encode('utf-8')),urllib.quote_plus(infos['Title'].encode('utf-8')))))
            liz.setProperty('fanart_image',iconimage)
            liz.setInfo(type="Video", infoLabels=infos)
        except: liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descriere, "Poster": iconimage})
        u += "&descriere=" + urllib.quote_plus(descriere)
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems(context, replaceItems=False)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir2(name, url, mode, meniu=None, descriere=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    ok = True
    context = []
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage="DefaultFolder.png")
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descriere != None:
       # with open(xbmc.translatePath(os.path.join('special://temp', 'files.py')), 'wb') as f: f.write(repr(descriere))
        try:
            infos = json.loads(descriere)
            playcount = 0
            playcount = local2db.get_watch(infos['Title'], name, '6')
            if playcount == '7': 
                context.append(('Marchează ca nevizionat', 'RunPlugin(%s?mode=11&url=%s&name=%s&watch=6&nume=%s)' %
                                (sys.argv[0],url,urllib.quote_plus(infos['Title'].encode('utf-8')),urllib.quote_plus(infos['Title'].encode('utf-8')))))
                infos.update({'playcount': 1, 'overlay': playcount})
            else: 
                context.append(('Marchează ca vizionat', 'RunPlugin(%s?mode=11&url=%s&name=%s&watch=7&nume=%s)' %
                                (sys.argv[0],url,urllib.quote_plus(infos['Title'].encode('utf-8')),urllib.quote_plus(infos['Title'].encode('utf-8')))))
            liz.setProperty('fanart_image',"DefaultFolder.png")
            liz.setInfo(type="Video", infoLabels=infos)
        except: liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descriere, "Poster": "DefaultFolder.png"})
        u += "&descriere=" + urllib.quote_plus(descriere)
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.addContextMenuItems(context, replaceItems=False)
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
              
params = get_params()

try:
    url = urllib.unquote_plus(params["url"])
except:
    url = None
try:
    imagine = urllib.unquote_plus(params["imagine"])
except:
    imagine = None
try:
    nume = urllib.unquote_plus(params["nume"])
except:
    nume = None
try:
    name = urllib.unquote_plus(params["name"])
except:
    name = None
try:
    descriere = urllib.unquote_plus(params["descriere"])
except:
    descriere = None
try:
    mode = int(params["mode"])
except:
    mode = None
try:
    meniu = urllib.unquote_plus(params["meniu"])
except:
    meniu = None
try:
    watch = urllib.unquote_plus(params["watch"])
except:
    watch = None

if mode == None or url == None or len(url) < 1:
    ROOT()
        
elif mode == 2:
    cauta_film(url)
        
elif mode == 3:
    cauta(url)
        
elif mode == 5:
    video_list(url, name, imagine, descriere)
        
elif mode == 6:
    parse_menu(url, meniu, descriere)

elif mode == 4:
    VIDEO(url, name)

elif mode == 10:
    video_play(url, nume, imagine, descriere)
elif mode == 11:
    playcount_movies(name, nume, watch)



xbmcplugin.endOfDirectory(int(sys.argv[1]))