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

settings = xbmcaddon.Addon(id='plugin.video.emisiunionline')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')
base_url = "http://www.emisiuni-online.ro"

def ROOT():
    addDir('Recent Adaugate', 'http://www.emisiuni-online.ro', 6, movies_thumb, 'recente')
    addDir('Emisiuni Pro-TV', 'http://www.emisiuni-online.ro/news/emisiuni_protv/1-0-1', 6, movies_thumb, 'recente')
    addDir('Emisiuni Antena 1', 'http://www.emisiuni-online.ro/news/emisiuni_antena_1/1-0-2', 6, movies_thumb, 'recente')
    addDir('Emisiuni KanalD', 'http://www.emisiuni-online.ro/news/emisiuni_kanald/1-0-3', 6, movies_thumb, 'recente')
    addDir('Emisiuni Prima TV', 'http://www.emisiuni-online.ro/news/emisiuni_prima_tv/1-0-4', 6, movies_thumb, 'recente')
    addDir('Seriale', 'http://www.emisiuni-online.ro/news/seriale/1-0-5', 6, movies_thumb, 'recente')
    addDir('Cauta', base_url, 3, search_thumb)
    
def striphtml(data):
    p = re.compile(r'<.*?>')
    return p.sub('', data)

def cauta_video(url):
    link = get_search(url)
    match = re.compile('search-block clr".+?image: url\(\'(.+?)\'.+?href="(.+?)".+?title="(.+?)".+?eMessage">(.+?)</div', re.DOTALL | re.IGNORECASE).findall(link)
    for imagine, legatura, nume, descriere in match:
        imagine = '%s%s' % (base_url, imagine)
        addDir(striphtml(nume), legatura, 5, imagine, None, striphtml(descriere))
    match = re.compile('class="swchItem"', re.IGNORECASE).findall(link)
    if len(match) > 0:
        new = re.compile(';t=0;p=(\d+);md=').findall(url)
        if new:
            nexturl = re.sub(';p=(\d+)', ';p=' + str(int(new[0]) + 1), url)
            print "NEXT " + nexturl
            addNext('Next', nexturl, 2, next_thumb)
        else:
            nexturl = '%s;t=0;p=2;md=' % (url)
            addNext('Next', nexturl, 2, next_thumb)
 
def get_video_links(url, name):
    link = get_search(url)
    match = re.compile('uSpoiler(.+?)uSpoiler', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)[-1]
    match2 = re.compile('src="(.+?)"', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(match)
    #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(match))
    for m_link in match2:
        if m_link.startswith("//"):
            m_link = 'http:' + m_link #//ok.ru fix
        parsed_url1 = urlparse.urlparse(m_link)
        if parsed_url1.scheme:
            if urlresolver.HostedMediaFile(m_link).valid_url():
                host = m_link.split('/')[2].replace('www.', '').capitalize()
                addLink(host, m_link, movies_thumb, name, 10)

            

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
    
    cauta_video(get_search_url(search_string + "" + autoSearch))
    
def play_video(url, mname):
    stream_url = urlresolver.resolve(url)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=movies_thumb); liz.setInfo(type="Video", infoLabels={"Title": name})
    liz.setInfo(type="Video", infoLabels={"Title": mname})
    xbmc.Player ().play(stream_url, liz, False)
    
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
    url = '%s/search/?q=%s' % (base_url, urllib.quote_plus(keyword))
    
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
        url = 'http://www.emisiuni-online.ro'
    link = get_url(url)
    if meniu == 'recente':
        match = re.compile('col-\d+".+?background-image: url\(\'(.+?)\'.+?eTitle"><a href="(.+?)".+?>(.+?)<.+?ssage">(.+?)<', re.DOTALL).findall(link)
        for imagine, legatura, nume, descriere in match:
            imagine = base_url + imagine
            legatura = base_url + legatura
            nume = re.sub('Emisiunea ','', nume)
            addDir(nume, legatura, 5, imagine, descriere)
        match = re.compile('class="swchItem"', re.IGNORECASE).findall(link)
        if len(match) > 0:
            new = re.compile('//?page(\d+)').findall(url)
            new2 = re.compile('/(\d+)-\d+-\d+$').findall(url)
            if new:
                nexturl = re.sub('/?page(\d+)', '/?page' + str(int(new[0]) + 1), url)
                print "NEXT " + nexturl
                addNext('Next', nexturl, 6, next_thumb, 'recente')
            elif new2:
                nexturl = re.sub('/(\d+)-', '/' + str(int(new2[0]) + 1) + '-', url)
                addNext('Next', nexturl, 6, next_thumb, 'recente')
            else:
                nexturl = url + '/?page2'
                addNext('Next', nexturl, 6, next_thumb, 'recente')

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
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name) + "&mname=" + urllib.quote_plus(movie_name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    if descriere != None:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descriere})
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

try: url = urllib.unquote_plus(params["url"])
except: url = None
try: name = urllib.unquote_plus(params["name"])
except: name = None
try: mname = urllib.unquote_plus(params["mname"])
except: mname = None
try: mode = int(params["mode"])
except: mode = None
try: meniu = urllib.unquote_plus(params["meniu"])
except: meniu = None

if mode == None or url == None or len(url) < 1:
    ROOT()
        
elif mode == 2:
    cauta_video(url)
        
elif mode == 3:
    CAUTA(url)
        
elif mode == 5:
    get_video_links(url, name)
        
elif mode == 6:
    parse_menu(url, meniu)

elif mode == 10:
    play_video(url, mname)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
