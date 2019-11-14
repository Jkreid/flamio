# -*- coding: utf-8 -*-
"""
Created on Tue Oct  1 20:50:11 2019

@author: justi

Flamio - Utility functions
"""

def username(spotify):
    """ Get user's username """
    return spotify.me()['id']


def select_element(user, 
                   song_id=None, 
                   name=None, 
                   element_field=None):
    """ select element of loop or skip if one exist, from a song id and name """
    if element_field == 'playlists':
        if name not in user.data['playlist'].keys():
            for i,playlist in enumerate(user.data['playlists'].keys()):
                print('{}. {}'.format(i+1, playlist))
            selection = input('playlist number or name')
            try:
                name = user.data['playlists'].keys()[int(selection)-1]
            except:
                if selection in user.data['playlists'].keys():
                    name = selection
                else:
                    name = None
        return name
    else:
        if song_id not in user.data[element_field].keys():
            tracks = user.sp().tracks(user.data[element_field].keys())['tracks']
            for i,track in enumerate(tracks):
                stored_name = track['name']
                stored_artist = '/'.join([artist['name'] for artist in track['artists']])
                explicit = ' | [explicit]' if track['explicit'] else ''
                print('{}. {} | {}{}'.format(i+1,stored_name,stored_artist,explicit))
            try:
                selection = int(input('song number: ')) - 1
                song_id = list(user.data[element_field].keys())[selection]
            except:
                song_id = None
        if song_id:
            if name == 'FULLSONG' and element_field == 'loops':
                pass
            elif name not in user.data[element_field][song_id].keys():
                for i,stored_name in enumerate(user.data[element_field][song_id].keys()):
                    print('{}. {}'.format(i+1,stored_name))
                try:
                    selection = int(input('name number: ')) - 1
                    name =  list(user.data[element_field][song_id].keys())[selection]
                except:
                    name = None
        if (not song_id and name):
            song = user.sp().track(song_id)['name'] if song_id else '[NONE]'
            print('no element found in {} for song: {} with name: {}'.format(element_field,song,name))
        return song_id, name


def select_from_search(spotify, query=' ', field='track', limit=10, offset=0):
    """ Get item id from user query """
    search_type = {'track':search_track,
                   'album':search_album,
                   'artist':search_artist,
                   'playlist':search_playlist}
    results = search_type[field](spotify, query=query, limit=limit, offset=offset, void=False)
    selection = input('\nresult number, (next/back) to change result page, or quit: ')
    if len(results) > 0:
        try:
            selection_id = results[int(selection)-1]['id']
        except:
            if selection == 'next':
                print('\n')
                selection_id = select_from_search(spotify, query=query, field=field, limit=limit, offset=offset+limit)
            elif selection == 'back':
                print('\n')
                if offset >= limit:
                    selection_id = select_from_search(spotify, query=query, field=field, limit=limit, offset=offset-limit)
                else:
                    selection_id = select_from_search(spotify, query=query, field=field, limit=limit)
            else:
                print('\n')
                print('no selection made')
                return False
        return selection_id
    else:
        if not offset:
            print('\n')
            print('no results')
            return False
        else:
            return select_from_search(spotify, query=query, field=field, limit=limit)
    

def search_track(spotify, query=' ', limit=10, offset=0,void=True):
    """ display results of user track query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='track')['tracks']['items']
    for i,result in enumerate(results):
        name = result['name']
        artists = [artist['name'] for artist in result['artists']]
        album = result['album']['name']
        explicit = result['explicit']
        popularity = result['popularity']
        identifiers = [i+1,name, '/'.join(artists), '[explicit]' if explicit else '', album, popularity]
        print('{}. {} | {} | {} | {} | {}'.format(*identifiers)) #format nicer
    if not void:
        return results


def search_album(spotify, query=' ', limit=10, offset=0, void=True):
    """ display results of user album query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='album')['albums']['items']
    for i,result in enumerate(results):
        name = result['name']
        artists = [artist['name'] for artist in result['artists']]
        print('{}. {} | {}'.format(i+1, name, '/'.join(artists)))
    if not void:
        return results


def search_artist(spotify, query=' ', limit=10, offset=0, void=True):
    """ display results of user artist query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='artist')['artists']['items']
    for i,result in enumerate(results):
        name = result['name']
        popularity = result['popularity']
        genres = result['genres']
        print('{}. {} | {} | {}'.format(i+1, name, popularity, '/'.join(genres)))
    if not void:
        return results


def search_playlist(spotify, query=' ', limit=10, offset=0, void=True):
    """ display results of user playlist query and return them if void is False """
    results = spotify.search(query, limit=limit, offset=offset, type='playlist')['playlists']['items']
    for i,result in enumerate(results):
        name = result['name']
        owner = result['owner']['display_name']
        print('{}. {} | {}'.format(i+1, name, owner))
    if not void:
        return results


def view_devices(spotify, void=True):
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
            pb = spotify.current_playback()
            if pb:
                select_current = input('use currently selected device? (y/n): ' )[0].lower() == 'y'
                if select_current:
                    return pb['device']['id']
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
            retry = input('retry? (y/n): ')[0].lower() == 'y'
            if retry:
                return select_device(spotify,selection=None,asked_for_current_device=True)
            else:
                print('did not select valid device')
                return None
            