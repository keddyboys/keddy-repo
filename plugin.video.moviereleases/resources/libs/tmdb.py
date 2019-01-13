# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License
import basic,links,json,omdbapi,threading,xbmcaddon,os,localdb

LANG = basic.get_api_language()
getSetting          = xbmcaddon.Addon().getSetting

def listmovies(url):
	basic.log(u"tmdb.listmovies url: %s" % url)
	mainlist = []
	sendlist = [] 
	result = []
	threads = []
	order = 0
	jsonpage = basic.open_url(url)
	j = json.loads(jsonpage)
	for list in j['results']: 
		order += 1
		sendlist.append([order,list['id']])
	chunks=[sendlist[x:x+5] for x in xrange(0, len(sendlist), 5)]
	for i in range(len(chunks)): threads.append(threading.Thread(name='listmovies'+str(i),target=searchmovielist,args=(chunks[i],result, )))
	[i.start() for i in threads]
	[i.join() for i in threads]
	result = sorted(result, key=basic.getKey)
	for id,lists in result: mainlist.append(lists)
	basic.log(u"tmdb.listmovies mainlist: %s" % mainlist)	
	return mainlist

def searchmovielist(list,result):
	basic.log(u"tmdb.searchmovielist list: %s" % list)
	for num,id in list: 
		moviedata = searchmovie(id)
		if moviedata: result.append([num,moviedata])
	basic.log(u"tmdb.searchmovielist result: %s" % result)
	
def searchmovie(id):
	basic.log(u"tmdb.searchmovie id: %s" % id)
	listgenre = []
	listcast = []
	listcastr = []	
	genre = ''
	title = ''
	plot = ''
	tagline = ''
	director = ''
	writer = ''
	credits = ''
	poster = ''
	fanart = ''
	temptitle = ''
	originaltitle = ''
	if getSetting("cachesites") == 'true':
		cached = localdb.get_cache(id)
		if cached:
			response = { "label": cached[2], "originallabel": cached[3], "poster": cached[4], "fanart_image": cached[5], "imdbid": cached[0], "year": cached[6], "info": json.loads(cached[7]) }
			return response
	jsonpage = basic.open_url(links.link().tmdb_info_default % (id))
	try: jdef = json.loads(jsonpage)
	except:
		if 'tt' in str(id):
			try: 
				jdef = omdbapi.searchmovie(str(id))
				return jdef
			except: return False
		else: return False
	if LANG <> 'en':
		try:
			jsonpage = basic.open_url(links.link().tmdb_info % (id,LANG))
			j = json.loads(jsonpage)
			temptitle = j['title'].encode('ascii','ignore').replace(' ','')
			if temptitle <> '': title = j['title']
			fanart = links.link().tmdb_backdropbase % (j["backdrop_path"])
			poster = links.link().tmdb_posterbase % (j["poster_path"])
			for g in j['genres']: listgenre.append(g['name'])
			genre = ', '.join(listgenre)
			try: plot = j['overview']
			except: pass
			try: tagline = j['tagline']
			except: pass
			fanart = j["backdrop_path"]
			poster = j["poster_path"]
		except: pass
	temptitle = jdef['title'].encode('ascii','ignore').replace(' ','')
	if temptitle <> '':
		if not title: title = jdef['title']
	temporiginaltitle = jdef['original_title'].encode('ascii','ignore')
	if temptitle == '': originaltitle = jdef['title']
	if temporiginaltitle == '': originaltitle = jdef['title']
	else: originaltitle = jdef['original_title']
	if not poster: poster = jdef['poster_path']
	if not fanart: fanart = jdef['backdrop_path']
	if not fanart: fanart = poster
	if fanart: fanart = links.link().tmdb_backdropbase % (fanart)
	if poster: poster = links.link().tmdb_posterbase % (poster)	
	if genre == '':
		for g in jdef['genres']: listgenre.append(g['name'])
		genre = ', '.join(listgenre)
	if not plot: plot = jdef['overview']
	if not tagline: tagline = jdef['tagline']
	try: trailer = links.link().youtube_plugin % (jdef['trailers']['youtube'][0]['source'])
	except: trailer = ''
	try: year = jdef["release_date"].split("-")[0]
	except: year = ''
	try: studio = jdef['production_companies'][0]['name']
	except: studio = ''
	for listc in jdef['credits']['cast']: 
		listcastr.append(listc['name']+'|'+listc['character'])
		listcast.append(listc['name'])
	for crew in jdef['credits']['crew']:
		if crew['job'] == 'Director': director = crew['name']
		break
	for crew in jdef['credits']['crew']:
		if crew['job'] == 'Story': credits = crew['name']
		break		
	for crew in jdef['credits']['crew']:
		if crew['job'] == 'Writer': 
			writer = crew['name']
			break
		if crew['job'] == 'Novel': 
			writer = crew['name']
			break
		if crew['job'] == 'Screenplay': 
			writer = crew['name']
			break
	duration = jdef['runtime']
	if not poster or duration == 0 and jdef['imdb_id']:
		altsearch = omdbapi.searchmovie(jdef['imdb_id'],False)
		if not poster: poster = altsearch['poster']
		if not fanart: fanart = poster
		if not plot: plot = altsearch['info']['plot']
		if not tagline: tagline = altsearch['info']['plot']	
		if not listcast: 
			listcast = altsearch['info']['cast']
			listcastr = []
		if not duration: duration = altsearch['info']['duration']
		if not writer: writer = altsearch['info']['writer']
		if not director: director = altsearch['info']['director']		
		if not genre: genre = altsearch['info']['genre']
	info = {
			"genre": genre, 
			"year": year,
			"rating": jdef['vote_average'], 
			"cast": listcast,
			"castandrole": listcastr,
			"director": director,
			"plot": plot,
			"plotoutline": plot,
			"title": title,
			"originaltitle": originaltitle,
			"duration": duration,
			"studio": studio,
			"tagline": tagline,
			"writer": writer,
			"premiered": jdef['release_date'],
			"code": jdef['imdb_id'],
			"credits": credits,
			"votes": jdef['vote_count'],
			"trailer": trailer
			}
	response = {
		"label": '%s (%s)' % (title,year),
		"originallabel": '%s (%s)' % (originaltitle,year),		
		"poster": poster,
		"fanart_image": fanart,
		"imdbid": jdef['imdb_id'],
		"year": year,
		"info": info
		}
	if getSetting("cachesites") == 'true':
		if not str(id).startswith('tt'): tmdbid = id
		else: tmdbid = jdef['id']
		localdb.save_cache(jdef['imdb_id'],tmdbid,'%s (%s)' % (title,year),'%s (%s)' % (originaltitle,year),poster,fanart,year,json.dumps(info))
	return response
