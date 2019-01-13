# -*- coding: UTF-8 -*-
# by Mafarricos
# email: MafaStudios@gmail.com
# This program is free software: GNU General Public License
import xbmcaddon

getSetting          = xbmcaddon.Addon().getSetting

class link:
	def __init__(self):
		import base64
		self.omdbapi_info = 'http://www.omdbapi.com/?plot=short&r=json&i=%s'
		self.omdbapi_byname = 'http://www.omdbapi.com/?t=%s+&y=%s&plot=full&r=json'
		self.tmdb_base = 'http://api.themoviedb.org/3/movie/%s'
		self.tmdb_image = 'http://image.tmdb.org/t/p/%s'
		self.tmdb_key = base64.urlsafe_b64decode('ODFlNjY4ZTdhMzdhM2Y2NDVhMWUyMDYzNjg3ZWQ3ZmQ=')
		self.tmdb_info = self.tmdb_base % ('%s?language=%s&api_key='+self.tmdb_key)
		self.tmdb_info_default = self.tmdb_base % ('%s?append_to_response=trailers,credits&api_key='+self.tmdb_key)
		self.tmdb_info_default_alt = self.tmdb_base % ('%s?language=ge&append_to_response=trailers,credits&api_key='+self.tmdb_key)
		self.tmdb_theaters = self.tmdb_base % ('now_playing?page=%s&api_key='+self.tmdb_key)
		self.tmdb_upcoming = self.tmdb_base % ('upcoming?page=%s&api_key='+self.tmdb_key)
		self.tmdb_popular = self.tmdb_base % ('popular?page=%s&api_key='+self.tmdb_key)
		self.tmdb_top_rated = self.tmdb_base % ('top_rated?page=%s&api_key='+self.tmdb_key)			
		self.tmdb_backdropbase = self.tmdb_image % ('original%s')
		self.tmdb_posterbase = self.tmdb_image % ('w500%s')
		self.tmdb_discover = 'http://api.themoviedb.org/3/discover/movie?page=%s&sort_by=popularity.desc&api_key='+self.tmdb_key
		self.tmdb_search ='http://api.themoviedb.org/3/search/movie?include_adult=false&query=%s&api_key='+self.tmdb_key
		self.youtube_trailer_search = 'https://www.googleapis.com/youtube/v3/search?part=id%2Csnippet&q=%s-Trailer&maxResults=1&key=AIzaSyCtxrgktLdk4Y6dTcqeYw3U9-3H_wvtP6E'
		self.youtube_plugin = 'plugin://plugin.video.youtube/?action=play_video&videoid=%s'
		
		self.imdb_top250 = 'http://akas.imdb.com/chart/top'
		self.imdb_bot100 = 'http://akas.imdb.com/chart/bottom'
		self.imdb_theaters = 'http://www.imdb.com/movies-in-theaters/'
		self.imdb_coming_soon = 'http://www.imdb.com/movies-coming-soon/'	
		self.imdb_popular = 'http://akas.imdb.com/search/title?sort=moviemeter,asc&title_type=feature,tv_movie&count=30&start=%s'
		self.imdb_popularbygenre = 'http://akas.imdb.com/search/title?sort=moviemeter,asc&title_type=feature,tv_movie&count=30&start=%s&genres=%s'
		self.imdb_popularbyyear = 'http://akas.imdb.com/search/title?sort=moviemeter,asc&title_type=feature,tv_movie&count=30&start=%s&year=%s'
		self.imdb_boxoffice = 'http://akas.imdb.com/search/title?sort=boxoffice_gross_us&title_type=feature,tv_movie&count=30&start=%s'
		self.imdb_most_voted = 'http://akas.imdb.com/search/title?sort=num_votes&title_type=feature,tv_movie&count=30&start=%s'
		self.imdb_oscars = 'http://akas.imdb.com/search/title?count=30&groups=oscar_best_picture_winners&sort=year,desc&start=%s'
		self.imdb_amazon = 'http://rss.imdb.com/list/ls002595589'
		self.imdb_dvd = 'http://rss.imdb.com/list/ls075513547'
		self.imdb_api_search = 'http://www.imdb.com/xml/find?json=1&nr=1&tt=on&q=%s'
		self.imdb_years = 'http://akas.imdb.com/search/title?title_type=feature,tv_movie&sort=boxoffice_gross_us&count=30&start=%s&year=%s,%s'
		self.imdb_genre = 'http://www.imdb.com/chart/boxoffice/'
		self.imdb_year = 'http://www.imdb.com/year/'
		self.imdb_year_genre = 'http://akas.imdb.com/search/title?year=%s,%s&title_type=feature&explore=genres&genres=%s&page=%s'
		
		self.cnmg = 'http://www.cinemagia.ro/liste/cele-mai-interesante-filme-5578/'
		self.cnmg_liste = 'http://www.cinemagia.ro/liste/filme/?pn=%s'
		self.cnmg_filme = 'http://www.cinemagia.ro/filme/?&pn=%s'
		
		self.trakt_user, self.trakt_password = getSetting("trakt_user"), getSetting("trakt_password")	
		self.trakt_base_s = 'https://api.trakt.tv/%s'
		if getSetting("trakt_api") <> '': self.trakt_apikey = getSetting("trakt_api")
		else: self.trakt_apikey = base64.urlsafe_b64decode('M2Q4OTdlNWFiNDkxMWIwMzYwZGQ4NGNmYmQzZTA3NzljZTg2OTM2ZmNjYmYwMDBjYTdlMjFkNWY4ZjBiNDk2ZA==')
		self.trakt_popular = self.trakt_base_s % 'movies/popular'
		self.trakt_trending = self.trakt_base_s % 'movies/trending'
		self.trakt_history = self.trakt_base_s % 'sync/history'
		self.trakt_history_remove = self.trakt_base_s % 'sync/history/remove'

		
		self.addon_plugin 	= 'plugin://script.module.addonsresolver/'
		
		#if getSetting("rotten_api") <> '': self.rotten_key = getSetting("rotten_api")
		#else: self.rotten_key = ''
		self.rotten_key = ''
		self.rotten_base = 'http://api.rottentomatoes.com/api/public/v1.0/lists/%s'
		self.rotten_boxoffice = self.rotten_base % 'movies/box_office.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_theaters = self.rotten_base % 'movies/in_theaters.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_opening = self.rotten_base % 'movies/opening.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_upcoming = self.rotten_base % 'movies/upcoming.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_dvdtop_rentals = self.rotten_base % 'dvds/top_rentals.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_dvdcurrent_releases = self.rotten_base % 'dvds/current_releases.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_dvdnew_releases = self.rotten_base % 'dvds/new_releases.json?apikey=%s&page_limit=30&page=%s'
		self.rotten_dvdupcoming = self.rotten_base % 'dvds/upcoming.json?apikey=%s&page_limit=30&page=%s'
