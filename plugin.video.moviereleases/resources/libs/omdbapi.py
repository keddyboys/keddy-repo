# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License
import links,json,basic,re,xbmcaddon,os,localdb

getSetting          = xbmcaddon.Addon().getSetting

def listmovies(url):
	basic.log(u"omdbapi.listmovies url: %s" % url)
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
	basic.log(u"omdbapi.listmovies mainlist: %s" % mainlist)	
	return mainlist

def searchmovielist(list,result):
	basic.log(u"omdbapi.searchmovielist list: %s" % list)
	if len(list) > 2:
            searching = []
            for num,imagine,nume,an,regia,actori,gen,nota,trailer,descriere in list:
                moviedata = searchmovie([num,imagine,nume,an,regia,actori,gen,nota,trailer,descriere],'an')
                if moviedata: result.append([num,moviedata])
        else:
            for num,id in list: 
		moviedata = searchmovie(id)
		if moviedata: result.append([num,moviedata])
	#basic.log(u"omdbapi.searchmovielist result: %s" % result)

def striphtml(data):
        p = re.compile(r'<.*?>')
        p = p.sub('', data)
        p = " ".join(p.split())
        return p.strip()

def searchmovie(id,an=None,cache=True):
	basic.log(u"omdbapi.searchmovie id: %s" % id)
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
	trailer = ''
	year = ''
	dur = 0
	if cache:
		if getSetting("cachesites") == 'true':
			cached = localdb.get_cache(id,an)
			if cached:
				response = { "label": cached[2], "originallabel": cached[3], "poster": cached[4], "fanart_image": cached[5], "imdbid": cached[0], "year": cached[6], "info": json.loads(cached[7]) }
				return response
        if an:
                ordine = id[0]
                imagine = id[1]
                nume = id[2]
                an = id[3]
                regia = id[4]
                actori = id[5]
                gen = id[6]
                nota = id[7]
                trailer = id[8]
                descriere = id[9]
                id = '1'
                #jsonpage = basic.open_url(links.link().omdbapi_byname % (nume.encode('ascii','xmlcharrefreplace'), an))
                jsonpage={}
	else: jsonpage = basic.open_url(links.link().omdbapi_info % (id))
	try:
            jdef = json.loads(jsonpage)
        except:
            try: nume = nume.decode('utf-8')
            except: nume = nume
            jdef = {'Title': nume,
                    'Poster': imagine,
                    'Genre': striphtml(gen),
                    'Plot': descriere,
                    'Year': an,
                    'Actors': re.sub('Cu: ','',striphtml(actori)),
                    'Director': re.sub('Regia: ','',striphtml(regia)),
                    'Writer': '',
                    'Runtime': '',
                    'imdbRating': re.sub('IMDB: ','',nota),
                    'imdbVotes': '',
                    'trailer': trailer}
	try: title = jdef['Title']
	except: title = nume
	try: poster = jdef['Poster']
	except: poster = imagine
	fanart = poster
	try: genre = jdef['Genre']
	except: genre = striphtml(gen)
	try: plot = jdef['Plot']
	except: plot = descriere
	tagline = plot
	try: year = re.findall('(\d+)', jdef['Year'], re.DOTALL)[0]
	except:
            try: year = jdef['Year']
            except: year = an
	try: listcast = jdef['Actors'].split(', ')
	except: listcast = re.sub('Cu: ','',striphtml(actori)).split(', ')
	try: director = jdef['Director']
	except: director = re.sub('Regia: ','',striphtml(regia))
	try: writer = jdef['Writer']
	except: writer = ''
	try:
            duration = re.findall('(\d+) min', jdef['Runtime'], re.DOTALL)
            if duration: dur = int(duration[0])
            else: 
		duration = re.findall('(\d) h', jdef['Runtime'], re.DOTALL)
		if duration: dur = int(duration[0])*60
        except: duration = ''
        try: rating = jdef['imdbRating']
        except: rating = re.sub('IMDB: ','',nota)
        try: votes = jdef['imdbVotes']
        except: votes = ''
        try: trailer = jdef['trailer']
        except: trailer = ''
	info = {
			"genre": genre, 
			"year": year,
			"rating": rating, 
			"cast": listcast,
			"castandrole": listcast,
			"director": director,
			"plot": plot,
			"plotoutline": plot,
			"title": title,
			"originaltitle": title,
			"duration": dur,
			"studio": '',
			"tagline": tagline,
			"writer": writer,
			"premiered": '',
			"code": id,
			"credits": '',
			"votes": votes,
			"trailer": trailer
			}		
	response = {
		"label": '%s (%s)' % (title,year),
		"originallabel": '%s (%s)' % (title,year),
		"poster": poster,
		"fanart_image": fanart,
		"imdbid": id,
		"year": year,
		"info": info
		}
	if cache:
		if getSetting("cachesites") == 'true': localdb.save_cache(id,'','%s (%s)' % (title,year),'%s (%s)' % (title,year),poster,fanart,year,json.dumps(info),an)
	return response
