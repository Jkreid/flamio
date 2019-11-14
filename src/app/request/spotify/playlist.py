# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 23:48:04 2019

@author: justi
"""

import utils
import loopify
#==============================================================================
# Playlist
#==============================================================================
### Playlist positon arguments are 1 indexed

def make_playlist(user, name=None):
    name = name or '[Untitled_{}]'.format(len(user.data['playlists']))
    user.data['playlists'][name] = []
    user.save_data()


def add_to_playlist(user, 
                    playlist_name=None, 
                    position=None, 
                    element_field='loops', 
                    song_id=None, 
                    song_name=None, 
                    reps=1):
    # add element to playlist
    # default position is the last
    # make playlist with given name if non existant
    if playlist_name not in user.data['playlists'].keys():
        newPlaylist = input('playlist not in stored, make a new one? (y/n): ')[0].lower() == 'y'
        if newPlaylist:
            user.data['playlists'][playlist_name] = []
        
    song_id, song_name, _ = utils.select_element(user,song_id, song_name, element_field)
    if not (song_id and song_name):
        return
    element = {'element_field':element_field, 'song_id':song_id, 'song_name':song_name, 'reps':reps}
    num_elements = len(user.data['playlists'][playlist_name])
    position = position or num_elements+1
    user.data['playlists'][playlist_name].insert(position-1, element)
  

def move_in_playlist(user, 
                     playlist_name=None, 
                     init_position=0, 
                     new_position=0):
    # move loop/skip in playlist
    playlist_name = utils.select_element(playlist_name=playlist_name)
    if not (playlist_name and new_position):
        return
    num_elements = len(user.data['playlists'][playlist_name])
    new_position = new_position or num_elements
    if num_elements >= max(init_position, new_position, 1):
        user.data['playlists'][playlist_name].insert(new_position-1, user.data['playlists'][playlist_name].pop(init_position-1))


def copy_in_playlist(user, 
                     playlist_name=None, 
                     init_position=0, 
                     paste_position='last', 
                     reps=None):
    # copy a loop from given position and place a copy in a given new location
    # if reps, use new reps number, else use the rep number from the copied loop
    playlist_name = utils.select_element(playlist_name=playlist_name)
    if not (playlist_name and paste_position):
        return
    num_elements = len(user.data['playlists'][playlist_name])
    paste_position = paste_position or num_elements+1
    if num_elements >= max(init_position, paste_position, 1):
        user.data['playlists'][playlist_name].insert(paste_position-1, user.data['playlists'][playlist_name][init_position-1])
        if reps:
            change_reps(user, playlist_name=playlist_name, position=paste_position, reps=reps)


def delete_from_playlist(user, playlist_name=None, position=0):
    # delete loop/skip from playlist
    #default position to delete is the last
    playlist_name = utils.select_element(playlist_name=playlist_name)
    if not playlist_name:
        return
    num_elements = len(user.data['playlists'][playlist_name])
    if num_elements:
        if num_elements >= position:
            user.data['playlists'][playlist_name].pop(position-1)
    

def change_reps(user,
                playlist_name=None,
                position=0,
                reps=1):
    # change rep number of loop/skip in playlist
    playlist_name = utils.select_element(playlist_name=playlist_name)
    if not playlist_name:
        return
    if user.data['playlists'][playlist_name]:
        user.data['playlists'][playlist_name][position-1]['reps'] = reps


def play_playlist(user, 
                  playlist_name=None, 
                  reps=1, 
                  repeat=False, 
                  device=None, 
                  offset=0, 
                  reverse=False):
    # play entire playlist
    playlist_name = utils.select_element(playlist_name=playlist_name)
    if not playlist_name:
        return
    device = device or utils.select_device(user.sp())
    repeat = 'context' if repeat else 'off'
    user.sp().repeat(repeat)
    playlist_elements = user.data['playlists'][playlist_name].copy()
    if reverse:
        playlist_elements.reverse()
    i,j=0,0
    while i < reps | user.sp().current_playback()['repeat_state'] == 'context':
        for element in playlist_elements:
            if not i and j < offset:
                continue
            continue_play = loopify.play(user,
                                         song_id=element['song_id'],
                                         name=element['song_name'],
                                         device=device,
                                         reps=element['reps'],
                                         element_field=element['element_field'])
            if not continue_play:
                break
        if user.sp().current_playback()['repeat_state'] == 'off' or not continue_play:
            break


def view_playlist(user, playlist_name=None):
    playlist_name = utils.select_element(playlist_name=playlist_name)
    if not playlist_name:
        return
    for i,element in enumerate(user.data['playlists'][playlist_name]):
        info = ', '.join(['{}: {}'.format(context, value) for context,value in element.items()])
        print('{}. {}'.format(i+1,info))
  
  
create = make_playlist
add = add_to_playlist
move = move_in_playlist  
duplicate = copy_in_playlist
remove = delete_from_playlist
play = play_playlist
view = view_playlist