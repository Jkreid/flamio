# -*- coding: utf-8 -*-
"""
Created on Tue Nov  5 00:05:13 2019

@author: justi
"""


import search
import flamio


def from_saved(field,
               username=None,
               service=None,
               user={},
               name=None,
               song_id=None,
               users={},
               path='.'):
    # get w/ input
    user = user or flamio.get_user(username, service, users, path)
    if user:
        if field in ['loops','skips']:
            if song_id and (song_id in user[field]):
                if name not in user[field][song_id]:
                    results = list(user[field][song_id].keys())
                    for i,loop_name in enumerate(results):
                        search.show(loop_name,i)
                    selection = input('select {} name or number: '.format(field[:-1]))
                    try:
                        name = results[int(selection)-1]
                    except:
                        if selection in results:
                            name = selection
            else:
                if name:
                    songs = [song for song in user[field] if name in user[field][song]]
                    for i,song in enumerate(songs):
                        search.show(search.track_name(username, service, song, users, path), i)
                    selection = input('select {} number: '.format(field[:-1]))
                    song_id = songs[int(selection)-1]
                else:
                    songs = [song for song in user[field]]
                    for i,song in enumerate(songs):
                        search.show(search.track_name(username, service, song, users, path), i)
                    selection = input('select {} number: '.format(field[:-1]))
                    song_id = songs[int(selection)-1]
                    
                    results = list(user[field][song_id].keys())
                    for i,loop_name in enumerate(results):
                        search.show(loop_name,i)
                    selection = input('select {} name or number: '.format(field[:-1]))
                    try:
                        name = results[int(selection)-1]
                    except:
                        if selection in results:
                            name = selection
            return {'name':name, 'song_id':song_id, 'field':field}
        else:
            if not (name in user[field]):
                items = list(user[field].keys())
                for i,item in items:
                    search.show(item, i)
                selection = input('select {} number: '.format(field))
                name = items[int(selection)-1]
            return {'name':name, 'field':field}


def from_search(username, 
                service, 
                query, 
                users={}, 
                path='.', 
                field='track', 
                limit=10, 
                offset=0):
    # get w/ input
    """ Get item id from user query """
    results = search.item(username=username, 
                          service=service, 
                          query=query, 
                          field=field,
                          users=users, 
                          path=path, 
                          limit=limit, 
                          offset=offset,
                          void=False)
    selection = input('\nresult number, (next/back) to change result page, or quit: ')
    if results:
        try:
            selection_id = results[int(selection)-1]['id']
        except:
            if selection in ['next','back']:
                fwdOrbck = 1 if selection == 'next' else -1
                print('\n')
                selection_id = from_search(username, 
                                           service, 
                                           query, 
                                           users, 
                                           path, 
                                           field, 
                                           limit, 
                                           offset=offset+limit*fwdOrbck)
            else:
                print('\nno selection made')
                return False
        return selection_id
    else:
        if not offset:
            print('\nno results')
            return False
        else:
            return from_search(username, service, query, users, path, field, limit)


def device(username, 
           service, 
           users={}, 
           path='.', 
           asked_for_current_device=False):
    # get w/ input
    """ Get device id from user selection """
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            player = flamio.get_player(username, service, users, path)
            if player:
                if service == 'spotify':
                    if not asked_for_current_device:
                        pb = player.current_playback()
                        if pb:
                            select_current = input('use currently selected device? (y/n): ' )[0].lower() == 'y'
                            if select_current:
                                return pb['device']['id']
                            else:
                                pass
                    device_list = search.devices(username, 
                                                 service, 
                                                 users=users, 
                                                 path=path,
                                                 void=False)
                    selection = input('device name or number: ')
                    try:
                        device_id = device_list[int(selection)-1]['id']
                        return device_id
                    except:
                        try:
                            device_id = {device_list[i]['name']:device_list[i]['id'] for i in range(len(device_list))}[selection]
                            return device_id
                        except:
                            retry = input('retry? (y/n): ')[0].lower() == 'y'
                            if retry:
                                return device(username, 
                                              service, 
                                              users=users, 
                                              path=path,
                                              asked_for_current_device=True)
                            else:
                                print('did not select valid device')
                                return None




