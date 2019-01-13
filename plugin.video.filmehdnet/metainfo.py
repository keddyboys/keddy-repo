# -*- coding: utf-8 -*-
import json
import os
import sys
import urllib
import xbmc
import xbmcaddon
import xbmcgui

__addon__ = xbmcaddon.Addon()
__scriptid__   = __addon__.getAddonInfo('id')
__scriptname__ = __addon__.getAddonInfo('name')

__cwd__        = xbmc.translatePath(__addon__.getAddonInfo('path')).decode("utf-8")
__profile__    = xbmc.translatePath(__addon__.getAddonInfo('profile')).decode("utf-8")
__resource__   = xbmc.translatePath(os.path.join(__cwd__, 'resources', 'lib')).decode("utf-8")
__temp__       = xbmc.translatePath(os.path.join(__profile__, 'temp', '')).decode("utf-8")

sys.path.append (__resource__)

import requests

class window(xbmcgui.WindowDialog):

    def get_n(self, name, name2):
        #from metahandler import metahandlers
        #mg = metahandlers.MetaData()
        nume, an = xbmc.getCleanMovieTitle(name)
        #nume = nume.replace(" ", "+")
        nume = nume.replace('ț', 't').replace('ă', 'a')
        nume = urllib.quote_plus(nume)
        info_url = 'http://www.omdbapi.com/?t=%s&y=%s&plot=full&r=json' % (nume, an)
        met = self.get_data(info_url)
        meta = json.loads(met)
        data  = ['Poster', 'Title', 'Plot', 'Genre', 'imdbRating', 'Year', 'Director', 'Writer', 'Actors', 'Country', 'Language']
        if ('Error' in meta) and not (name2 == ' filme online'):
            nume, an = xbmc.getCleanMovieTitle(name2)
            nume = urllib.quote_plus(nume)
            info_url = 'http://www.omdbapi.com/?t=%s&y=%s&plot=full&r=json' % (nume, an)
            met = self.get_data(info_url)
            meta = json.loads(met)
            
        for dat in data:
            if not dat in meta:
                meta[dat] = 'Not Found'
        fundal = os.path.join(__cwd__, 'resources', 'media', 'ContentPanel.png')
        self.background = xbmcgui.ControlImage(180, 0, 1120, 720, fundal)
        self.addControl(self.background)
        
        self.fanart = xbmcgui.ControlImage(200, 100, 270, 380, meta['Poster'], aspectRatio=2)
        self.addControl(self.fanart)
        
        #self.glassoverlay = xbmcgui.ControlImage(204, 104, 200, 230, 'GlassOverlay.png', aspectRatio=2)
        #self.addControl(self.glassoverlay)
        
        self.title = xbmcgui.ControlLabel(500, 40, 1030, 30, ('Titlu: %s' % meta['Title']))
        self.addControl(self.title)
        
        self.title = xbmcgui.ControlTextBox(210, 527, 1030, 120)
        self.addControl(self.title)
        self.title.setText('Plot: %s' % meta['Plot'])
       
        self.list = xbmcgui.ControlList (500, 90, 740, 390)
        self.addControl(self.list)
        
        self.list.addItem ("genre: %s" % meta['Genre'])
        self.list.addItem ("rating: %s" % meta['imdbRating'])
        self.list.addItem ("year: %s" % meta['Year'])
        self.list.addItem ("director: %s" % meta['Director'])
        self.list.addItem ("writer: %s" % meta['Writer'])
        self.list.addItem ("cast: %s" % meta['Actors'])
        self.list.addItem ("country: %s" % meta['Country'])
        self.list.addItem ("language: %s" % meta['Language'])
        
    def get_data(self, url):
        s = requests.Session()
        ua = 'Mozilla/5.0 (Windows NT 6.2; Win64; x64; rv:16.0.1) Gecko/20121011 Firefox/16.0.1'
        headers = {'User-Agent': ua}
        j = s.get(url, headers=headers)
        lik = json.dumps(j.json())
        return lik
        
