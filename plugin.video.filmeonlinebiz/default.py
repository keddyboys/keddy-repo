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

if not xbmc.getCondVisibility('System.HasAddon(script.mrknow.urlresolver)'):
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.mrknow.urlresolver)')

settings = xbmcaddon.Addon(id='plugin.video.filmeonlinebiz')
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
base_url = 'http://www.filmeonline.biz'
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

def ROOT():
    addDir('Recente', base_url, 6, movies_thumb, 'recente')
    addDir('Genuri', base_url, 6, movies_thumb, 'genuri')
    addDir('Ani', base_url, 6, movies_thumb, 'ani')
    
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
            
 
def video_list(url, name, iconimage=None):
    link = get_search(url)
    thumb = iconimage
    regex_lnk = '''iframe.+?src="((?:[htt]|[//]).+?)"'''
    regex_infos = '''"description">(.+?)</'''
    match_lnk = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
    match_nfo = re.compile(regex_infos, re.IGNORECASE | re.DOTALL).findall(link)
    for link1 in match_lnk:
            if link1.startswith("//"):
                link1 = 'http:' + link1 #//ok.ru fix
            parsed_url1 = urlparse.urlparse(link1)
            if parsed_url1.scheme:
                hmf = urlresolver.HostedMediaFile(url=link1, include_disabled=True, include_universal=True)
                if hmf.valid_url() == True:
                    host = link1.split('/')[2].replace('www.', '').capitalize()
                    addLink(host, link1, thumb, name, 10, striphtml(match_nfo[0]))

            

def cauta(url, autoSearch=None):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
        
    if autoSearch is None:
        autoSearch = ""
    
    cauta_film(get_search_url(search_string + "" + autoSearch))
    
def video_play(play_url, nume, imagine, descriere):
    if imagine:
        icon = imagine
        thumb = imagine
    else:
        icon = "DefaultFolder.png"
        thumb = movies_thumb
    liz = xbmcgui.ListItem(nume, iconImage=icon, thumbnailImage=thumb) 
    liz.setInfo(type="Video", infoLabels={"Title": nume, "Plot": descriere})
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
    
def get_search_url(keyword, offset=None):
    url = base_url + '/search/?q=' + urllib.quote_plus(keyword)
    
    if offset != None:
        url += "?offset=" + offset
    
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

def parse_menu(url, meniu):
    link = get_url(url)
    if meniu == 'recente':
        regex_menu = '''<div class="kutresim film-kutu-title">(.+?)</div>.?</div>'''
        regex_submenu = '''href="(.+?)".+?title="(.+?)".*img.*src="(.+?)"'''
        if link:
            for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
                for legatura, nume, imagine in match:
                    nume = nume.split(" &#8211; ")
                    #link_fix = base_url + legatura
                    addDir(striphtml(nume[0]), legatura, 5, imagine)
            match = re.compile('"pagination"', re.IGNORECASE).findall(link)
            if len(match) > 0:
                if '/page/' in url:
                    new = re.compile('/page/(\d+)').findall(url)
                    nexturl = re.sub('/page/(\d+)', '/page/' + str(int(new[0]) + 1), url)
                else:
                    nexturl = url + "/page/2"
                print "NEXT " + nexturl
                addNext('Next', nexturl, 6, next_thumb, 'recente')
    elif meniu == 'genuri':
        regex_cats = '''<ul class="categories">(.+?)</ul'''
        regex_cat = '''href="(.+?)">(.+?)<'''
        if link:
            for cat in re.compile(regex_cats, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
                match = re.compile(regex_cat, re.DOTALL).findall(cat)
                for legatura, nume in match:
                    addDir(nume, legatura, 6, movies_thumb, 'recente')
    elif meniu == 'ani':
        an = datetime.datetime.now().year
        while (an > 1984):
            legatura = base_url + '/filme/' + str(an)
            addDir(str(an), legatura, 6, movies_thumb, 'recente')
            an -= 1

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
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descriere})
        u += "&descriere=" + urllib.quote_plus(descriere)
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir(name, url, mode, iconimage, meniu=None):
    name = re.sub('&#39;','\'', name)
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&imagine=" + urllib.quote_plus(iconimage)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
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

if mode == None or url == None or len(url) < 1:
    ROOT()
        
elif mode == 2:
    cauta_film(url)
        
elif mode == 3:
    cauta(url)
        
elif mode == 5:
    video_list(url, name, imagine)
        
elif mode == 6:
    parse_menu(url, meniu)

elif mode == 4:
    VIDEO(url, name)

elif mode == 10:
    video_play(url, nume, imagine, descriere)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
