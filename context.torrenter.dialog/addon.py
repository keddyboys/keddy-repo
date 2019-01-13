# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 SergeSmitch
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import xbmc
import re


#def clean_label(Label):
    #Label = re.sub('\[.+?\]','', Label)
    #Label = str(Label).strip()
    #return Label

	
def main():
    if xbmc.getCondVisibility("Pvr.HasTVChannels"):
        Label = xbmc.getInfoLabel("ListItem.Title")
    else:
        Label = xbmc.getInfoLabel("ListItem.Label")

    Label, year = xbmc.getCleanMovieTitle(Label)

    url = ("plugin://plugin.video.torrenter/?action=searchWindow&mode=search&query=%s" % (Label))
    if xbmc.getCondVisibility("Container.Content(movies)"):
        xbmc.executebuiltin('xbmc.RunPlugin(%s)' % (url))
    elif xbmc.getCondVisibility("Container.Content(tvshows)"):
        xbmc.executebuiltin('xbmc.RunPlugin(%s)' % (url))
    elif xbmc.getCondVisibility("Container.Content(seasons)"):
        xbmc.executebuiltin('xbmc.RunPlugin(%s)' % (url))
    elif xbmc.getCondVisibility("Container.Content(actors) | Container.Content(directors)"):
        xbmc.executebuiltin('xbmc.RunPlugin(%s)' % (url))
    elif xbmc.getCondVisibility("Pvr.HasTVChannels"):
        xbmc.executebuiltin('xbmc.RunPlugin(%s)' % (url))

if __name__ == '__main__':
    main()	
