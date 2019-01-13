# -*- coding: utf-8 -*-

import os
import re
import shutil
import sys
import unicodedata
import urllib
import urllib2
import xbmc
import xbmcaddon
import xbmcgui
import xbmcplugin
import xbmcvfs
import json
from operator import itemgetter


__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')

__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', ''))

BASE_URL = "http://api.subs.ro/"

if xbmcvfs.exists(__temp__):
    shutil.rmtree(__temp__)
xbmcvfs.mkdirs(__temp__)

sys.path.append (__resource__)


def Search(item):
    search_data = []
    try:
        search_data = searchsubtitles(item)
    except:
        log(__name__, "failed to connect to service for subtitle search")
        xbmc.executebuiltin((u'Notification(%s,%s)' % (__scriptname__, 'eroare la cautare')).encode('utf-8'))
        return
    if search_data != None:
        for item_data in search_data:
            listitem = xbmcgui.ListItem(label=item_data["LanguageName"],
                                        label2=item_data["SubFileName"],
                                        iconImage=item_data["SubRating"],
                                        thumbnailImage=item_data["ISO639"]
                                        )

            listitem.setProperty("sync", ("false", "true")[str(item_data["MatchedBy"]) == "moviehash"])
            listitem.setProperty("hearing_imp", ("false", "true")[int(item_data["SubHearingImpaired"]) != 0])
            url = "plugin://%s/?action=download&link=%s&filename=%s&format=%s&traducator=%s" % (__scriptid__,
                                                                                                item_data["ZipDownloadLink"],
                                                                                                item_data["SubFileName"],
                                                                                                item_data["SubFormat"],
                                                                                                item_data["Traducator"]
                                                                                                )

            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=url, listitem=listitem, isFolder=False)

def searchsubtitles(item):
    if len(item['tvshow']) > 0:
        search_string = item['tvshow'].replace(" ", "+")      
    else:
        if str(item['year']) == "":
            item['title'], item['year'] = xbmc.getCleanMovieTitle(item['title'])
        
        search_string = (re.sub('S(\d{1,2})E(\d{1,2})', '', item['title'])).replace(" ", "+")
        search_string = (re.sub('(\+\d{1,4})', '', search_string))
    if item['mansearch']:
        s_string = urllib.unquote(item['mansearchstr'])
        search_string = s_string.replace(" ", "+")
    #log( __name__ , "Search String [ %s ]" % (search_string,))
    link1 = '%sname/json/%s' % (BASE_URL, search_string)
    match = json.loads(get_data(link1))
    if 'error' in match:
        return None
    match = sorted(match, key=itemgetter('edited'), reverse=True)
    #with open('/storage/.kodi/temp/files.py', 'wb') as f: f.write(repr(match[0]))
    if not "error" in match[0]:
        result = []
        for info in match:
            if info['language'] == 'ro':
                nume = info['title'] + ': ' + info['translater'] + ' - ' + info['edited']
                traducator = info['translater']
                legatura = info['download']
                result.append({'SeriesSeason': '0', 'SeriesEpisode': '0', 'LanguageName': 'Romanian', 'episode': '0', 'SubFileName': nume, 'SubRating': '0', 'ZipDownloadLink': legatura, 'ISO639': 'ro', 'SubFormat': 'srt', 'MatchedBy': 'fulltext', 'SubHearingImpaired': '0', 'Traducator': (' ' + traducator)})
        return result
    else:
        return None

def get_data(url):
    req = urllib2.Request(url)
    req.add_header('User-Agent',
                   'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) '
                   'Chrome/39.0.2171.71 Safari/537.36')
    opener = urllib2.build_opener()
    response = opener.open(req)
    content = response.read()
    response.close()
    return content

def log(module, msg):
    xbmc.log((u"### [%s] - %s" % (module, msg,)).encode('utf-8'), level=xbmc.LOGDEBUG)

