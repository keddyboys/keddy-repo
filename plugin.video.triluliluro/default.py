import HTMLParser
import os
import re
import sys
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin

settings = xbmcaddon.Addon(id='plugin.video.triluliluro')

search_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'search.png')
movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')


def ROOT():
    addDir('Muzica', 'http://www.trilulilu.ro/', 6, movies_thumb, 'Muzica')
    addDir('Film', 'http://www.trilulilu.ro/', 6, movies_thumb, 'Film')
    addDir('Haioase', 'http://www.trilulilu.ro/', 6, movies_thumb, 'Haioase')
    addDir('Copii', 'http://www.trilulilu.ro/', 6, movies_thumb, 'Kids')
    addDir('Lifestyle', 'http://www.trilulilu.ro/', 6, movies_thumb, 'Lifestyle')
    addDir('Altele', 'http://www.trilulilu.ro/', 6, movies_thumb, 'Altele')
    addDir('Cauta', 'http://www.trilulilu.ro/', 3, search_thumb)
    addDir('Cauta ... dublat', 'http://www.trilulilu.ro/', 31, search_thumb)
    

def CAUTA_LIST(url):
    link = get_search(url)
                   
    match = re.compile('<a href="(http://www.trilulilu.ro/video-.+?)#ref=cauta" .+?title="(.+?)" .+?>\n.+?<div.+?>(\d+:\d+)</div><img (src|data-src)="(.+?)" width="', re.IGNORECASE | re.MULTILINE).findall(link)
    if len(match) > 0:
        print match
        for legatura, name, length, s, img in match:
            #name = HTMLParser.HTMLParser().unescape(  codecs.decode(name, "unicode_escape") ) + " " + length
            name = name + " " + length
            the_link = legatura
            image = img
            sxaddLink(name, the_link, image, name, 10)

    match = re.compile('<link rel="next" href="\?offset=(\d+)" />', re.IGNORECASE).findall(link)
    if len(match) > 0:
        nexturl = re.sub('\?offset=(\d+)', '?offset=' + match[0], url)
        if nexturl.find("offset=") == -1:
            nexturl += '?offset=' + match[0]
      
        print "NEXT " + nexturl
      
        addNext('Next', nexturl, 2, next_thumb)
            
 
def CAUTA_VIDEO_LIST(url):
    link = get_search(url)
    match = re.compile('<a href="(http://www.trilulilu.ro/.+?)#ref=browse" .+?title="(.+?)" .+?>\n.+?<div.+?>(\d+:\d+)</div><img (src|data-src)="(.+?)" width="', re.IGNORECASE | re.MULTILINE).findall(link)
    #f = open( '/storage/.kodi/temp/files.py', 'w' )
    #f.write( 'match = ' + repr(match) + '\n' )
    #f.close()
    if len(match) > 0:
        print match
        for legatura, name, length, s, img in match:
            #name = HTMLParser.HTMLParser().unescape(  codecs.decode(name, "unicode_escape") ) + " " + length
            name = name + " " + length
            the_link = legatura
            image = img
            sxaddLink(name, the_link, image, name, 10)

    match = re.compile('<link rel="next" href=".+?offset=(\d+)" />', re.IGNORECASE).findall(link)
    if len(match) > 0:
        nexturl = re.sub('offset=(\d+)', 'offset=' + match[0], url)
        if nexturl.find("offset=") == -1:
            nexturl += '&offset=' + match[0]
        print "NEXT " + nexturl
        addNext('Next', nexturl, 5, next_thumb)
            

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

def CAUTA_VIDEO(url, gen, autoSearch=None):
    
    CAUTA_VIDEO_LIST(get_search_video_url(gen))
    
def SXVIDEO_GENERIC_PLAY(sxurl):
    #url = "http://www.youtube.com/watch?v=_yVv9dx88x0"   #a youtube ID will work as well and of course you could pass the url of another site
    url = sxurl
    src = get_url(url)
    title     = ''
    #title
    match = re.compile('<title>(.+?)<.+?file: "(.+?)".+?fileHD: (.+?)".+?fileUrlHD: "(.+?)"', re.IGNORECASE | re.DOTALL).findall(src)
    title = HTMLParser.HTMLParser().unescape(match[0][0])
    title = re.sub('\s+-\s*Video\s*-\s*Trilulilu', '', title);

    if match[0][1]:
        if match[0][2] == "\"1":
            listitem = xbmcgui.ListItem(path=match[0][3])
            listitem.setInfo('video', {'Title': title})
            #xbmcplugin.setResolvedUrl(1, True, listitem)
            xbmc.Player().play(item=match[0][3], listitem=listitem)     
        else:
            listitem = xbmcgui.ListItem(path=match[0][1])
            listitem.setInfo('video', {'Title': title})
            #xbmcplugin.setResolvedUrl(1, True, listitem)
            xbmc.Player().play(item=match[0][1], listitem=listitem)
    else:
        return False

    
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
    url = 'http://cauta.trilulilu.ro/video/' + urllib.quote_plus(keyword)
    
    if offset != None:
        url += "?offset=" + offset
    
    return url
  
def get_search_video_url(gen, offset=None):
    url = 'http://www.trilulilu.ro/' + gen + '?mimetype=video&header=1'
    if offset != None:
        url += "&amp;offset=" + offset
    
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
        url = 'http://www.trilulilu.ro/'
    link = get_url(url)
    regex_menu = '''<div class="tab-pane" id="subhashtag_''' + meniu + '''(.+?)</ul>'''
    regex_submenu = '''#subhashtag_content.+?<a href="(.+?)" >(.+?)<'''
    #http://www.trilulilu.ro/Monden?mimetype=video&header=1#ref=mimetype_filter_video
    #result: http://www.trilulilu.ro/Monden?header=1#ref=header
    for meniu in re.compile(regex_menu, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link):
        match = re.compile(regex_submenu, re.DOTALL).findall(meniu)
    for legatura, nume in match:
        link_fix = (legatura.split('?', 1)[0]) + '?mimetype=video&header=1'
        addDir(nume, link_fix, 5, movies_thumb)

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

def addLink(name, url, iconimage, movie_name):
    ok = True
    liz = xbmcgui.ListItem(name, iconImage="DefaultVideo.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": movie_name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=liz)
    return ok

def addNext(name, page, mode, iconimage):
    u = sys.argv[0] + "?url=" + urllib.quote_plus(page) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    liz.setInfo(type="Video", infoLabels={"Title": name})
    ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def addDir(name, url, mode, iconimage, meniu=None):
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
        
elif mode == 1:
    CAUTA_VIDEO(url, 'Haioase')
        
elif mode == 2:
    CAUTA_LIST(url)
        
elif mode == 3:
    CAUTA(url)
        
elif mode == 5:
    CAUTA_VIDEO_LIST(url)
        
elif mode == 6:
    parse_menu(url, meniu)
    
elif mode == 7:
    CAUTA_VIDEO(url, meniu)

elif mode == 31:
    CAUTA(url, " dublat")

elif mode == 4:
    VIDEO(url, name)

elif mode == 9:
    SXVIDEO_EPISOD_PLAY(url)

elif mode == 10:
    SXVIDEO_GENERIC_PLAY(url)



xbmcplugin.endOfDirectory(int(sys.argv[1]))
