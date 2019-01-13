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
    
try:
    import urlresolver
except:
    pass

settings = xbmcaddon.Addon(id='plugin.video.hindilovercom')
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
base_url = 'http://hindilover.net'

def ROOT():
    addDir('Recente', base_url + '/news/', 6, movies_thumb, 'recente')
    addDir('Cele mai vizionate', base_url + '/news/0-0-1-0-16-2', 6, movies_thumb, 'recente')
    addDir('Cele mai votate', base_url + '/news/0-0-1-0-16-3', 6, movies_thumb, 'recente')
    addDir('Filme Indiene', base_url + '/news/1-0-31', 6, movies_thumb, 'recente')
    addDir('Seriale Indiene Terminate', base_url, 6, movies_thumb, 'SerialIT')
    addDir('Seriale Indiene in desfasurare', 'desfasurare', 6, movies_thumb, 'SerialIT')
    addDir('Seriale Turcesti Terminate', 'desfasurare', 6, movies_thumb, 'SerialTT')
    addDir('Seriale Turcesti in desfasurare', base_url, 6, movies_thumb, 'SerialTT')
    addDir('Cauta', base_url, 3, search_thumb)
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('-', data)

def CAUTA_LIST(url):
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
            
 
def CAUTA_VIDEO_LIST(url):
    link = get_search(url)
    regex_lnk = '''iframe.+?src="([htt].+?)"'''
    match = re.compile(regex_lnk, re.IGNORECASE | re.DOTALL).findall(link)
    for link1 in match:
            if link1.startswith("//"):
                link1 = 'http:' + link1 #//ok.ru fix
            parsed_url1 = urlparse.urlparse(link1)
            if parsed_url1.scheme:
                hmf = urlresolver.HostedMediaFile(url=link1, include_disabled=True, include_universal=True)
                if hmf.valid_url() == True:
                    host = link1.split('/')[2].replace('www.', '').capitalize()
                    sxaddLink(host, link1, movies_thumb, link1, 10)

            

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
    
    CAUTA_LIST(get_search_url(search_string + "" + autoSearch))
    
def SXVIDEO_GENERIC_PLAY(sxurl):
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=movies_thumb); liz.setInfo(type="Video", infoLabels={"Title": name})
    hmf = urlresolver.HostedMediaFile(url=sxurl, include_disabled=True, include_universal=False) 
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
    desf = False
    match = []
    if url == None:
        url = base_url
    elif url == 'desfasurare':
        url = base_url
        desf = True
    link = get_url(url)
    if meniu == 'recente':
        regex_menu = '''<div class="image">(.+?)<!--<div class="fb'''
        regex_submenu = '''<a href="(.+?)".+?img src="(.+?)".+?h2>(.+?)</h2'''
        for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
            for legatura, imagine, nume in match:
                nume = striphtml(nume)
                link_fix = base_url + legatura
                addDir(nume, link_fix, 5, imagine)
        match = re.compile('"swchItem"', re.IGNORECASE).findall(link)
        if len(match) > 0:
            if '/stuff/' in url:
                new = re.compile('/\d+-(\d+)').findall(url)
                #with open(xbmc.translatePath(os.path.join('special://temp', 'files.py')), 'wb') as f: f.write(repr(nexturl))
            else:
                new = re.compile('/(\d+)-\d+-\d+$').findall(url)
            if new:
                if '/stuff/' in url:
                    nexturl = re.sub('-(\d+)', '-' + str(int(new[0]) + 1), url)
                else:
                    nexturl = re.sub('/(\d+)-', '/' + str(int(new[0]) + 1) + '-', url)
                print "NEXT " + nexturl
                addNext('Next', nexturl, 6, next_thumb, 'recente')
            else:
                if '/stuff/' in url:
                    nexturl = '%s%s' % (url, "-2")
                else:
                    new = re.compile('/\d+-\d+-(\d+)-\d+-\d+-\d+$').findall(url)
                    if new:
                        nexturl = re.sub('(?=\d+-\d+-)\d+(?=-\d+-\d+-\d+$)', str(int(new[0]) + 1), url)
                    else:
                        new = re.compile('/\?page(\d+)').findall(url)
                        if new:
                            nexturl = re.sub('page\d+', 'page' + (str(int(new[0]) + 1)), url)
                        else:
                            nexturl = url + '?page2'
                addNext('Next', nexturl, 6, next_thumb, 'recente')
    elif meniu == 'SerialT':
        match = re.compile('class="catsTdI".+?a href="(.+?)".+?class="abcdD.+?>(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            for legatura, nume in match:
                nume = striphtml(nume)
                addDir(nume, legatura, 6, movies_thumb, 'recente')
    elif meniu == 'SerialIT':
        regex_menu = '''<div id="myNa(?:v"|vs")(.+?) </div>.?</div>'''
        regex_submenu = '''class="catsTdI".+?a href="(.+?)".+?class="abcdD.+?>(.+?)<'''
        meniu = re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        match = re.compile(regex_submenu, re.DOTALL).findall((meniu[0] if desf else meniu[1]))
        for legatura, nume in match:
            nume = striphtml(nume)
            addDir(nume, legatura, 6, movies_thumb, 'recente')
    elif meniu == 'SerialTT':
        regex_menu = '''<div id="myNa(?:vss"|vsss")(.+?) </div>.?</div>'''
        regex_submenu = '''class="catsTdI".+?a href="(.+?)".+?class="abcdD.+?>(.+?)<'''
        meniu = re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        match = re.compile(regex_submenu, re.DOTALL).findall((meniu[0] if desf else meniu[1]))
        for legatura, nume in match:
            nume = striphtml(nume)
            addDir(nume, legatura, 6, movies_thumb, 'recente')
    elif meniu == 'turcesti':
        regex_menu = '''<div class="eTitle"(.+?)</div></td></tr></table><br />'''
        regex_submenu = '''<a href="(.+?)".+?>(.+?)</a>'''
        for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
            for legatura, nume in match:
                addDir(striphtml(nume), base_url + legatura, 5, movies_thumb)
        match = re.compile('"swchItem"', re.IGNORECASE).findall(link)
        if len(match) > 0:
            new = re.compile('/\?page(\d+)').findall(url)
            if new:
                nexturl = re.sub('\?page\d+', '?page' + (str(int(new[0]) + 1)), url)
            else:
                nexturl = url + '?page2'
            print "NEXT " + nexturl
            addNext('Next', nexturl, 6, next_thumb, 'turcesti')

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

def sxaddLink(name, url, iconimage, movie_name, mode=4):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
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
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok
              
params = get_params()
url = None
name = None
mode = None

try:
    url = urllib.unquote_plus(params["url"])
except:
    pass
try:
    name = urllib.unquote_plus(params["name"])
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
        
elif mode == 2:
    CAUTA_LIST(url)
        
elif mode == 3:
    CAUTA(url)
        
elif mode == 5:
    CAUTA_VIDEO_LIST(url)
        
elif mode == 6:
    parse_menu(url, meniu)

elif mode == 4:
    VIDEO(url, name)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
