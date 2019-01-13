# -*- coding: UTF-8 -*-

import re,threading,xbmcgui,xbmc
import basic,tmdb,omdbapi
from resources.libs import links
import datetime

def listmovies(url, tip):
	basic.log(u"cnmg.listmovies url: %s" % url)
	mainlist = []
	sendlist = [] 
	result = []
	threads = []
	order = 0
	if tip == 'liste':
            htmlpage = basic.open_url(url)
            regex = '''<li class="list_item clearfix">(.+?)</li>'''
            regex2 = '''<a [^>]*href\s*=\s*"[^"]*imdb.com/title/(.*?)/"'''
            for lists in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage):
                for imdb_id in re.compile(regex2, re.DOTALL).findall(lists):
                    order += 1
                    sendlist.append([order,imdb_id])
            target = tmdb.searchmovielist
        elif tip == 'filme':
            headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Referer': url,
                   'Cookie': 'ps=30'}
            htmlpage = basic.open_url_headers(url, headers)
            regex = '''<div class="poza">(.+?)</div>\n</li>'''
            regex2 = '''img src="(.+?)".+?<h2>.+?title.+?>(.+?)<.+?\((\d+)\).*(?:^$|<li>(.+?)</li>).*(?:^$|<li>(.+?)</li>).+?Gen.+?">(.+?)</ul>.+?(?:^$|\((.+?)\)).+?body".+?(?:^$|href="(.+?)".+?)(?:^$|<span>(.+?)</span>)'''
            for lists in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage):
                for imagine,nume,an,regia,actori,gen,nota,trailer,descriere in re.compile(regex2, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(lists):
                    order += 1
                    nume = nume.decode('utf-8')
                    sendlist.append([order,imagine,nume,an,regia,actori,gen,nota,trailer,descriere])
            target = omdbapi.searchmovielist
	chunks=[sendlist[x:x+5] for x in xrange(0, len(sendlist), 5)]
	for i in range(len(chunks)): threads.append(threading.Thread(name='listmovies'+str(i),target=target,args=(chunks[i],result, )))
	[i.start() for i in threads]
	[i.join() for i in threads]
	result = sorted(result, key=basic.getKey)
	for id,lists in result: mainlist.append(lists)
	basic.log(u"imdb.listmovies mainlist: %s" % mainlist)
	return mainlist

def getgenre(url):
	genrechoice = xbmcgui.Dialog().select
	htmlpage = basic.open_url(url)	
	found = re.findall('<h3>Popular Movies by Genre</h3>.+?</html>',htmlpage, re.DOTALL)
	newfound = re.findall('<a href="/genre/(.+?)\?',found[0], re.DOTALL)
	choose=genrechoice("select",newfound)
	if choose > -1:	return newfound[choose]

def getyear():
        now_year = datetime.datetime.now().year
        year = []
        while (now_year > 1920):
            year.append(str(now_year))
            now_year -= 1
	yearchoice = xbmcgui.Dialog().select
	choose=yearchoice("select",year)
	if choose > -1:	return year[choose]

def getyearbygenre():
        genre = getgenre(links.link().imdb_genre)
        year = getyear(links.link().imdb_year)
	if genre and year: return genre, year

def striphtml(data):
    p = re.compile(r'<.*?>')
    p = p.sub('', data)
    p = " ".join(p.split())
    return p.strip()

def getliste(url):
        htmlpage = basic.open_url(url)
        liste = []
        order = 0
        regex = '''<div class="list_preview clearfix">(.+?)<div class="list_meta">(.+?)</div>'''
        regex2 = '''img src="(.+?)".+?"up">(.+?)<.+?"down">(.+?)<.+?list_name.+?<a href="(.+?)">(.+?)</a>'''
        #with open('/root/.kodi/temp/files.py', 'wb') as f: f.write(repr(htmlpage))
        for lists in re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage):
            for imagine, aprecieri, deprecieri, link, nume in re.compile(regex2, re.DOTALL).findall(lists[0]):
                order += 1
                nume = nume.decode('utf-8').strip()
                nume += ' (%s filme) ' % (re.findall('cu.+?(\d+)', lists[1])[0])
                info = (striphtml(lists[1]).strip()).decode('utf-8')
                info += ' | Cu %s aprecieri si %s deprecieri' % (aprecieri, deprecieri)
                descriere = {'plot': info, 'title': nume}
                liste.append([order, imagine, link, nume, descriere])
        return liste

def gettari(url, tip=''):
        htmlpage = basic.open_url(url)
        tarisoara = []
        order = 0
        regex = '''class="filters_list">(.+?)</div'''
        regex2 = '''<a href="(.+?)".+?>(.+?)<'''
        tari = re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage)
        if tip == 'tari': search = tari[2]
        elif tip == 'gen': search = tari[0]
        for link, nume in re.compile(regex2, re.DOTALL).findall(search):
            order += 1
            nume = nume.decode('utf-8')
            tarisoara.append([order, link, nume])
        return tarisoara
	
def playtrailer(url,name):
	if url == None: return
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:51.0) Gecko/20100101 Firefox/51.0',
                   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                   'Referer': url}
        htmlpage = basic.open_url_headers(url, headers)
        regex = '''<iframe[^>]+src=["\']([http].+?)"'''
        regex2 = '''<source[^>]+src=["\']([http].+?)\''''
        source = re.compile(regex, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(htmlpage)[0]
        getlink = basic.open_url_headers(source, headers)
        link = re.compile(regex2, re.IGNORECASE | re.MULTILINE | re.DOTALL).findall(getlink)[-1]
	item = xbmcgui.ListItem(name + ' - Trailer', path=link)
	item.setProperty("IsPlayable", "true")
	xbmc.Player().play(link, item)
