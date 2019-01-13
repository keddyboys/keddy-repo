# -*- coding: utf-8 -*- 
# Based on contents from https://github.com/Diecke/service.subtitles.addicted
# Thanks Diecke!

import os
import re
import shutil
import socket
import string
import sys
import unicodedata
import urllib
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs

__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')
__version__    = __addon__.getAddonInfo('version')
__language__   = __addon__.getLocalizedString

__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', '')).decode("utf-8")

sys.path.append (__resource__)

import requests

from Addic7edUtilities import log, get_language_info

self_host = "http://www.addic7ed.com"

req_headers = {
    'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.13 (KHTML, like Gecko) Chrome/0.A.B.C Safari/525.13',
    'Referer': 'http://www.addic7ed.com'}
    
def get_url(url, headers=None):
    socket.setdefaulttimeout(20)
    if headers:
        try:
            h = requests.get(url, req_headers)
            url = h.url
        except:
            pass
    req_headers['Pragma'] = 'no-cache'
    request = requests.get(url, headers=req_headers)
    contents = request.content
    return contents

def append_subtitle(item):
    listitem = xbmcgui.ListItem(label=item['lang']['name'],
                                label2=item['filename'],
                                iconImage=item['rating'],
                                thumbnailImage=item['lang']['2let'])

    listitem.setProperty("sync", 'true' if item["sync"] else 'false')
    listitem.setProperty("hearing_imp", 'true' if item["hearing_imp"] else 'false')

    url = "plugin://%s/?action=download&link=%s&filename=%s" % (__scriptid__,
                                                                item['link'],
                                                                item['filename'])
    xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

def query_TvShow(name, season, episode, langs, file_original_path):
    log(__name__, "query show: 'name=%s, season=%s, episode=%s, langs=%s, file_original_path=%s'" % (name, season, episode, langs, file_original_path))
    name = addic7ize(name).lower().replace(" ", "_")
    searchurl = "%s/serie/%s/%s/%s/addic7ed" % (self_host, name, season, episode)
    filename_string = "%s.S%.2dE%.2d" % (name.replace("_", ".").title(), int(season), int(episode))
    query(searchurl, langs, file_original_path, filename_string)

def query_Film(name, year, langs, file_original_path):
    log(__name__, "query film: 'name=%s, year=%s, langs=%s, file_original_path=%s'" % (name, year, langs, file_original_path))
    name = urllib.quote(name.replace(" ", "_"))
    searchurl = "%s/film/%s_(%s)-Download" % (self_host, name, str(year))
    filename_string = "%s" % (name.replace("_", ".").title())
    query(searchurl, langs, file_original_path, filename_string)

def query(searchurl, langs, file_original_path, filename_string):
    log(__name__, "query: 'searchurl=%s, langs=%s, file_original_path=%s, filename_string=%s'" % (searchurl, langs, file_original_path, filename_string))
    sublinks = get_subs(searchurl, langs, filename_string)
    sublinks.sort(key=lambda x: [not x['sync']])
    #log(__name__, "sub='%s'" % (sublinks))

    for s in sublinks:
        append_subtitle(s)

