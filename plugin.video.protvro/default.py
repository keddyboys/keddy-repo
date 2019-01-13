import os
import re
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


website = 'http://protvplus.ro'

__addon__ = xbmcaddon.Addon()
__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
search_thumb   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'media', 'search.png')).decode("utf-8")
movies_thumb   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'media', 'movies.png')).decode("utf-8")
next_thumb   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'media', 'next.png')).decode("utf-8")

sys.path.append (__resource__)
import requests
ua = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36"

def ROOT():
    addDir('Seriale', 'http://protvplus.ro/', 23, movies_thumb, 'seriale')
    addDir('Emisiuni', 'http://protvplus.ro/', 23, movies_thumb, 'emisiuni')
    addDir('Stirile ProTV', 'http://protvplus.ro/', 23, movies_thumb, 'stiri')
    addDir('Cauta', 'http://protvplus.ro/', 3, search_thumb)

def CAUTA(url, autoSearch=None):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
        
    if autoSearch is None:
        autoSearch = ""
    
    parse_menu(get_search_url(search_string), 'emlink')
    
def play_video(sxurl, icon):
    print "icon = " + icon
    s = requests.Session()
    url = website + sxurl
    link = get_search(url)
    try:
        match = re.compile('<meta property="og:title" content="(.+?)".+?clipSource =.+?"(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            m3url = match[0][1]
            title = match[0][0]
            for line in requests.get(m3url).text.split('\n'):
                if not line.startswith("#") and len(line) > 0:
                    m3url = re.sub((m3url.rsplit('/', 1)[-1]), (re.sub("\n", "", line)), m3url)
                    break
        ###Big thanks to Shani for this###
        ##################################
            headers = {'User-Agent': ua, 'Referer': url}
            s.get("http://drmapi.protv.ro/hlsengine/prepare/", headers=headers)
            play_url = m3url + "|Cookie=PHPSESSID=" + s.cookies['PHPSESSID'] + ";SERVERID=" + s.cookies['SERVERID'] + ";&Origin=" + website + "&Referer=" + url + "&User-Agent=" + ua
        ###################################
        #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(play_url))
            item = xbmcgui.ListItem(title, iconImage=icon, thumbnailImage=icon)
            xbmc.Player().play(play_url, item)
    except:
        xbmc.executebuiltin((u'Notification(%s,%s)' % ('ProTV', 'Video indisponibil')))
    
def get_search_url(keyword, offset=None):
    url = 'http://protvplus.ro/hledat?q=' + urllib.quote_plus(keyword) + '&searchsend=Search'
    return url

def get_search(url):
    header = {'User-Agent': ua,
        'Content-type': 'application/x-www-form-urlencoded'}
    try:
        response = requests.get(url, headers=header)
        link = response.text
        return link
    except:
        return False

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

def sxaddLink(name, url, iconimage, movie_name, mode=4, descript=None):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&icon=" + urllib.quote_plus(iconimage)
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.addContextMenuItems([('Watched/Unwatched', 'Action(ToggleWatched)')])
    if descript != None:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir(name, url, mode, iconimage, meniu=None, descript=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descript != None:
        u += "&descriere=" + urllib.quote_plus(descript)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if descript != None:
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
      
def parse_menu(url, meniu):
    if url == None:
        url = 'http://protvplus.ro/'
    if meniu == 'emisiuni' or meniu == 'seriale' or meniu == 'stiri':
        url = url + meniu + '/'
        link = get_search(url)
        match = re.compile('<li><a href="(.+?)".+?class="title_new">(.+?)<.+?label" >(.+?)<', re.IGNORECASE | re.MULTILINE).findall(link)
    elif meniu == 'emlink':
        link = get_search(url)
        match = re.compile('<a href="(.+?)">\n\s*<span.+?\n\s*<img src=\'(.+?)\'\s*.+?\n\s*.+?\n\s*.+?\n.+?\n.+?<a href.+?>(.+?)</a>', re.IGNORECASE | re.MULTILINE).findall(link)
    if len(match) > 0:
        print match
        if meniu == 'emisiuni' or meniu == 'seriale' or meniu == 'stiri':
            for link, nume, nrep in match:
                image = "DefaultVideo.png"
                url = website + link
                addDir(nume, url, 23, image, 'emlink')
        elif meniu == 'emlink':
            for linkem, image, name in match:
                sxaddLink(name, linkem, image, name, 10)
	  
	  
    match = re.compile('<a href="(.+?)" class="page">', re.IGNORECASE).findall(link)
    if len(match) > 0:
        page_num = re.compile('\?page=(\d+)', re.IGNORECASE).findall(url)
        if page_num:
            pagen = int(page_num[0]) + 1
            nexturl = re.sub('\?page=(\d+)', '?page=' + str(pagen), url)
        else:
            nexturl = url.rstrip('/') + '?page=2'
        addNext('Next', nexturl, 23, next_thumb, 'emlink')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')             
params = get_params()

try:
    url = urllib.unquote_plus(params["url"])
except:
    url = None
try:
    mode = int(params["mode"])
except:
    mode = None
try:
    meniu = urllib.unquote_plus(params["meniu"])
except:
    meniu = None
try:
    icon = urllib.unquote_plus(params["icon"])
except:
    icon = None


#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)

if mode == None or url == None or len(url) < 1:
    ROOT()
        
elif mode == 3:
    CAUTA(url)
        
elif mode == 23:
    parse_menu(url, meniu)

elif mode == 10:
    play_video(url, icon)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
