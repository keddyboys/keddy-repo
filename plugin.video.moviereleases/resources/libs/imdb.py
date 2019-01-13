# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License

import re,threading,xbmcgui
import basic,tmdb
from BeautifulSoup import BeautifulSoup
from resources.libs import links
import datetime

def listmovies(url):
	basic.log(u"imdb.listmovies url: %s" % url)
	mainlist = []
	sendlist = [] 
	result = []
	threads = []
	order = 0
	htmlpage = basic.open_url(url)
	found = re.findall('data-tconst="(.+?)"',htmlpage, re.DOTALL)
	for imdb_id in sorted(set(found), key=lambda x: found.index(x)): 
		order += 1
                sendlist.append([order,imdb_id])
        #with open('/root/.kodi/temp/files.py', 'wb') as f: f.write(repr(sorted(set(found), key=lambda x: found.index(x))))
	chunks=[sendlist[x:x+5] for x in xrange(0, len(sendlist), 5)]
	for i in range(len(chunks)): threads.append(threading.Thread(name='listmovies'+str(i),target=tmdb.searchmovielist,args=(chunks[i],result, )))
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
	
def getlinks(url,results,order,Source=None):
	basic.log(u"imdb.getlinks url: %s" % url)
	try:
		html_page = basic.open_url(url)
		if html_page:
			soup = BeautifulSoup(html_page)
			if Source == 'IMDB':
				for link in soup.findAll('a', attrs={'href': re.compile("^/title/.+?/\?ref_=.+?_ov_tt")}):
					if '?' in link.get('href'): cleanlink = link.get('href').split("?")[0].split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
					else: cleanlink = link.get('href').split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
					results.append([order, cleanlink])
					order += 1			
			else:
				for link in soup.findAll('a', attrs={'href': re.compile("^http://.+?/title/")}):
					if '?' in link.get('href'): cleanlink = link.get('href').split("?")[0].split("/title/")[1].replace('/','').replace('awards','').replace('videogallery','')
					else: cleanlink = link.get('href').split("title")[1].replace('/','').replace('awards','').replace('videogallery','')
					results.append([order, cleanlink])
					order += 1
			basic.log(u"imdb.getlinks results: %s" % results)
			return results
	except BaseException as e: basic.log(u"imdb.getlinks ERROR: %s - %s" % (str(url),str(e)))