def get_subs(url, langs, filename_string, cont=None):
    if cont:
        content = cont
    else:
        content = get_url(url)
    sublinks = []
    regex = '''>Version(.+?),.+?uploaded(.+?)table footer'''
    regex2 = '''(?:|\'>(.+?)</a>(.+?)</td>.+?)(?:|Translated(.+?))language">(.+?)<.+?(?:|<b>(\d{1,2}).+?)Download" href="(.+?)".+?(?:.+?(impaired)|)'''
    for match in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(content):
        ver = match[0]
        infos = re.compile(regex2, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(match[1])
        for uploadr, edit, translator, language, percent, rawurl, impaired in infos:
            lang = get_language_info(language)
            if lang['3let'] in langs:
                if uploadr: uploader = uploadr
                if edit: edited = re.sub('\s+', '', edit)
                link = "%s%s" % (self_host, rawurl)
                hi = '1' if impaired else ''
                rating = str(int(round(float(percent)/20))) if percent else '5'
                sublinks.append({'rating': rating, 'filename': "%s-%s-%s-%s" % (filename_string, ver, uploader, edited), 'sync': '', 'link': link, 'lang': lang, 'hearing_imp': hi})
                #log(__name__, "rating: \"%s\"" % (rating))
    return sublinks

def test():
    with open('/root/.kodi/temp/files444.py', 'r') as content_file:
        content = content_file.read()
    return content

def search_manual(searchstr, languages, year=None):
    search_string = urllib.unquote(searchstr)
    if year:
        search_string  = search_string + ' ' + str(year)
    log(__name__, "manual_search='%s', addon_version=%s" % (search_string, __version__))
    url = self_host + "/search.php?search=" + search_string + '&Submit=Search'
    content = get_url(url, 'headers')
    #with open('/root/.kodi/temp/files.py', 'wb') as f: f.write(repr(content))
    #content = test()
    regexp = '''</td><td><a href="(.+?)".+?>(.+?)<'''
    match = re.compile(regexp, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(content)
    if match:
        if len(match) > 1:
            dialog = xbmcgui.Dialog()
            sel = dialog.select("Select item",
                                [name for link, name in match])
            if sel >= 0:
                show_url = self_host + "/" + match[int(sel)][0]
                for s in get_subs(show_url, languages, ''):
                    append_subtitle(s)
            else:
                return
        else:
            show_url = self_host + "/" + match[0][0]
            for s in get_subs(show_url, languages, ''):
                append_subtitle(s)
    else:
        for s in get_subs('', languages, '', content):
            append_subtitle(s)
      

    if content is not None:
        return False
        # getallsubs(content, languages, filename)

def search_filename(filename, languages):
    title, year = xbmc.getCleanMovieTitle(filename)
    log(__name__, "clean title: \"%s\" (%s)" % (title, year))
    try:
        yearval = int(year)
    except ValueError:
        yearval = 0
    if title and yearval > 1900:
        query_Film(title, year, item['3let_language'], filename)
    else:
        match = re.search(r'\WS(?P<season>\d\d)E(?P<episode>\d\d)', title, flags=re.IGNORECASE)
        if match is not None:
            tvshow = string.strip(title[:match.start('season')-1])
            season = string.lstrip(match.group('season'), '0')
            episode = string.lstrip(match.group('episode'), '0')
            query_TvShow(tvshow, season, episode, item['3let_language'], filename)
        else:
            search_manual(filename, item['3let_language'])


def Search(item):
    filename = os.path.splitext(os.path.basename(item['file_original_path']))[0]
    #log(__name__, "Search_filename='%s', addon_version=%s" % (filename, __version__))

    if item['mansearch']:
        search_manual(item['mansearchstr'], item['3let_language'])

    if len(item['tvshow']) > 0:
        query_TvShow(item['tvshow'], item['season'], item['episode'], item['3let_language'], filename)
    else:
        if str(item['year']) == "":
            titlu = item['title']
            item['title'], item['year'] = xbmc.getCleanMovieTitle(titlu)
            #log(__name__, "first item from filename='%s'" % (titlu))
            episodes = re.compile('S(\d{1,2})E(\d{1,2})', re.IGNORECASE).findall(item['title'])
            if episodes:
                item['season'] = episodes[0][0]
                item['episode'] = episodes[0][1]
            else:
                episodes = re.compile('(\d)(\d{1,2})', re.IGNORECASE).findall(item['title'])
                if episodes:
                    item['season'] = episodes[0][0]
                    item['episode'] = episodes[0][1]
            item['title'] = addic7ize((re.sub('(\d)(\d{1,2})', '', (re.sub('S(\d{1,2})E(\d{1,2})', '', item['title'])))).strip())
            try: item['title'] = item['title'].split('  ', 1)[0]
            except: pass
            log(__name__, "item from filename='%s'" % (item))
            if len(item['season']) > 0 and len(item['episode']) > 0:
                query_TvShow(item['title'], item['season'], item['episode'], item['3let_language'], filename)
            else:
                if item['year']:
                    query_Film(item['title'], item['year'], item['3let_language'], filename)
                else:
                    search_manual(item['title'], item['3let_language'], item['year'])
        else:
            query_Film(item['title'], item['year'], item['3let_language'], filename)

def takeTitleFromFocusedItem():
    labelMovieTitle = xbmc.getInfoLabel("ListItem.OriginalTitle")
    labelYear = xbmc.getInfoLabel("ListItem.Year")
    labelTVShowTitle = xbmc.getInfoLabel("ListItem.TVShowTitle")
    labelSeason = xbmc.getInfoLabel("ListItem.Season")
    labelEpisode = xbmc.getInfoLabel("ListItem.Episode")
    labelType = xbmc.getInfoLabel("ListItem.DBTYPE")  #movie/tvshow/season/episode	
    isItMovie = labelType == 'movie' or xbmc.getCondVisibility("Container.Content(movies)")
    isItEpisode = labelType == 'episode' or xbmc.getCondVisibility("Container.Content(episodes)")

    title = 'SearchFor...'
    if isItMovie and labelMovieTitle and labelYear:
        title = labelMovieTitle + " " + labelYear
    elif isItEpisode and labelTVShowTitle and labelSeason and labelEpisode:
        title = ("%s S%.2dE%.2d" % (labelTVShowTitle, int(labelSeason), int(labelEpisode)))

    return title
  
def download(link):
    subtitle_list = []

    if xbmcvfs.exists(__temp__):
        shutil.rmtree(__temp__)
    xbmcvfs.mkdirs(__temp__)

    files = os.path.join(__temp__, "addic7ed.srt")

    #f = get_url(link)
    s = requests.Session()
    r = s.get(link, headers=req_headers)
    t = r.content
    with open(files, 'wb') as f: f.write(t)

    subtitle_list.append(files)

    if len(subtitle_list) == 0:
        if search_string:
            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32002))).encode('utf-8'))
        else:
            xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, __language__(32003))).encode('utf-8'))

    return subtitle_list


