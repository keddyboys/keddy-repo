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

if not xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'):
    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.module.urlresolver)')

try:
    import urlresolver
except:
    pass

settings = xbmcaddon.Addon(id='plugin.video.desene3dcom')
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
    if not mode == 2:
        addDir('Adaugate recent', 'http://desene3d.com', 6, movies_thumb, 'filme')
        addDir('Categorii', 'http://desene3d.com', 6, movies_thumb, 'categorii')
        addDir('Dupa ani', 'http://desene3d.com', 6, movies_thumb, 'ani')
        #addDir('Seriale', 'http://desene3d.com/index/seriale_tv/0-9', 6, movies_thumb, 'seriale')
        addDir('Cauta', 'http://desene3d.com', 3, search_thumb)
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
 
def CAUTA_VIDEO_LIST(url, name):
    link = get_search(url)
    links = re.compile('((?:varianta \d+).+?|)(?:<iframe.+?src="((?:[htt]|[//]).+?)" w| <td><a href="(.+?)")', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    for nume, m_link, show in links:
        if m_link.startswith("//"):
            m_link = 'http:' + m_link #//ok.ru fix
        parsed_url1 = urlparse.urlparse(m_link)
        if parsed_url1.scheme:
            hmf = urlresolver.HostedMediaFile(url=m_link, include_disabled=True, include_universal=True)
            if hmf.valid_url() == True:
                host = m_link.split('/')[2].replace('www.', '').capitalize()
                sxaddLink((nume.strip() + ': ' + host), m_link, movies_thumb, name, 10, name)
        

def CAUTA(url):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() == False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
        
    
    parse_menu(get_search_url(search_string), 'filme')
    
def SXVIDEO_GENERIC_PLAY(sxurl, mname, desc):
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=movies_thumb)
    liz.setInfo(type="Video", infoLabels={"Title": mname, "Plot": desc})
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

def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return cleantext


def get_search_url(keyword):
    url = 'http://desene3d.com/search/?q=' + urllib.quote_plus(keyword)
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
        url = 'http://desene3d.com'
    link = get_url(url)
    if meniu == 'ani':
        an = datetime.datetime.now().year
        while (an > 1939):
            legatura = url + '/search/Filme ' + str(an)
            addDir(str(an), legatura, 6, movies_thumb, 'filme')
            an -= 1
    if meniu == 'filme':
        match = re.compile('<div class="eTitle.+?<a href="(.+?)">(.+?)</div', re.DOTALL).findall(link)
        #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(match))
        for legatura, nume in match:
            nume = cleanhtml(nume)
            legatura = legatura if legatura.startswith("http://") else 'http://desene3d.com' + legatura
            addDir(nume, legatura, 5, movies_thumb, None, nume)
    elif meniu == 'categorii':
        regex_menu = '''div class="sidebox.+?categorii(.+?)</section>'''
        regex_submenu = '''href="(.+?)".+?>(.+?)<'''
        for categorie in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(categorie)
            for legatura, nume in match:
                legatura = 'http://desene3d.com' + legatura
                addDir(nume, legatura, 6, movies_thumb, 'filme')
    elif meniu == 'seriale':
        match = re.compile('<td><a href="(.+?)"><b.*?>(.+?)</b', re.DOTALL).findall(link)
        for legatura, nume in match:
            nume = cleanhtml(nume)
            legatura = legatura if legatura.startswith("http://") else 'http://desene3d.com' + legatura
            addDir(nume, legatura, 5, movies_thumb, None, nume)
    nexturl = False
    pagination = re.compile('pagesBlockuz(\d)', re.IGNORECASE).findall(link)
    if (len(pagination) > 0) and ((meniu != 'categorii') and (meniu != 'ani')):
        if pagination[0] == '1':
            s_new = re.compile('/search/').findall(url)
            s_new_1 = re.compile('/search/\?q=').findall(url)
            new = re.compile('/\?page(\d+)').findall(url)
            if new and not s_new:
                if re.compile('/?page' + str(int(new[0]) + 1), re.IGNORECASE).findall(link):
                    nexturl = re.sub('/?page(\d+)', '/?page' + str(int(new[0]) + 1), url)
            elif not new and not s_new:
                if re.compile('/?page2', re.IGNORECASE).findall(link):
                    nexturl = url + '/?page2'
            elif s_new_1:
                new_s = re.compile(';p=(\d+);').findall(url)
                if new_s:
                    if re.compile(';p=' + str(int(new_s[0]) + 1) + ';', re.IGNORECASE).findall(link):
                        nexturl = re.sub(';p=(\d+);', ';p=' + str(int(new_s[0]) + 1) + ';', url)
                else:
                    nexturl = url + ';t=1;p=2;md='   
            elif s_new and not s_new_1:
                nexturl = re.sub('/search/', '/search/?q=', url)
                nexturl = nexturl.replace(" ", "+") + ';t=1;p=2;md='
                
        elif pagination[0] == '2':
            new = re.compile('/\d+-(\d+)').findall(url)
            if new:
                if re.compile((re.sub('-(\d+)', '-' + str(int(new[0]) + 1), url[-6:])), re.IGNORECASE).findall(link):
                    nexturl = re.sub('-(\d+)', '-' + str(int(new[0]) + 1), url)
            else:
                if re.compile((url[-6:] + '-2'), re.IGNORECASE).findall(link):
                    nexturl = url + '-2'
        if nexturl:
            addNext('Next', nexturl, 6, next_thumb, 'filme')
    
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
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&mname=" + urllib.quote_plus(movie_name) + "&desc=" + urllib.quote_plus(descriere)
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
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if meniu != None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descriere != None:
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descriere})
        name_all = re.compile('^(.*?)(?:episodul|sezonul).*', re.IGNORECASE).findall(name)
        if len(name_all) > 0:
            cm = []
            url_all = 'http://desene3d.com/search/?q=' + name_all[0].replace(" ", "+")
            cm.append((name_all[0], 'XBMC.Container.Update(%s?mode=2&url=%s&meniu=filme)' % (sys.argv[0], urllib.quote_plus(url_all))))
            liz.addContextMenuItems(cm, replaceItems=False)
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
    desc = urllib.unquote_plus(params["desc"])
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
    parse_menu(url, 'filme')

elif mode == 3:
    CAUTA(url)
        
elif mode == 5:
    CAUTA_VIDEO_LIST(url, name)
        
elif mode == 6:
    parse_menu(url, meniu)

elif mode == 4:
    VIDEO(url, name)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url, mname, desc)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
