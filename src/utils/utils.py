# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 20:50:11 2019

@author: justi

Flamio - Utility functions
"""

def select_from_search(spotify, query, field='track', limit=10, offset=0):
    """ Get item id from user query """
    search_type = {'track':search_track,
                   'album':search_album,
                   'artist':search_artist,
                   'playlist':search_playlist}
    results = search_type[field](spotify, query, limit=limit, offset=offset, void=False)
    selection = input('result number, (next/last) to change result page, or quit: ')
    if len(results) > 0:
        try:
            selection_id = results[int(selection)-1]['id']
        except:
            if selection == 'next':
                selection_id = select_from_search(spotify, query, field=field, lmit=limit, offsest=offset+limit)
            elif selection == 'back':
                if offset >= limit:
                    selection_id = select_from_search(spotify, query, field=field, limit, offsest=offset-limit)
                else:
                    selection_id = select_from_search(spotify, query, field=field, limit=limit)
            else:
                print('no selection made')
                return False
        return selection_id
    else:
        if not offset:
            print('no results')
            return False
        else:
            return select_from_search(spotify, query, field=field, limit=limit)
    

def search_track(spotify, query, limit=10, offset=0,void=True):
    """ display results of user track query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='track')['tracks']['items']
    for i,result in enumerate(results):
        name = result['name']
        artists = [artist['name'] for artist in result['artists']]
        album = result['album']['name']
        explicit = result['explicit']
        popularity = result['popularity']
        identifiers = [i+1,name, '/'.join(artists), '[explicit]' if explicit else '', album, popularity]
        print('{}. {} {} {} {} {}'.format(*identifiers)) #format nicer
    if not void:
        return results


def search_album(spotify, query, limit=10, offset=0, void=True):
    """ display results of user album query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='album')['albums']['items']
    for i,result in enumerate(results):
        name = result['name']
        artists = [artist['name'] for artist in result['artist']]
        print('{}. {} {}'.format(i+1, name, '/'.join(artists)))
    if not void:
        return results


def search_artist(spotify, query, limit=10, offset=0, void=True):
    """ display results of user artist query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='artist')['artists']['items']
    for i,result in enumerate(results):
        name = result['name']
        popularity = result['popularity']
        genres = result['genres']
        print('{}. {} {} {}'.format(i+1, name, popularity, '/'.join(genres)))
    if not void:
        return results


def search_playlist(spotify, query, limit=10, offset=0, void=True):
    """ display results of user playlist query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='playlist')['playlists']['items']
    for i,result in enumerate(results):
        name = result['name']
        owner = result['owner']['display_name']
        print('{}. {} {}'.format(i+1, name, owner))
    if not void:
        return results


def view_devices(spotify,void=True):
    """ display user devices and return them if void is False """
    devices = spotify.devices()['devices']
    for i,device in enumerate(devices):
        status = ' -- {}'.format('*active' if device['is_active'] else 'inactive')
        print('{}. {}{}'.format(i+1,device['name'],status))
    if not void:
        return devices


def select_device(spotify, selection=None, asked_for_current_device=False):
    """ Get device id from user selection """
    if not selection:
        if not asked_for_current_device:
            if spotify.current_playback:
                if input('play currently selected device? (y/n): ' )[0].lower() == 'y':
                    return spotify.current_playback()['device']['id']
                else:
                    pass
        devices = view_devices(spotify,void=False)
        selection = input('device name or number: ')
    try:
        device_id = devices[int(selection)-1]['id']
        return device_id
    except:
        try:
            device_id = {devices[i]['name']:devices[i]['id'] for i in range(len(devices))}[selection]
            return device_id
        except:
            if input('retry? (y/n): ')[0].lower() == 'y':
                return select_device(spotify,selection=None,asked_for_current_device=True)
            else:
                print('did not select valid device')
                raise ValueError
            
                