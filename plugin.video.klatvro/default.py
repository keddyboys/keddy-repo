# -*- coding: utf-8 -*-
import json
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

settings = xbmcaddon.Addon(id='plugin.video.klatvro')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
__url__ = 'https://www.kla.tv/'

def ROOT():
    addDir('Recente', 'https://www.kla.tv/index.php?a=showlanguage&lang=ro', 6, movies_thumb, 'movies')
    regex = '''<li><a href="index.php\?a=showportal">(.+?)</ul>'''
    regex_art = '''<a href="(.+?)">(.+?)<'''
    for art in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(get_search('https://www.kla.tv/index.php?a=showlanguage&lang=ro')):
        result = re.compile(regex_art, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(art)
        for legatura, nume in result:
            legatura = __url__ + legatura
            addDir(nume, legatura, 6, movies_thumb, 'movies')
    addDir('Cautare', __url__, 3, search_thumb)
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def CAUTA(url):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
    
    parse_menu(urllib.quote_plus(search_string), 'cautare', None)
    
def SXVIDEO_GENERIC_PLAY(sxurl, mname):
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=movies_thumb)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    xbmc.Player().play(sxurl, liz, False)
    
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
    url = __url__ + 'index.php?a=showsearch&search=' + urllib.quote_plus(keyword)
    
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

def parse_menu(url, meniu, offs):
    if offs is None:
        offs = 0
    match = []
    if url == None:
        url = __url__
    if meniu == 'movies':
        parsed = urlparse.parse_qs(urlparse.urlparse(url).query)
        try:
            typ = parsed['sendtyp']
        except:
            typ = ''
        try:
            category = parsed['category']
        except:
            category = ''
        try:
            act = parsed['a']
        except:
            act = ''
        typ = typ[0] if typ else ""
        a, offset = get_json(url, category, typ, act, offs)
        count = 1
        for list in a['data']:
            video_u = 'https://www.kla.tv/' if (('http') or ('https')) not in list['videopath'] else ''
            img_u = 'https://www.kla.tv/' if ('http://') or ('https://') not in list['img'] else ''
            link = video_u + list['videopath']
            descriere = list['desc']
            nume = list['title'] + ':' + list['originalVideoDate']
            imagine = img_u + list['img']
            #print list['videoTime']
            addLink(nume, link, imagine, nume, 10, descriere)
            count += 1
            if count > 24:
                offset = int(offset) + 24
                addNext('next', url, 6, next_thumb, 'movies', offset)
            
    elif meniu == 'cautare':
        a, offset = get_json(url, None, None, 'cautare')
        for list in a['data']:
            id = list['shortlink']
            nume = list['title']
            imagine = __url__ + list['img']
            data = ('type=viewVideo&progress=0&videoId=' + id)
            headers = {'Content-type': 'application/json;charset=utf-8', 'Accept': 'application/json, text/plain, */*', 'Host': 'www.kla.tv', 'Referer': __url__ + id}
            r = urllib2.Request(__url__, data=data, headers=headers)
            f = urllib2.urlopen(r)
            response = f.read()
            f.close
            match = re.compile('file: "(.+?)"').findall(response)
            link = __url__ + match[0]
            addLink(nume, link, imagine, nume, 10)

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

def get_json(url, category=None, typ=None, act=None, offset=None, count=None):
    if act == 'cautare':
        data = {"mode":"action", "data":{"type":"getSearchResultForTitels", "searchinput":str(url)}}
        headers = {'Content-type': 'application/json;charset=utf-8', 'Accept': 'application/json, text/plain, */*', 'Host': 'www.kla.tv', 'Referer': 'https://www.kla.tv/ro', 'Accept-Language':'ro,en-US;q=0.7,en;q=0.3', 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        r = urllib2.Request('https://www.kla.tv/ro', data=json.dumps(data), headers=headers)
        f = urllib2.urlopen(r)
        response = f.read()
        a = json.loads(response)
        f.close()
    else:
        cats = {'bildung':1, 'gesundheit':2, 'ideologie':3, 'kultur':4, 'medien':5, 'politik':6, 'rechtundunrecht':7, 'terror':8, 'umwelt':9, 'technik':10, 'wirtschaft':11, 'wissenschaft':12}
        if category:
            if category[0] in cats:
                category = cats[category[0]]
        if not offset:
            offset = 0
        data = {"mode":"action", "data":{"type":"loadingNextVideos", "category":category, "sendtyp":typ, "offset":int(offset), "count":24, "langid":"8"}}
        headers = {'Content-type': 'application/json;charset=utf-8', 'Accept': 'application/json, text/plain, */*', 'Host': 'www.kla.tv', 'Referer': url, 'Accept-Language':'ro,en-US;q=0.7,en;q=0.3', 'User-Agent':'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'}
        r = urllib2.Request(url, data=json.dumps(data), headers=headers)
        f = urllib2.urlopen(r)
        response = f.read()
        #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(data))
        a = json.loads(response)
        f.close()
        
    return a, offset

def addLink(name, url, iconimage, movie_name, mode=4, descriere=None):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name.encode('utf8')) + "&mname=" + urllib.quote_plus(movie_name.encode('utf8'))
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if descriere != None:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descriere})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage, meniu=None, offset=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if offset != None:
        u += "&offs=" + str(offset)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir(name, url, mode, iconimage, meniu=None, descriere=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if descriere != None:
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descriere})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
              
params = get_params()
url = None
name = None
mode = None
offs = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
except:
    pass
try:
    mname = urllib.unquote_plus(params["mname"])
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
try:
    offs = int(params["offs"])
except:
    pass
#print "Mode: "+str(mode)
#print "URL: "+str(url)
#print "Name: "+str(name)
if mode == None or url == None or len(url) < 1:
    ROOT()

elif mode == 3:
    CAUTA(url)

elif mode == 6:
    parse_menu(url, meniu, offs)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url, mname)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
