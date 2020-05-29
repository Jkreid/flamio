# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 21:07:13 2019

@author: justi

API playlist
"""

import src.api.utils.flamio as flamio
import src.api as api
#==============================================================================
# Playlist Functions
#==============================================================================

### Playlist positon arguments are 1 indexed

def new(username,
        service,
        name=None,
        users={},
        path= '.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            playlists = user['playlists']
            if name not in playlists:
                if not name:
                    untitled = sorted(list(filter(lambda x: 'untitled' in x, playlists)))
                    number = int(untitled[-1].split(' ')[-1]) + 1
                    while 'untitled {}'.format(number) in untitled:
                        number += 1
                    name = 'untitled {}'.format(number)
                playlists[name] = []
                flamio.save(users,path)


def add_loop(username,
             service,
             name,
             song_id,
             loop_name='FULLSONG',
             position=None, 
             field='loops', 
             reps=1,
             users={},
             path='.',
             start=None,
             end=None):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                if song_id in user[field] or loop_name == 'FULLSONG':
                    if loop_name == 'FULLSONG' or loop_name in user[field][song_id]:
                        playlist = user['playlists'][name]
                        loop = {'field':field, 
                                'song_id':song_id, 
                                'name':loop_name, 
                                'reps':reps}
                        if field == 'loops' and loop_name == 'FULLSONG':
                            if start or end:
                                if start:
                                    loop['start'] = start
                                if end:
                                    loop['end'] = end
                            else:
                                loop['buff'] = 500
                        position = position or len(playlist) + 1
                        playlist.insert(position-1, loop)
                        flamio.save(users,path)
  
def add_skip(username,
             service,
             name,
             song_id,
             loop_name='FULLSONG',
             position=None, 
             reps=1,
             users={},
             path='.',
             start=None,
             end=None):
    # update
    return add_loop(username=username,
                    service=service,
                    name=name,
                    song_id=song_id,
                    loop_name=loop_name,
                    position=position, 
                    field='skips', 
                    reps=reps,
                    users=users,
                    path=path,
                    start=start,
                    end=end)

def add_mix(username,
                service,
                name,
                mix_name,
                field='playlists',
                position=None,
                reps=1,
                users={},
                path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                if mix_name in user[field]:
                    playlist = user[field][name]
                    mix = {'field':field, 
                            'name':mix_name, 
                            'reps':reps}
                    position = position or len(playlist) + 1
                    playlist.insert(position-1, mix)
                    flamio.save(users,path)

def move_item(username,
              service,
              name, 
              init_position, 
              new_position=0,
              users={},
              path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if init_position and -num_loops <= init_position <= num_loops:
                    new_position = new_position or num_loops
                    playlist.insert(new_position-1, playlist.pop(init_position-1))
                    flamio.save(users,path)


def duplicate_item(username,
                   service,
                   name, 
                   init_position, 
                   paste_position=None, 
                   reps=None,
                   users={},
                   path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if init_position and -num_loops <= init_position <= num_loops:
                    paste_position = paste_position or num_loops+1
                    playlist.insert(paste_position-1, playlist[init_position-1])
                    if reps:
                        change_reps(username, 
                                    service, 
                                    name, 
                                    min(paste_position,len(playlist)), 
                                    reps, 
                                    users, 
                                    path)
                    flamio.save(users,path)


def delete_item(username, 
                service,
                name, 
                position=0,
                users={},
                path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if position and -num_loops <= position <= num_loops:
                    playlist.pop(position-1)
                    flamio.save(users,path)
    

def change_reps(username,
                service,
                name,
                position=0,
                reps=1,
                users={},
                path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if position and -num_loops <= position <= num_loops:
                    playlist[position-1]['reps'] = reps
                    flamio.save(users,path)


def play(username,
         service,
         name, 
         reps=1,
         repeat=False, 
         device=None, 
         offset=0, 
         reverse=False,
         users={},
         path='.'):
    # play
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                player = flamio.get_player(username,service,users,path)
                player.repeat('context' if repeat else 'off')
                if reverse:
                    playlist = playlist.copy().reverse()
                i,j=0,0
                print('playing playlist: {}'.format(name))
                while (i < reps) or (player.current_playback()['repeat_state'] == 'context'):
                    for item in playlist:
                        if not i and j < offset:
                            continue
                        continue_play = api.play(username=username,
                                                 service=service,
                                                 users=users,
                                                 path=path,
                                                 device=device,
                                                 **item)
                        player = flamio.get_player(username,service,users,path)
                        if not continue_play:
                            break
                    if player.current_playback()['repeat_state'] == 'off' or not continue_play:
                        break


def view(name,
         user={},
         username=None, 
         service=None,
         users={},
         path='.'):
    # get w/ input
    user = user or flamio.get_user(username, service, users, path)
    if name in user['playlists']:
        playlist = user['playlists'][name]
        for i,item in enumerate(playlist):
            info = ', '.join(['{}: {}'.format(context, value) for context,value in item.items()])
            print('{}. {}'.format(i+1,info))


def delete_playlist(username,
                    service,
                    name,
                    users={},
                    path='.'):
    # delete
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                del user['playlists'][name]
                flamio.save(users,path)


def rename(username,
           service,
           name,
           new_name,
           users={},
           path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                user['playlists'][new_name] = user['playlists'].pop(name)
                # rename in playlists
                for playlist in user['playlists'].values():
                    for item in playlist:
                        if item['field'] == 'playlists':
                            if item['name'] == name:
                                item['name'] = new_name
                flamio.save(users,path)
