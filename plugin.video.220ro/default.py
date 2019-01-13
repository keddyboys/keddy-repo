import HTMLParser
import os
import re
import sys
import time
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


__addon__ = xbmcaddon.Addon()
__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")

sys.path.append (__resource__)

settings = xbmcaddon.Addon(id='plugin.video.220ro')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')


def ROOT():
    addDir('Video', 'http://www.220.ro/', 23, movies_thumb, 'video')
    addDir('Shows', 'http://www.220.ro/', 23, movies_thumb, 'shows')
    addDir('Best-Of', 'http://www.220.ro/', 23, movies_thumb, 'best-of')
    addDir('Cauta', 'http://www.220.ro/', 3, search_thumb)


def CAUTA_LIST(url):
    link = get_search(url)
    match = re.compile('<div class=".+?>\n<div.+?\n<a.+?"(.+?)" title="(.+?)" class.+?\n<img src="(.+?)".+?\n.+?\n<span.+?>\n(.+?)\n', re.IGNORECASE | re.MULTILINE).findall(link)
    if len(match) > 0:
        print match
        for legatura, name, img, length in match:
            # name = HTMLParser.HTMLParser().unescape(  codecs.decode(name, "unicode_escape") ) + " " + length
            name = name + " " + length
            the_link = legatura
            image = img
            sxaddLink(name, the_link, image, name, 10)


def CAUTA_VIDEO_LIST(url, meniu):
    link = get_search(url)
    # f = open( '/storage/.kodi/temp/files.py', 'w' )
    # f.write( 'url = ' + repr(url) + '\n' )
    # f.close()
    if meniu == 'video':
        match = re.compile('<div class=".+?>\n<a title="(.+?)" href="(.+?)" class=.+?><img.+?data-src="(.+?)".+?\n<span.+?\n(.+?)\n', re.IGNORECASE | re.MULTILINE).findall(link)
        if len(match) > 0:
            for name, legatura, img, length in match:
                # name = HTMLParser.HTMLParser().unescape(  codecs.decode(name, "unicode_escape") ) + " " + length
                the_link = legatura
                image = img
                sxaddLink(name, the_link, image, name, 10, name, length)
    elif meniu == 'shows':
        match = re.compile('<div class="tabel_show">\n<a href="(.+?)" title="(.+?)".+? data-src="(.+?)".+?\n.+?\n.+?\n.+?\n<p>(.+?)</p>', re.IGNORECASE | re.MULTILINE).findall(link)
        if len(match) > 0:
            for legatura, name, image, descript in match:
                addDir(name, legatura, 5, image, 'sub_shows', descript)
    elif meniu == 'sub_shows':
        match = re.compile('<div class="left thumbnail">\n<a href="(.+?)" title="(.+?)".+?data-src="(.+?)".+?<span.+?>(.+?)</span>.+?<p>(.+?)</p>', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        if len(match) > 0:
            for legatura, name, image, length, descript in match:
                sxaddLink(name, legatura, image, name, 10, descript, length)
    elif meniu == 'best-month':
        match = re.compile('<div class=".+?>\n<div.+?\n<a.+?"(.+?)" title="(.+?)" class.+?\n<img src="(.+?)".+?\n.+?\n<span.+?>\n(.+?)\n.+?\n.+?\n.+?\n.+?\n<p>(.+?)</p>', re.IGNORECASE | re.MULTILINE).findall(link)
        if len(match) > 0:
            for legatura, name, image, length, descript in match:
                sxaddLink(name, legatura, image, name, 10, descript, length)

    match = re.compile('<li><a href=".+?" title="Pagina (\d+)">', re.IGNORECASE).findall(link)
    if len(match) > 0:
        if meniu == 'best-month':
            page_num = re.compile('.+?220.+?\d+/\d+/(\d+)', re.IGNORECASE).findall(url)
            nexturl = re.sub('.+?220.+?\d+/\d+/(\d+)', match[0], url)
        else:
            page_num = re.compile('.+?220.+?(\d+)', re.IGNORECASE).findall(url)
            nexturl = re.sub('.+?220.+?(\d+)', match[0], url)
        if nexturl.find("/\d+") == -1:
            nexturl = url[:-1]
        if page_num:
            pagen = page_num[0]
            pagen = int(pagen)
            pagen += 1
            nexturl += str(pagen)
        else:
            nexturl = url + match[0]
        addNext('Next', nexturl, 5, next_thumb, meniu)


def CAUTA(url, autoSearch=None):
    keyboard = xbmc.Keyboard('')
    keyboard.doModal()
    if (keyboard.isConfirmed() is False):
        return
    search_string = keyboard.getText()
    if len(search_string) == 0:
        return
    if autoSearch is None:
        autoSearch = ""
    CAUTA_LIST(get_search_url(search_string + "" + autoSearch))


def CAUTA_VIDEO(url, gen, autoSearch=None):
    CAUTA_VIDEO_LIST(get_search_video_url(gen), meniu=None)


def SXVIDEO_GENERIC_PLAY(sxurl):
    progress = xbmcgui.DialogProgress()
    progress.create('220.ro', 'Se incarca videoclipul \n')
    url = sxurl
    src = get_url(urllib.quote(url, safe="%/:=&?~#+!$,;'@()*[]"))
    title = ''
    # title
    match = re.compile('<title>(.+?)<.+?>.?\s*.+?videosrc:\'(.+?)\'.+?og:description.+?"(.+?)".+?<p class="date">(.+?)</p>', re.IGNORECASE | re.DOTALL).findall(src)
    title = HTMLParser.HTMLParser().unescape(match[0][0])
    title = re.sub('VIDEO.?- ', '', title) + " " + match[0][3]
    location = match[0][1]
    progress.update(0, "", title, "")
    if progress.iscanceled():
        return False
    listitem = xbmcgui.ListItem(path=location)
    listitem.setInfo('video', {'Title': title, 'Plot': match[0][2]})
    # xbmcplugin.setResolvedUrl(1, True, listitem)
    progress.close()
    xbmc.Player().play(item=(location + '|Host=s2.220.t1.ro'), listitem=listitem)


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
    url = 'http://www.220.ro/cauta/' + urllib.quote_plus(keyword) + '/video'
    return url


def get_search_video_url(gen, offset=None):
    url = 'http://www.220.ro/' + gen + '/'
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
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = {}
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]
    return param


