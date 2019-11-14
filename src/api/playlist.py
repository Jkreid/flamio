# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 21:07:13 2019

@author: justi

API playlist
"""

import utils.flamio as flamio
from loopify import play_loop, play_skip
from stremix import play_mix
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
    users = flamio.get_users(path,users)
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
             loop_name,
             position=None, 
             field='loops', 
             reps=1,
             users={},
             path='.'):
    # update
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                if song_id in user[field]:
                    if loop_name in user[field][song_id]:
                        playlist = user['playlists'][name]
                        loop = {'field':field, 
                                'song_id':song_id, 
                                'name':loop_name, 
                                'reps':reps}
                        position = position or len(playlist) + 1
                        playlist.insert(position-1, loop)
                        flamio.save(users,path)
  
def add_skip(username,
             service,
             song_id,
             name,
             loop_name,
             position=None, 
             reps=1,
             users={},
             path='.'):
    # update
    return add_loop(username=username,
                    service=service,
                    song_id=song_id,
                    loop_name=loop_name,
                    name=name, 
                    position=position, 
                    field='skips', 
                    reps=reps,
                    users=users,
                    path=path)

def add_stremix(username,
                service,
                name,
                stremix_name,
                position=None,
                reps=1,
                users={},
                path='.'):
    # update
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                if stremix_name in user['stremixes']:
                    playlist = user['playlists'][name]
                    mix = {'field':'stremixes', 
                            'name':stremix_name, 
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
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if num_loops >= init_position:
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
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if num_loops >= init_position:
                    paste_position = paste_position or num_loops
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
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                num_loops = len(playlist)
                if num_loops >= position:
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
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                if position >= len(playlist):
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
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                playlist = user['playlists'][name]
                play_functions = {'loops':play_loop, 
                                  'skips':play_skip,
                                  'stremixes':play_mix}
                player = flamio.get_player(username,service,users,path)
                player.repeat('context' if repeat else 'off')
                if reverse:
                    playlist = playlist.copy().reverse()
                i,j=0,0
                while i < reps | player.current_playback()['repeat_state'] == 'context':
                    for item in playlist:
                        if not i and j < offset:
                            continue
                        play_func = play_functions[item['field']]
                        continue_play = play_func(username=username, 
                                                  users=users, 
                                                  path=path, 
                                                  device=device, 
                                                  **{k:item[k] for k in item if k !='field'})
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
    users = flamio.get_users(path,users)
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
    users = flamio.get_users(path,users)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user['playlists']:
                user['playlists'][new_name] = user['playlists'].pop(name)
                flamio.save(users,path)