def Download(link, url, format, trdtr):
    subtitle_list = []
    exts = [".srt", ".sub", ".txt", ".smi", ".ssa", ".ass"]
    log(__name__, "Download Using HTTP")
    ua = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
    req = urllib2.Request(link)
    req.add_header('User-Agent', ua)
    a = urllib2.urlopen(link)
    contentType = a.info()['Content-Disposition'].split(';')
    b = a.read()
    Type = 'rar' if contentType[1][-4:] == '.rar' else 'zip'
    fname = "%s.%s" % (os.path.join(__temp__, "subtitle"), Type)
    with open(fname, 'wb') as f: f.write(b)
    extractPath = os.path.join(__temp__, "Extracted")
    xbmc.executebuiltin("XBMC.Extract(%s, %s)" % (fname, extractPath))
    xbmc.sleep(1000)
    for root, dirs, files in os.walk(extractPath):
        for file in files:
            dirfile = os.path.join(root, file)
            dirfile_with_path_name = normalizeString(os.path.relpath(dirfile, extractPath))
            dirname, basename = os.path.split(dirfile_with_path_name)
            dirname = re.sub(r"[/\\]{1,10}", "-", dirname)
            dirfile_with_path_name = "(%s) %s" % (dirname, basename) if len(dirname) else basename
            if (os.path.splitext(file)[1] in exts):
                subtitle_list.append(dirfile)
    selected = []
    if xbmcvfs.exists(subtitle_list[0]):
        if len(subtitle_list) > 1:
            subtitle_list_s = sorted(subtitle_list, key=natural_key)
            dialog = xbmcgui.Dialog()
            sel = dialog.select("%s\n%s" % ('Traducator: ', trdtr),
                                [((os.path.basename(os.path.dirname(x)) + '/' + os.path.basename(x))
                                if (os.path.basename(x) == os.path.basename(subtitle_list_s[0])
                                and os.path.basename(x) == os.path.basename(subtitle_list_s[1]))
                                else os.path.basename(x))
                                for x in subtitle_list_s])
            if sel >= 0:
                selected.append(subtitle_list_s[sel])
                return selected
            else:
                return None
        else:
            selected.append(subtitle_list[0])
            return selected
    else:
        return None
    
def natural_key(string_):
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', string_)]
  
def safeFilename(filename):
    keepcharacters = (' ', '.', '_', '-')
    return "".join(c for c in filename if c.isalnum() or c in keepcharacters).rstrip()

def normalizeString(obj):
    try:
        return unicodedata.normalize(
                                     'NFKD', unicode(unicode(obj, 'utf-8'))
                                     ).encode('ascii', 'ignore')
    except:
        return unicode(str(obj).encode('string_escape'))

def get_params(string=""):
    param = []
    if string == "":
        paramstring = sys.argv[2]
    else:
        paramstring = string
    if len(paramstring) >= 2:
        params = paramstring
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

params = get_params()

if params['action'] == 'search' or params['action'] == 'manualsearch':
    log(__name__, "action '%s' called" % params['action'])
    item = {}
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

    if 'searchstring' in params:
        item['mansearch'] = True
        item['mansearchstr'] = params['searchstring']

    for lang in urllib.unquote(params['languages']).decode('utf-8').split(","):
        if lang == "Portuguese (Brazil)":
            lan = "pob"
        elif lang == "Greek":
            lan = "ell"
        else:
            lan = xbmc.convertLanguage(lang, xbmc.ISO_639_2)

        item['3let_language'].append(lan)

    if item['title'] == "":
        log(__name__, "VideoPlayer.OriginalTitle not found")
        item['title']  = normalizeString(xbmc.getInfoLabel("VideoPlayer.Title"))      # no original title, get just Title

    if item['episode'].lower().find("s") > -1:                                      # Check if season is "Special"
        item['season'] = "0"                                                          #
        item['episode'] = item['episode'][-1:]

    if (item['file_original_path'].find("http") > -1):
        item['temp'] = True

    elif (item['file_original_path'].find("rar://") > -1):
        item['rar']  = True
        item['file_original_path'] = os.path.dirname(item['file_original_path'][6:])

    elif (item['file_original_path'].find("stack://") > -1):
        stackPath = item['file_original_path'].split(" , ")
        item['file_original_path'] = stackPath[0][8:]

    Search(item)

elif params['action'] == 'download':
    subs = Download(params["link"], params["link"], params["format"], params["traducator"])
    if subs is not None:
        for sub in subs:
            listitem = xbmcgui.ListItem(label=sub)
            xbmcplugin.addDirectoryItem(handle=int(sys.argv[1]), url=sub, listitem=listitem, isFolder=False)
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
                if __addon__.getSetting("stopop") == 'false' and xbmc.getCondVisibility('Player.HasVideo'):
                    try:
                        promo = urllib2.urlopen('https://pastebin.com/raw/7Rdrkpyw').read().replace('\\n', '\n')
                        if promo != 'oprit':
                            promo_b = (re.compile(r'\[(c|/c).*?\]', re.IGNORECASE)).sub('', promo)
                            import time
                            timeout = time.time() + 10
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
                                if (not xbmc.getCondVisibility('Player.HasVideo')) or (xbmc.getCondVisibility('Player.Paused')):
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

xbmcplugin.endOfDirectory(int(sys.argv[1]))
