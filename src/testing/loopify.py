# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 12:25:05 2019

@author: justi

Flamio - Loopify
"""

import os
import utils
#import time as t
import pandas as pd

#==============================================================================
# Loops & Skips
#==============================================================================

def time_to_ms(time):
    if type(time) is int:
        return time
    minute,seconds = map(float,time.split(':'))
    return int(1000*(minute*60 + seconds))


def ms_to_time(ms):
    ms = int(ms)
    minute,seconds = int(ms/60000), round((ms/1000)%60,3)
    return ':'.join(map(str,(minute,seconds)))


def load_data(spotify, include=True, data=None):
    un = utils.username(spotify)
    action = 'loops' if include else 'skips'
    data_path = '../data/{}/{}.xlsx'.format(action, un)
    if data:
        return data, data_path
    elif os.path.exists(data_path):
        return pd.read_excel(data_path), data_path
    else:
        print('no stored {}'.format(action))
        return None,None
    
    
def select_stored(spotify, data, field, field_id=None):
    if field == 'song' and field_id in data.index:
        return field_id
    elif field == 'name' and field_id in data.columns:
        return field_id
    else:
        console_prompt = '{} not in stored {}s. select from stored? (y/n) '.format(field,field)
        select_from_stored = input(console_prompt).lower()[0] == 'y'
        if select_from_stored:
            
            if field == 'name':
                for i,stored_name in enumerate(data.columns):
                    print('{}. {}'.format(i+1,stored_name))
            
            elif field == 'song':
                tracks = spotify.tracks(data.index)['tracks']
                for i,track in enumerate(tracks):
                    stored_name = track['name']
                    stored_artist = '/'.join([artist['name'] for artist in track['artists']])
                    explicit = ' | [explicit]' if track['explicit'] else ''
                    print('{}. {} | {}{}'.format(i+1,stored_name,stored_artist,explicit))
            
            selection = input('option number: ')
            try:
                if field == 'name':
                    return data.columns[int(selection)-1]
                elif field == 'song':
                    return data.index[int(selection)-1]
                else:
                    return
            except:
                print('no selection made')
                return
        else:
            print('no selection made')
            return


def add(spotify, start=None, end=None, song_id=None, include=True, name=None):
    un = utils.username(spotify)
    action = 'loops' if include else 'skips'
    data_path = '../data/{}/{}.xlsx'.format(action, un)
    song_id = song_id or utils.select_from_search(spotify, 
                                                  query=(input('enter song for search: ')))
    start = start if start else '0:00'
    end = end if end else ms_to_time(spotify.track(song_id)['duration_ms'])
    time_range = '{}-{}'.format(start,end)
    name = name or time_range
    if os.path.exists(data_path):
        data = pd.read_excel(data_path)
    else:
        data = pd.DataFrame()
    data.loc[song_id,name] = time_range
    data.to_excel(data_path)


def edit(spotify, name=None, new_start=None, new_end=None, song_id=None, include=True, data=None):
    if new_start or new_end:
        data,data_path = load_data(spotify, include, data)
        if type(data) is None:
            return
        name = select_stored(spotify, data, 'name', name)
        if not name:
            return
        song_id = select_stored(spotify, data, 'song', song_id)
        print(song_id)
        if not song_id:
            return
        old_start,old_end = data.loc[song_id,name].split('-')
        start = new_start or old_start
        end = new_end or old_end
        data.loc[song_id,name] = '{}-{}'.format(start,end)
        data.to_excel(data_path)
        

def view(spotify, song_id=None, name=None, include=True, data=None):
    data = load_data(spotify, include, data)[0]
    if not (name or song_id):
        print(data)
    elif not name:
        print(data.loc[song_id,:])
    elif not song_id:
        print(data.loc[:,name])
    else:
        print(data.loc[song_id,name])


def play(spotify, song_id=None, name=None, device=None, reps=1, persist=True, include=True, data=None):
    data,_ = load_data(spotify, include, data)
    if type(data) is None:
        return
    name = select_stored(spotify, data, 'name', name)
    if not name:
        return
    filtered_data = data.loc[:,name][data.loc[:,name].notnull()]
    if len(filtered_data) == 1:
        song_id = filtered_data.index[0]
    song_id = select_stored(spotify, filtered_data, 'song', song_id)
    if not song_id:
        return
    times = data.loc[song_id,name].split('-')
    start_ms,end_ms = map(time_to_ms, times)
    device = device or utils.select_device(spotify)
    uri = ['https://open.spotify.com/track/'+song_id]
        
    def inLoop(playback, t1, t2, include):
        if playback:
            return (t1 <= playback['progress_ms'] < t2) == include
        
    def validPlayback(spotify, t1, t2, song_id, persist, include):
        playback = spotify.current_playback()
        if playback:
            if playback['item']['id'] == song_id:
                if playback['is_playing'] or (persist and inLoop(playback,t1,t2,include)):
                    return playback
                    
    playback = spotify.current_playback()
    if playback:
        if (not playback['is_playing']) or (playback['item']['id'] != song_id):
            spotify.start_playback(device_id=device, uris=uri)
        spotify.repeat(playback['repeat_state'])
    else:
        spotify.start_playback(device_id=device, uris=uri)
        playback = spotify.current_playback()

    i=0
    while playback and (i < reps or playback['repeat_state'] == 'track'):
        if not inLoop(spotify.current_playback(), start_ms, end_ms, include):
            spotify.seek_track(start_ms if include else end_ms)
        while inLoop(spotify.current_playback(), start_ms, end_ms, include):
            playback = validPlayback(spotify, start_ms, end_ms, song_id, persist, include)
            if not playback:
                break
        i+=1
        
    if spotify.current_playback()['is_playing']:
        spotify.pause_playback()


#==============================================================================
# Mixes
#==============================================================================

class Mix:
    
    def __init__(self):
        pass
    
    def all_the_mix_methods():
        pass