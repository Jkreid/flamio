# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 00:05:01 2019

@author: justi
"""

import os
import sys
sys.path.insert(1, os.path.realpath('../../..'))
import src.api.utils.flamio as flamio


def show(result,i):
    if not (type(result) is list):
        result = [result]
    display = '{}. '.format(i+1) + ' | '.join(map(str,result))
    print(display)


def track_name(username, service, song_id, users={}, path='.'):
    users = users or flamio.get_users(path)
    player = flamio.get_player(username=username, service=service, users=users, path=path)
    if service == 'spotify':
        return player.track(song_id)['name']
    elif service == 'soundcloud':
        pass
    elif service == 'apple_music':
        pass

def item(username, 
         service, 
         query,
         field,
         users={}, 
         path='.', 
         limit=10, 
         offset=0, 
         void=True):
    # get w/ input
    search_function = {'track':track, 'album':album, 'artist':artist, 'playlist':playlist}[field]
    return search_function(username, service, query, users, path, limit, offset, void)


def track(username, 
          service, 
          query, 
          users={}, 
          path='.', 
          limit=10, 
          offset=0, 
          void=True):
    # get w/ input
    """ display results of user track query and return them if void is False """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            player = flamio.get_player(username, service, users, path)
            if player:
                if service == 'spotify':
                    results = player.search(query, limit=limit, offset=offset, type='track')['tracks']['items']
                    for i,result in enumerate(results):
                        name = result['name']
                        artists = '/'.join([artist['name'] for artist in result['artists']])
                        album = result['album']['name']
                        explicit = '[explicit]' if result['explicit'] else ''
                        popularity = result['popularity']
                        identifiers = [name, artists, explicit, album, popularity]
                        show(identifiers,i)
                elif service == 'soundcloud':
                    pass
                elif service == 'apple_music':
                    pass
                if not void:
                    return results


def album(username, 
          service, 
          query, 
          users={}, 
          path='.', 
          limit=10, 
          offset=0, 
          void=True):
    # get w/ input
    """ display results of user album query and return them if void is False """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            player = flamio.get_player(username, service, users, path)
            if player:
                if service == 'spotify':
                    results = player.search(query, limit=limit, offset=offset, type='album')['albums']['items']
                    for i,result in enumerate(results):
                        name = result['name']
                        artists = '/'.join([artist['name'] for artist in result['artists']])
                        identifiers = [name, artists]
                        show(identifiers,i)
                elif service == 'soundcloud':
                    pass
                elif service == 'apple_music':
                    pass
                if not void:
                    return results


def artist(username, 
           service, 
           query, 
           users={},
           path='.', 
           limit=10, 
           offset=0, 
           void=True):
    # get w/ input
    """ display results of user artist query and return them if void is False """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            player = flamio.get_player(username, service, users, path)
            if player:
                if service == 'spotify':
                    results = player.search(query, limit=limit, offset=offset, type='artist')['artists']['items']
                    for i,result in enumerate(results):
                        name = result['name']
                        popularity = result['popularity']
                        genres = '/'.join(result['genres'])
                        identifiers = [name, popularity, genres]
                        show(identifiers,i)
                elif service == 'soundcloud':
                    pass
                elif service == 'apple_music':
                    pass
                if not void:
                    return results


def playlist(username, 
             service, 
             query, 
             users={}, 
             path='.', 
             limit=10, 
             offset=0, 
             void=True):
    # get w/ input
    """ display results of user playlist query and return them if void is False """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            player = flamio.get_player(username, service, users, path)
            if player:
                if service == 'spotify':
                    results = player.search(query, limit=limit, offset=offset, type='playlist')['playlists']['items']
                    for i,result in enumerate(results):
                        name = result['name']
                        owner = result['owner']['display_name']
                        identifiers = [name, owner]
                        show(identifiers,i)
                elif service == 'soundcloud':
                    pass
                elif service == 'apple_music':
                    pass
                if not void:
                    return results
    

def devices(username, 
            service, 
            users={}, 
            path='.', 
            void=True):
    # get w/o input
    """ display user devices and return them if void is False """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            player = flamio.get_player(username, service, users, path)
            if player:
                if service == 'spotify':
                    devices = player.devices()['devices']
                    for i,device in enumerate(devices):
                        name = device['name']
                        status = '*active' if device['is_active'] else 'inactive'
                        identifiers = [name, status]
                        show(identifiers,i)
                elif service == 'soundcloud':
                    pass
                elif service == 'apple_music':
                    pass
                if not void:
                    return devices