def sxaddLink(name, url, iconimage, movie_name, mode=4, descript=None, length=None):
    ok = True
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    if descript is not None:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": movie_name, "Plot": name})
    if length is not None:
        liz.setInfo(type="Video", infoLabels={"duration": int(get_sec(length))})
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=False)
    return ok


def get_sec(time_str):
    m, s = time_str.split(':')
    return int(m) * 60 + int(s)


def addLink(name, url, iconimage, movie_name):
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok


def addNext(name, page, mode, iconimage, meniu=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu is not None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    xbmcplugin.setContent(int(sys.argv[1]), 'movies')
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def addDir(name, url, mode, iconimage, meniu=None, descript=None):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    if meniu is not None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descript is not None:
        u += "&descriere=" + urllib.quote_plus(descript)
    ok = True
    liz = xbmcgui.ListItem(name, iconImage=iconimage, thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Genre": name})
    if descript is not None:
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok


def parse_menu(url, meniu):
    if url is None:
        url = 'http://www.220.ro/'
    if meniu == 'video':
        url = url + meniu + '/'
        link = get_search(url)
        match = re.compile('</a>\n<a title="(.+?)" href="(.+?)">', re.IGNORECASE | re.MULTILINE).findall(link)
        match.append(['Sexy', 'http://www.220.ro/sexy/'])
    elif meniu == 'shows':
        match = [('Cele mai tari', 'http://www.220.ro/shows/'), ('Ultimele actualizate', 'http://www.220.ro/shows/ultimele-actualizate/'), ('Alfabetic', 'http://www.220.ro/shows/alfabetic/')]
    elif meniu == 'best-of':
        now = time.localtime()
        # x = (now.tm_year - 2005) * 12 + (now.tm_mon - 5)
        x = (now.tm_year - 2005) + 1
        # match = [time.localtime(time.mktime((now.tm_year, now.tm_mon - n, 1, 0, 0, 0, 0, 0, 0)))[:1] for n in range(x)]
        match = [time.localtime(time.mktime((now.tm_year - n, 12, 0, 0, 0, 0, 0, 0, 0)))[:2] for n in range(x)]
        # match=[(), (), (), (), (), (), (), (), (), (), (), ()]
    elif meniu == 'best-year':
        match = [('Ianuarie', '01'), ('Februarie', '02'), ('Martie', '03'), ('Aprilie', '04'), ('Mai', '05'), ('Iunie', '06'), ('Iulie', '07'), ('August', '08'), ('Septembrie', '09'), ('Octombrie', '10'), ('Noiembrie', '11'), ('Decembrie', '12')]

    if len(match) > 0:
        print match
        if meniu == 'best-of':
            for titlu, an in match:
                image = "DefaultVideo.png"
                year_link = 'http://www.220.ro/best-of/' + str(titlu) + '/'
                addDir(str(titlu), year_link, 23, image, 'best-year')
        elif meniu == 'best-year':
            for titlu, luna in match:
                image = "DefaultVideo.png"
                month_link = url + str(luna) + '/'
                addDir(str(titlu), month_link, 5, image, 'best-month')
        else:
            for titlu, url in match:
                image = "DefaultVideo.png"
                addDir(titlu, url, 5, image, meniu, titlu)
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


# print "Mode: "+str(mode)
# print "URL: "+str(url)
# print "Name: "+str(name)

if mode is None or url is None or len(url) < 1:
    ROOT()

elif mode == 1:
    CAUTA_VIDEO(url, 'faze-tari')

elif mode == 2:
    CAUTA_LIST(url)

elif mode == 3:
    CAUTA(url)

elif mode == 5:
    CAUTA_VIDEO_LIST(url, meniu)

elif mode == 23:
    parse_menu(url, meniu)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
