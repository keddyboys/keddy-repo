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
    import urlresolver9 as urlresolver

settings = xbmcaddon.Addon(id='plugin.video.filmeonline2013biz')
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

def ROOT():
    addDir('Recent Adaugate', 'http://www.filmeonline2013.biz', 6, movies_thumb, 'recente')
    addDir('Genuri', 'http://www.filmeonline2013.biz', 6, movies_thumb, 'genuri')
    addDir('Cauta', 'http://www.filmeonline2013.biz/?s=', 3, search_thumb)
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def CAUTA_LIST(url):
    link = get_search(url)
    match = re.compile('<a class="entry-thumb" href="(.+?)" title="(.+?)".+?src="(.+?)".+?<p>(.+?)<', re.DOTALL).findall(link)
    for legatura, nume, imagine, descriere in match:
        addDir(nume, legatura, 5, imagine, None, descriere)
    match = re.compile('class=\'wp-pagenavi', re.IGNORECASE).findall(link)
    if len(match) > 0:
        new = re.compile('/(\d+)').findall(url)
        if new:
            nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
            print "NEXT " + nexturl
            addNext('Next', nexturl, 2, next_thumb)
        else:
            new = re.compile('page/(\d+)/').findall(url)
            if new:
                re.sub('page/\d+', 'page/' + (str(int(new[0]) + 1)), url)
            else:
                nexturl = re.sub('.biz/', '.biz/page/2/', url)
            addNext('Next', nexturl, 2, next_thumb)
        #f = open( '/storage/.kodi/temp/files.py', 'w' )
        #f.write( 'url = ' + repr(nexturl) + '\n' )
        #f.close()
 
def CAUTA_VIDEO_LIST(url, name):
    link = get_search(url)
    match = re.compile('<div class="entry-embed">.+?<iframe.+?src="(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    for m_link in match:
        if m_link.startswith("//"):
            m_link = 'http:' + m_link #//ok.ru fix
        parsed_url1 = urlparse.urlparse(m_link)
        if parsed_url1.scheme:
            if urlresolver.HostedMediaFile(m_link).valid_url():
                host = m_link.split('/')[2].replace('www.', '').capitalize()
                sxaddLink(host, m_link, movies_thumb, name, 10)

            

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
    
def SXVIDEO_GENERIC_PLAY(sxurl, mname):
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=movies_thumb); liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setInfo(type="Video", infoLabels={"Title": mname})
    hmf = urlresolver.HostedMediaFile(url=sxurl, include_disabled=True, include_universal=False) 
    xbmc.Player ().play(hmf.resolve(), liz, False)
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
    url = 'http://www.filmeonline2013.biz/?s=' + urllib.quote_plus(keyword)
    
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
    match = []
    if url == None:
        url = 'http://www.filmeonline2013.biz'
    link = get_url(url)
    if meniu == 'recente':
        match = re.compile('<a class="entry-thumb2" href="(.+?)" title="(.+?)".+?src="(.+?)"', re.DOTALL).findall(link)
        for legatura, nume, imagine in match:
            addDir(nume, legatura, 5, imagine)
        match = re.compile('class=\'wp-pagenavi', re.IGNORECASE).findall(link)
        if len(match) > 0:
            new = re.compile('/(\d+)').findall(url)
            if new:
                nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
                print "NEXT " + nexturl
                addNext('Next', nexturl, 6, next_thumb, 'recente')
            else:
                new = re.compile('page/(\d+)/').findall(url)
                if new:
                    re.sub('page/\d+', 'page/' + (str(int(new[0]) + 1)), url)
                else:
                    nexturl = url + '/page/2/'
                addNext('Next', nexturl, 6, next_thumb, 'recente')
    if meniu == 'nextgen':
        match = re.compile('<a class="entry-thumb" href="(.+?)" title="(.+?)".+?src="(.+?)".+?<p>(.+?)<', re.DOTALL).findall(link)
        for legatura, nume, imagine, descriere in match:
            addDir(nume, legatura, 5, imagine, None, descriere)
        match = re.compile('class=\'wp-pagenavi', re.IGNORECASE).findall(link)
        if len(match) > 0:
            new = re.compile('/(\d+)').findall(url)
            if new:
                nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
                print "NEXT " + nexturl
                addNext('Next', nexturl, 6, next_thumb, 'nextgen')
            else:
                new = re.compile('page/(\d+)/').findall(url)
                if new:
                    re.sub('page/\d+', 'page/' + (str(int(new[0]) + 1)), url)
                else:
                    nexturl = url + '/page/2/'
                addNext('Next', nexturl, 6, next_thumb, 'nextgen')
    elif meniu == 'genuri':
        regex_menu = '''<ul id="cat-nav" class="nav">(.+?)</ul>'''
        regex_submenu = '''href="(.+?)".+?>(.+?)<'''
        for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
            for legatura, nume in match:
                addDir(nume, legatura, 6, movies_thumb, 'nextgen')

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

def sxaddLink(name, url, iconimage, movie_name, mode=4, descriere=None):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&mname=" + urllib.quote_plus(movie_name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if descriere != None:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descriere})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    return ok

def addLink(name, url, iconimage, movie_name):
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
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
    CAUTA_VIDEO_LIST(url, name)
        
elif mode == 6:
    parse_menu(url, meniu)

elif mode == 4:
    VIDEO(url, name)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url, mname)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
