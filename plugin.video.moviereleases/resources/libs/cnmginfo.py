# -*- coding: UTF-8 -*-


import links,json,basic,re,xbmcaddon,os,localdb
getSetting          = xbmcaddon.Addon().getSetting

def searchmovielist(list,result):
	#basic.log(u"cnmginfo.searchmovielist list: %s" % list)
	#with open('/root/.kodi/temp/files.py', 'wb') as f: f.write(repr(list))
        searching = []
        for num,imagine,nume,an,regia,actori,gen,nota,descriere in list:
            moviedata = searchmovie([num,imagine,nume,an,regia,actori,gen,nota,descriere],'an')
            if moviedata: result.append([num,moviedata])

def striphtml(data):
    try:
        p = re.compile(r'<.*?>')
        p = p.sub('', data)
        p = " ".join(p.split())
        return p.strip()
    except:
        return data

def searchmovie(id,an=None,cache=True):
	basic.log(u"cnmginfo.searchmovie id: %s" % id)
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
        ordine = id[0]
        imagine = id[1]
        nume = id[2]
        an = id[3]
        regia = re.sub('Regia: ','',striphtml(id[4])) if id[4] else ''
        actori = re.sub('Cu: ','',striphtml(id[5])) if id[5] else ''
        gen = striphtml(id[6])
        nota = re.sub('IMDB: ','',id[7])
        descriere = id[8]
        id = '1'
        try: nume = nume.decode('utf-8')
        except: nume = nume
        jdef = {'Title': nume,
                'Poster': imagine,
                'Genre': gen,
                'Plot': descriere,
                'Year': an,
                'Actors': actori,
                'Director': regia,
                'Writer': '',
                'Runtime': '',
                'imdbRating': nota,
                'imdbVotes': ''}
	try: title = jdef['Title']
	except: title = nume
	try: poster = jdef['Poster']
	except: poster = imagine
	fanart = poster
	try: genre = jdef['Genre']
	except: genre = gen
	try: plot = jdef['Plot']
	except: plot = descriere
	tagline = plot
	try: year = re.findall('(\d+)', jdef['Year'], re.DOTALL)[0]
	except:
            try: year = jdef['Year']
            except: year = an
	try: listcast = jdef['Actors'].split(', ')
	except: listcast = actori
	try: director = jdef['Director']
	except: director = regia
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
        except: rating = nota
        try: votes = jdef['imdbVotes']
        except: votes = ''
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
			"trailer": ''
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
	#if cache:
            #if getSetting("cachesites") == 'true': localdb.save_cache(id,'','%s (%s)' % (title,year),'%s (%s)' % (title,year),poster,fanart,year,json.dumps(info),an)
	return response
