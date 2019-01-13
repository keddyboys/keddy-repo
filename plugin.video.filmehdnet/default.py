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

#if not xbmc.getCondVisibility('System.HasAddon(script.module.urlresolver)'):
#    xbmc.executebuiltin('XBMC.RunPlugin(plugin://script.module.urlresolver)')

try:
    import urlresolver
except:
    pass


settings = xbmcaddon.Addon(id='plugin.video.filmehdnet')
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
        addDir('Recent Adaugate', 'http://filmehd.net/page/1', 6, movies_thumb, 'filme')
        addDir('Categorii', 'http://filmehd.net', 6, movies_thumb, 'categorii')
        addDir('Dupa ani', 'http://filmehd.net/despre/', 6, movies_thumb, 'ani')
        addDir('Seriale', 'http://filmehd.net/seriale', 6, movies_thumb, 'filme')
        addDir('De colectie', 'http://filmehd.net/filme-vechi', 6, movies_thumb, 'filme')
        addDir('Cauta', 'http://filmehd.net/?s=', 3, search_thumb)
    else:
        import metainfo
        disp = metainfo.window()
        disp.get_n(name, nametwo)
        disp.doModal()
        del disp
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)
 
def CAUTA_VIDEO_LIST(url, name):
    link = get_search(url)
    match = re.compile('content_box">.+?<p>(.+?)</p>.+?js_content.php(.+?)\'', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    descriere = cleanhtml(match[0][0])
    jslink = 'http://filmehd.net/js_content.php' + match[0][1]
    jscontent = get_search(jslink)
    jscode = re.compile('=\\\'(.+?)\\\'|=\\\\\\\'(.+?)\\\\\\\'', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(jscontent)
    jsfix = re.compile('\|(.+?)\'.split', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(jscontent)
    pieces = ("|" + jsfix[0]).split("|")
    def lookup(code):
        word = code.group(0)
        try:
            piece = pieces[int(word)]
        except:
            piece = None
        return piece if piece else word
    jscodea = re.sub(r'\b\w+\b', lookup, jscode[1][1])
    jscodeb = jscode[0][0]
    alljs = jscodea + jscodeb
    links = []
    links = re.compile('<center>(.+?)</center>.+?src="(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(alljs)
    new_links = re.compile('<center>(.+?)</center>.+?src="(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
    links.extend(new_links)
    #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(links))
    for nume, m_link in sorted(links, key=lambda x: x[0]):
        if m_link.startswith("//"):
            m_link = 'http:' + m_link #//ok.ru fix
        parsed_url1 = urlparse.urlparse(m_link)
        if parsed_url1.scheme:
            hmf = urlresolver.HostedMediaFile(url=m_link, include_disabled=True, include_universal=True)
            if hmf.valid_url() == True:
                #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(na))
                host = m_link.split('/')[2].replace('www.', '').capitalize()
                sxaddLink((nume + ': ' + host), m_link, movies_thumb, name, 10, descriere)
        

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


def get_search_url(keyword, offset=None):
    url = 'http://filmehd.net/?s=' + urllib.quote_plus(keyword)
    
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
        url = 'http://filmehd.net'
    link = get_url(url)
    if meniu == 'ani':
        an = datetime.datetime.now().year
        while (an > 1929):
            legatura = url + 'filme-' + str(an)
            addDir(str(an), legatura, 6, movies_thumb, 'filme')
            an -= 1
    if meniu == 'filme':
        match = re.compile('<div id="post.+?a href="(.+?)" title="(.+?)".+?src="(.+?)"', re.DOTALL).findall(link)
        for legatura, nume, imagine in match:
            try:
                numeall = nume.split('&#8211;')
                numeen = re.sub("&#8217;", "'", numeall[0])
                numeen = re.sub("&#038;", "&", numeen)
                numero = re.sub("&#8217;", "'", numeall[1])
                numero = re.sub("&#038;", "&", numero)
            except:
                nume = re.sub("&#8217;", "'", nume)
                nume = re.sub("&#038;", "&", nume)
                numeen = nume
                numero = nume
            addDir(numeen, legatura, 5, imagine, None, numero)
    elif meniu == 'categorii':
        regex_menu = '''<li id="nav_menu(.+?)</ul></div></li>'''
        regex_submenu = '''<li.+?a href="(.+?)">(.+?)<'''
        for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
            match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
            #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(match))
            for legatura, nume in match:
                addDir(nume, legatura, 6, movies_thumb, 'filme')
        more_cat = [('Romanesti', 'http://filmehd.net/despre/filme-romanesti'),
            ('Noi', 'http://filmehd.net/despre/filme-romanesti')]
        for nume, legatura in more_cat:
            addDir(nume, legatura, 6, movies_thumb, 'filme')
    match = re.compile('class=\'wp-pagenavi', re.IGNORECASE).findall(link)
    if len(match) > 0:
        new = re.compile('/(\d+)').findall(url)
        if new:
            nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
            print "NEXT " + nexturl
            addNext('Next', nexturl, 6, next_thumb, 'filme')
        else:
            new = re.compile('page/(\d+)/').findall(url)
            if new:
                re.sub('page/\d+', 'page/' + (str(int(new[0]) + 1)), url)
            else:
                nexturl = url + '/page/2/'
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
        cm = []
        cm.append(('MetaInfo', 'XBMC.RunPlugin(%s?mode=2&name=%s&nametwo=%s)' % (sys.argv[0], urllib.quote_plus(name), urllib.quote_plus(descriere))))
        liz.addContextMenuItems(cm, replaceItems=False)
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    #liz.setInfo(type="Video", infoLabels={"overlay": 7})
    #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(cm))
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
    nametwo = urllib.unquote_plus(params["nametwo"])
except:
    nametwo = None
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
    get_meta(name)

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
