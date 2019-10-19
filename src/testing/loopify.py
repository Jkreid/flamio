# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 12:25:05 2019

@author: justi

Flamio - Loopify
"""

import utils
#import time as t

#==============================================================================
# Loops & Skips
#==============================================================================

def time_to_ms(time):
    """ '0:00' to milisecond """
    if type(time) is int:
        return time
    minute,seconds = map(float,time.split(':'))
    return int(1000*(minute*60 + seconds))


def ms_to_time(ms):
    """ milisecond to '0:00' """
    ms = int(ms)
    minute,seconds = int(ms/60000), round((ms/1000)%60,3)
    return ':'.join(map(str,(minute,seconds)))

    
def select_element(user, 
                   song_id, 
                   name, 
                   include):
    # make function to take in these objects and based on them and user data, return 
    action = 'loops' if include else 'skips'
    if song_id not in user.data[action].keys():
        select_from_stored=input('song not found in stored songs,\
                                 select from stored songs? (y/n) ')[0].lower()=='y'
        if select_from_stored:
            tracks = user.sp().tracks(user.data[action].keys())['tracks']
            for i,track in enumerate(tracks):
                stored_name = track['name']
                stored_artist = '/'.join([artist['name'] for artist in track['artists']])
                explicit = ' | [explicit]' if track['explicit'] else ''
                print('{}. {} | {}{}'.format(i+1,stored_name,stored_artist,explicit))
            try:
                selection = int(input('song number: ')) - 1
                song_id = list(user.data[action].keys())[selection]
            except:
                song_id = None
        else:
            song_id = None
    if song_id:
        if name not in user.data[action][song_id].keys():
            select_from_stored=input('name not found in stored names for the selected song,\
                                     select from stored songs? (y/n) ')[0].lower()=='y'
            if select_from_stored:
                for i,stored_name in enumerate(user.data[action][song_id].keys()):
                    print('{}. {}'.format(i+1,stored_name))
                try:
                    selection = int(input('name number: ')) - 1
                    name =  list(user.data[action][song_id].keys())[selection]
                except:
                    name = None
            else:
                name = None
    if (not song_id and name):
        song = user.sp().track(song_id)['name'] if song_id else '[NONE]'
        print('no element found in {} for song: {} with name: {}'.format(action,song,name))
    return song_id, name, action


def add(user, 
        start=None, 
        end=None, 
        song_id=None, 
        name=None, 
        include=True):
    """ add loop or skip to saved options """
    if not song_id:
        query=input('enter song for search: ')
        song_id = utils.select_from_search(user.sp(), query=query)
    action = 'loops' if include else 'skips'
    start = start if start else '0:00'
    end = end if end else ms_to_time(user.sp().track(song_id)['duration_ms'])
    time_range = '{}-{}'.format(start,end)
    name = name or time_range
    if song_id not in user.data[action].keys():
        user.data[action][song_id] = {}
    user.data[action][song_id][name] = time_range
    user.save_data()


def edit(user, 
         song_id=None, 
         name=None, 
         new_start=None, 
         new_end=None, 
         include=True):
    """ edit existing loop or skip """
    if new_start or new_end:
        song_id,name,action = select_element(user, song_id, name, include)
        if not (song_id and name):
            return
        old_start,old_end = user.data[action][song_id][name].split('-')
        start = new_start or old_start
        end = new_end or old_end
        user.data[action][song_id][name] = '{}-{}'.format(start,end)
        user.save_data()
        

def view(user, 
         song_id=None, 
         name=None, 
         include=True):
    """ view stored loops or skips, filtered by song and name """
    song_id,name,action = select_element(user, song_id, name, include)
    if song_id not in user.data[action].keys():
        print(user.data[action])
    elif name not in user.data[action][song_id].keys():
        print(user.data[action][song_id])
    else:
        print(user.data[action][song_id][name])


def play(user, 
         song_id=None, 
         name=None, 
         device=None, 
         reps=1, 
         persist=True, 
         include=True):
    """ play existing loop or skip """
    song_id,name,action = select_element(user, song_id, name, include)
    if not (song_id and name):
        return
    times = user.data[action][song_id][name].split('-')
    start_ms,end_ms = map(time_to_ms, times)
    device = device or utils.select_device(user.sp())
    uri = ['https://open.spotify.com/track/'+song_id]
        
    def inLoop(playback, t1, t2, include):
        if playback:
            return (t1 <= playback['progress_ms'] < t2) == include
        
    def validPlayback(spotify, t1, t2, song_id, persist, include):
        playback = spotify.current_playback()
        if playback:
            if playback['item']['id'] == song_id:
                if playback['is_playing'] or (persist and inLoop(playback,
                                                                 t1,t2,
                                                                 include)):
                    return playback
    
    print('playing {} - {}'.format(name,user.sp().track(song_id)['name']))                
    playback = user.sp().current_playback()
    if playback:
        if (not playback['is_playing']) or (playback['item']['id'] != song_id):
            user.sp().start_playback(device_id=device, uris=uri)
        user.sp().repeat(playback['repeat_state'])
    else:
        user.sp().start_playback(device_id=device, uris=uri)
        playback = user.sp().current_playback()

    i=0
    while playback and (i < reps or playback['repeat_state'] == 'track'):
        if not inLoop(user.sp().current_playback(), start_ms, end_ms, include):
            user.sp().seek_track(start_ms if include else end_ms)
        while inLoop(user.sp().current_playback(), start_ms, end_ms, include):
            playback = validPlayback(user.sp(), 
                                     start_ms, 
                                     end_ms, 
                                     song_id, 
                                     persist, 
                                     include)
            if not playback:
                break
        i+=1
        
    if user.sp().current_playback()['is_playing']:
        user.sp().pause_playback()


#==============================================================================
# Mixes
#==============================================================================

class Mix:
    
    def __init__(self):
        pass
    
    def all_the_mix_methods():
        pass