def normalizeString(str):
    return unicodedata.normalize(
                                 'NFKD', unicode(unicode(str, 'utf-8'))
                                 ).encode('ascii', 'ignore')

# Sometimes search fail because Addic7ed uses URLs that does not match the TheTVDB format.
# This will probably grow to be a hardcoded colleciton over time. 
def addic7ize(str):
  
    addic7ize_dict = eval(open(__cwd__ + '/addic7ed_dict.txt').read())
  
    return addic7ize_dict.get(str, str)
  

def get_params():
    param = {}
    paramstring = sys.argv[2]
    if len(paramstring) >= 2:
        params = paramstring
        cleanedparams = params.replace('?', '')
        if (params[len(params) - 1] == '/'):
            params = params[0:len(params) - 2]
        pairsofparams = cleanedparams.split('&')
        param = {}
        for i in range(len(pairsofparams)):
            splitparams = pairsofparams[i].split('=')
            if (len(splitparams)) == 2:
                param[splitparams[0]] = splitparams[1]

    return param

params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
    item = {}
    if xbmc.Player().isPlaying():
        item['temp']               = False
        item['rar']                = False
        item['mansearch']          = False
        item['year']               = xbmc.getInfoLabel("VideoPlayer.Year")                         # Year
        item['season']             = str(xbmc.getInfoLabel("VideoPlayer.Season"))                  # Season
        item['episode']            = str(xbmc.getInfoLabel("VideoPlayer.Episode"))                 # Episode
        item['tvshow']             = normalizeString(xbmc.getInfoLabel("VideoPlayer.TVshowtitle"))  # Show
        item['title']              = normalizeString(xbmc.getInfoLabel("VideoPlayer.OriginalTitle"))# try to get original title
        item['file_original_path'] = xbmc.Player().getPlayingFile().decode('utf-8')                 # Full path of a playing file
        item['3let_language']      = [] #['scc','eng']

    else:
        item['temp'] = False
        item['rar'] = False
        item['mansearch'] = False
        item['year'] = ""
        item['season'] = ""
        item['episode'] = ""
        item['tvshow'] = ""
        item['title'] = takeTitleFromFocusedItem()
        item['file_original_path'] = ""
        item['3let_language'] = []

    if 'searchstring' in params:
        item['mansearch'] = True
        item['mansearchstr'] = params['searchstring']

    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        item['3let_language'].append(xbmc.convertLanguage(lang, xbmc.ISO_639_2))

    if item['title'] == "":
        item['title'] = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

    if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
        item['season'] = "0"                                                          #
        item['episode'] = item['episode'][-1:]

    if item['file_original_path'].find("http") > -1:
        item['temp'] = True

    elif item['file_original_path'].find("rar://") > -1:
        item['rar'] = True
        item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

    elif item['file_original_path'].find("stack://") > -1:
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]
    Search(item)

elif params['action'] == 'download':
    subs = download(params["link"])
    for sub in subs:
        listitem = xbmcgui.ListItem(label=sub)
        xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)

xbmcplugin.endOfDirectory(int(sys.argv[1]))  # send end of directory to XBMC
