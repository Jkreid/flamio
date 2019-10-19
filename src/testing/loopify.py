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
    """ select element of loop or skip if one exist, from a song id and name """
    
    action = 'loops' if include else 'skips'
    if song_id not in user.data[action].keys():
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
    if song_id:
        if name not in user.data[action][song_id].keys():
            for i,stored_name in enumerate(user.data[action][song_id].keys()):
                print('{}. {}'.format(i+1,stored_name))
            try:
                selection = int(input('name number: ')) - 1
                name =  list(user.data[action][song_id].keys())[selection]
            except:
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
         include=True,
         repeat=False):
    """ play existing loop or skip """
    
    def inLoop(playback, t1, t2, include):
        if playback:
            return (t1 <= playback['progress_ms'] < t2) == include
        
    def validPlayback(spotify, t1, t2, song_id, persist, include):
        playback = spotify.current_playback()
        if playback:
            if playback['item']:
                if playback['item']['id'] == song_id:
                    if playback['is_playing'] or (persist and inLoop(playback,
                                                                     t1,t2,
                                                                     include)):
                        return playback
    
    song_id,name,action = select_element(user, song_id, name, include)
    if not (song_id and name):
        return
    times = user.data[action][song_id][name].split('-')
    start_ms,end_ms = map(time_to_ms, times)
    device = device or utils.select_device(user.sp())
    uri = ['https://open.spotify.com/track/'+song_id]
    print('playing: {} - {}'.format(name,user.sp().track(song_id)['name']))                
    pb = user.sp().current_playback()
    if pb:
        repeat = 'track' if repeat else pb['repeat_state']
        if (not pb['is_playing']) or (pb['item']['id'] != song_id):
            user.sp().start_playback(device_id=device, uris=uri)
    else:
        user.sp().start_playback(device_id=device, uris=uri)
        pb = user.sp().current_playback()
        repeat = 'track' if repeat else pb['repeat_state']
    user.sp().repeat(repeat)
    
    i=0
    while pb and (i < reps or pb['repeat_state'] == 'track'):
        if not inLoop(user.sp().current_playback(), start_ms, end_ms, include):
            user.sp().seek_track(start_ms if include else end_ms)
        while inLoop(user.sp().current_playback(), start_ms, end_ms, include):
            if not validPlayback(user.sp(), 
                                     start_ms, 
                                     end_ms, 
                                     song_id, 
                                     user.persist_through_pause, 
                                     include): break
        pb = validPlayback(user.sp(), 
                           start_ms, 
                           end_ms, 
                           song_id, 
                           user.persist_through_pause, 
                           include)
        i+=1
    
    pb = user.sp().current_playback()
    if pb:
        if pb['is_playing']:
            if pb['item']:
                if pb['item']['id'] == song_id:
                    user.sp().pause_playback()


#==============================================================================
# Mixes
#==============================================================================

class Mix:
    
    def __init__(self,user,name=None):
        self.name=name
        
    
    def all_the_mix_methods():
        pass