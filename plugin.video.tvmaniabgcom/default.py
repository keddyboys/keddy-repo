# -*- coding: utf-8 -*-

import HTMLParser
import cookielib
import json
import os
import re
import sys
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin


website = 'http://tvmaniabg.com'

settings = xbmcaddon.Addon(id='plugin.video.tvmaniabgcom')

movies_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'movies.png')
next_thumb = os.path.join(settings.getAddonInfo('path'), 'resources', 'media', 'next.png')


def ROOT():
    addDir('Live TV Music', 'http://tvmaniabg.com/category/%d0%bc%d1%83%d0%b7%d0%b8%d0%ba%d0%b0%d0%bb%d0%bd%d0%b8/', 23, movies_thumb, 'lives')
    addDir('Live TV Nationals', 'http://tvmaniabg.com/category/%d0%bd%d0%b0%d1%86%d0%b8%d0%be%d0%bd%d0%b0%d0%bb%d0%bd%d0%b8/', 23, movies_thumb, 'lives')
    addDir('Live TV Sport', 'http://tvmaniabg.com/category/sport/', 23, movies_thumb, 'lives')
    addDir('Live TV Film', 'http://tvmaniabg.com/category/%d1%84%d0%b8%d0%bb%d0%bc%d0%b8/', 23, movies_thumb, 'lives')
    addDir('Live TV Documentary', 'http://tvmaniabg.com/category/%d1%87%d1%83%d0%b6%d0%b4%d0%b5%d1%81%d1%82%d1%80%d0%b0%d0%bd%d0%bd%d0%b8/', 23, movies_thumb, 'lives')
    addDir('Live TV 18+', 'http://tvmaniabg.com/category/18/', 23, movies_thumb, 'lives')


def get_url(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0')
    try:
        response = urllib2.urlopen(req)
        link = response.read()
        response.close()
        return link
    except:
        return False


def get_search(url):
    f = HTMLParser.HTMLParser()
    url = f.unescape(url)
    cj = cookielib.CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    opener.addheaders = [('User-Agent', 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:48.0) Gecko/20100101 Firefox/48.0'),
        ('Content-type', 'application/x-www-form-urlencoded'),
        ('Referer', url),
        ('Host', 'tvmaniabg.com')
        ]
    try:
        response = opener.open(url)
        link = response.read()
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
    iconimage = urllib.unquote(urllib.unquote(iconimage))
    u = sys.argv[0] + "?url=" + urllib.quote_plus(url) + "&mode=" + str(mode) + "&name=" + urllib.quote_plus(name)
    liz = xbmcgui.ListItem(name, iconImage="DefaultFolder.png", thumbnailImage=iconimage)
    if meniu is not None:
        u += "&meniu=" + urllib.quote_plus(meniu)
    if descript is not None:
        u += "&descriere=" + urllib.quote_plus(descript)
        ok = True
        liz.setInfo(type="Video", infoLabels={"Title": name, "Plot": descript})
    else:
        liz.setInfo(type="Video", infoLabels={"Title": name})
    if meniu == 'play':
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz)
    else:
        ok = xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=u, listitem=liz, isFolder=True)
    return ok

def play_video(path, title):
    item = xbmcgui.ListItem(path=path)
    item.setInfo('video', {'Title': title, 'Plot': title})
    xbmc.Player().play(path, item)

def parse_menu(url, meniu, searchterm=None):
    if url is None:
        url = 'http://tvmaniabg.com'
    if meniu == 'lives':
        match = []
        link = get_search(url)
        #with open(xbmc.translatePath(os.path.join('special://temp', 'files.py')), 'wb') as f: f.write(repr(link))
        match = re.compile('class="post-thumbnail">.+?src="(.+?)".+?<a href="(.+?)">(.+?)<', re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(link)
        for imagine, legatura, nume in match:
            descriere = nume
            addDir(nume, legatura, 23, imagine, 'play', descriere)
        match = re.compile('class="pagination', re.IGNORECASE).findall(link)
        if len(match) > 0:
            new = re.compile('/(\d+)').findall(url)
            if new:
                nexturl = re.sub('/(\d+)', '/' + str(int(new[0]) + 1), url)
                print "NEXT " + nexturl
                addNext('Next', nexturl, 23, next_thumb, 'lives')
            else:
                new = re.compile('page/(\d+)/').findall(url)
                if new:
                    re.sub('page/\d+', 'page/' + (str(int(new[0]) + 1)), url)
                else:
                    nexturl = url + 'page/2/'
                addNext('Next', nexturl, 23, next_thumb, 'lives')
    elif meniu == 'play':
        link = get_search(url)
        regex = """"name">(.+?)<.+?(?:'file': '(.+?)'|<iframe.+?src="(.+?)")"""
        match = re.compile(regex, re.IGNORECASE | re.DOTALL).findall(link)
        if len(match) > 0:
            if match[0][1]:
                play_video(match[0][1], match[0][0])
            elif match[0][2]:
                if re.compile('neterra', re.IGNORECASE).findall(match[0][2]):
                    neterra = get_search(match[0][2])
                    data = re.compile('source:.+?"(.+?)"', re.IGNORECASE | re.DOTALL).findall(neterra)
                    play_video(data[0], match[0][0])
                else:
                    link = get_search(match[0][2])
                    matchs = re.compile('file:"(.+?)"', re.IGNORECASE | re.DOTALL).findall(link)
                    if len(matchs) > 0:
                        play_video(matchs[0], match[0][0])
                    else:
                        matchs = re.compile('og:video" content="(.+?)"', re.IGNORECASE | re.DOTALL).findall(link)
                        if len(matchs) > 0:
                            if re.compile('dacast', re.IGNORECASE).findall(matchs[0]):
                                path = matchs[0]
                                data = re.compile('c=(\d+)_(\d+)', re.IGNORECASE).findall(path)
                                req_url = 'https://json.dacast.com/b/%s/c/%s' % (data[0][0], data[0][1])
                                get_response = json.loads(get_search(req_url))
                                play_video(get_response.get('hls'), match[0][0])
                        else:
                            matchs = re.compile("file': '(.+?)'", re.IGNORECASE | re.DOTALL).findall(link)
                            if len(matchs) > 0:
                                play_video(matchs[0], match[0][0])
                            else:
                                matchs = re.compile('src="(.+?)"', re.IGNORECASE | re.DOTALL).findall(link)
                                if len(matchs) > 0:
                                    play_video(matchs[0], match[0][0])
                                
                            
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

if mode is None or url is None or len(url) < 1:
    ROOT()
elif mode == 23:
    parse_menu(url, meniu)

xbmcplugin.endOfDirectory(int(sys.argv[1]))
