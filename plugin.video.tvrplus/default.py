import os
import re
import sys
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


website = 'http://www.tvrplus.ro'

settings = xbmcaddon.Addon(id='plugin.video.tvrplus')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')


def ROOT():
    addDir('Emisiuni', 'http://www.tvrplus.ro', 23, movies_thumb, 'emisiuni')
    addDir('Live', 'http://www.tvrplus.ro/live-tvr-1', 23, movies_thumb, 'live')
    addDir('Cauta', 'http://nobalance.tvrplus.ro', 3, search_thumb)
         

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
    
    parse_menu(get_search_url(search_string), 'search', urllib.quote_plus(search_string))
    
def SXVIDEO_GENERIC_PLAY(sxurl):
    link = get_search(sxurl)
    match = re.compile('file: "http://(.+?)"', re.IGNORECASE | re.MULTILINE).findall(link)
    match2 = re.compile('<meta property="og:title" content="(.+?)".+?\n\s*.+?content="(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    if len(match) > 0:
        if len(match2) > 0:
            #var player_config.+?\n\s*.+?\n\s*"url": "(.+?)",(\n\s*.+?){15}url": "(.+?)",\n\s*.+?netConnectionUrl": \'(.+?)\'
            iconimage = "DefaultVideo.png"
            item = xbmcgui.ListItem(match2[0][0], iconImage="DefaultVideo.png", thumbnailImage=iconimage)
            item.setInfo('video', {'Title': match2[0][0], 'Plot': match2[0][1]})
            xbmc.Player().play('http://' + match[0], item)

    
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
    url = 'http://nobalance.tvrplus.ro/cauta/cauta-ajax?termen=' + urllib.quote_plus(keyword)
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
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
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
      
def parse_menu(url, meniu, searchterm=None):
    if url == None:
        url = 'http://www.tvrplus.ro'
    if meniu == 'emisiuni':
        url = url + '/' + meniu
        link = get_search(url)
        match = re.compile('div class="emisiune.+?\n\s*<p.+?>(.+?)<.+?\n\s*<a href="(.+?)".+?data-original="(.+?)".+?\n\s*.+?\n\s*.+?\n\s*<p.+?>(.+?)</p><p>(.+?)<.+?\n\s*.+?<a href.+?">(.+?)<', re.IGNORECASE | re.MULTILINE).findall(link)
    elif meniu == 'emlink':
        link = get_search(url)
        match = re.compile('<li .+?\n\s*<a href="(.+?)".+?\n\s*.+?alt="(.+?)".+?\n\s*.+?">(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    elif meniu == 'search':
        link = get_search(url)
        match = re.compile('<a.+? href="(.+?)".+?alt="(.+?)".+?<a.+?>(.+?)</a.+?<p.+?>(.+?)<.+?">(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    elif meniu == 'live':
        link = get_search(url)
        match = re.compile('<li class="floatL" s.+?<a href="(.+?)".+?src="(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    if len(match) > 0:
        print match
        if meniu == 'emisiuni':
            for nume, legatura, imagine, posttv, data, descriere in match:
                linkem = website + legatura
                nume = nume + ' - ' + posttv + ' : ' + data
                descriere = posttv + ' - ' + data + '\n' + descriere
                addDir(nume, linkem, 23, imagine, 'emlink', descriere)
        elif meniu == 'emlink':
            for linkem, imagine, nume in match:
                linkem = website + linkem
                sxaddLink(nume, linkem, imagine, nume, 10)
        elif meniu == 'search':
            for legatura, imagine, titlu1, titlu2, descriere in match:
                nume = titlu1 + '-' + titlu2
                linkem = website + legatura
                sxaddLink(nume, linkem, imagine, nume, 10, descriere)
        elif meniu == 'live':
            for legatura, imagine in match:
                nume = re.sub('/live', '', legatura)
                nume = re.sub('-', ' ', nume)
                linkem = website + legatura
                sxaddLink(nume.upper(), linkem, imagine, nume, 10)
	    
    match = re.compile('pagina/(\d)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    if len(match) > 0:
        page_num = re.compile('pagina/(.+?)\?', re.IGNORECASE).findall(str(url))
        if len(page_num) > 0:
            pagen = int(page_num[0]) + 1
            nexturl = re.sub('pagina/(\d+)', 'pagina/' + str(pagen), url)
        else:
            nexturl = 'http://nobalance.tvrplus.ro/cauta/cauta-ajax/pagina/2?termen=' + str(searchterm)
        #f = open( '/storage/.kodi/temp/files.py', 'w' )
        #f.write( 'match = ' + repr(url) + '\n' )
        #f.close()  
        addNext('Next', nexturl, 23, next_thumb, 'search')
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')             
params = get_params()
url = None
mode = None
meniu = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    mode = int(params["mode"])
except:
    pass
try:
    meniu = urllib.unquote_plus(params["meniu"])
except:
    pass


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
    SXVIDEO_GENERIC_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
