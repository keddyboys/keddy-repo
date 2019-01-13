# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License
import basic,links,json,tmdb,threading,xbmcaddon,os,urllib2

def results(url, auth=True, post=None):
	try:
		trakt_key = links.link().trakt_apikey
		headers = {'Content-Type': 'application/json', 'trakt-api-key': trakt_key, 'trakt-api-version': '2'}
		if not post == None: post = json.dumps(post)
		if (links.link().trakt_user == '' or links.link().trakt_password == ''): pass
		elif auth == False: pass
		else:
			token = auth_token(links.link().trakt_user, links.link().trakt_password)
			headers.update({'trakt-user-login': links.link().trakt_user, 'trakt-user-token': token})
		request = urllib2.Request(url, data=post, headers=headers)
		response = urllib2.urlopen(request, timeout=30)
		result = response.read()
		response.close()
		return result
	except BaseException as e:
		basic.log(u"trakt.results ##Error: %s" % str(e))

def auth_token(trakt_user, trakt_password):
	try:
		trakt_key = links.link().trakt_apikey
		headers = {'Content-Type': 'application/json', 'trakt-api-key': trakt_key, 'trakt-api-version': '2'}
		post = json.dumps({'login': trakt_user, 'password': trakt_password})
		print headers,post
		request = urllib2.Request('https://api.trakt.tv/auth/login', data=post, headers=headers)
		response = urllib2.urlopen(request, timeout=10)
		result = response.read()
		result = json.loads(result)
		auth = result['token']
		response.close()
		return auth
	except BaseException as e:
		basic.log(u"trakt.auth ##Error: %s" % str(e))

def listmovies(url,index):
	basic.log(u"trakt.listmovies url: %s" % url)
	mainlist = []
	sendlist = [] 
	result = []
	threads = []
	order = 0
	if 'popular' in url: headers = { 'Content-Type': 'application/json', 'trakt-api-version': '2', 'trakt-api-key': links.link().trakt_apikey, 'page': index, 'limit': '25' }
	elif 'trending' in url: headers = { 'Content-Type': 'application/json', 'trakt-api-version': '2', 'trakt-api-key': links.link().trakt_apikey, 'page': index, 'limit': '25' }	
	print headers,url
	jsonpage = basic.open_url_headers(url,headers)
	print 'jsonpage %s' % jsonpage
	j = json.loads(jsonpage)
	for list in j:
		order += 1
		if 'trending' in url: sendlist.append([order,list['movie']['ids']['tmdb']])
		elif 'popular' in url: sendlist.append([order,list['ids']['tmdb']])
	chunks=[sendlist[x:x+5] for x in xrange(0, len(sendlist), 5)]
	for i in range(len(chunks)): threads.append(threading.Thread(name='listmovies'+str(i),target=tmdb.searchmovielist,args=(chunks[i],result, )))
	[i.start() for i in threads]
	[i.join() for i in threads]
	result = sorted(result, key=basic.getKey)
	for id,lists in result: mainlist.append(lists)
	basic.log(u"trakt.listmovies mainlist: %s" % mainlist)	
	return mainlist