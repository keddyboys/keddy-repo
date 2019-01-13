# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License
import basic,links,json,tmdb,threading,xbmcaddon,os

def listmovies(url):
	basic.log(u"rotten.listmovies url: %s" % url)
	mainlist = []
	sendlist = [] 
	result = []
	threads = []
	order = 0
	jsonpage = basic.open_url(url)
	print 'jsonpage %s' % jsonpage
	j = json.loads(jsonpage)
	for list in j['movies']:
		order += 1
		try: sendlist.append([order,'tt'+list['alternate_ids']['imdb']])
		except: pass
	chunks=[sendlist[x:x+5] for x in xrange(0, len(sendlist), 5)]
	for i in range(len(chunks)): threads.append(threading.Thread(name='listmovies'+str(i),target=tmdb.searchmovielist,args=(chunks[i],result, )))
	[i.start() for i in threads]
	[i.join() for i in threads]
	result = sorted(result, key=basic.getKey)
	for id,lists in result: mainlist.append(lists)
	basic.log(u"rotten.listmovies mainlist: %s" % mainlist)	
	return mainlist