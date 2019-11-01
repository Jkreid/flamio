# -*- coding: utf-8 -*-
"""
Created on Sat Oct  5 12:25:05 2019

@author: justi

Flamio - Loopify
"""

import utils
import time as t

#==============================================================================
# Loop & Skip Functions
#==============================================================================
#make loopify just the playing function that can play anything pretty much
#put loops and skips in seperate module
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


def add(user, 
        start=None, 
        end=None, 
        song_id=None, 
        name=None, 
        element_field='loops'):
    """ add loop or skip to saved options """
    if not song_id:
        query=input('enter song for search: ')
        song_id = utils.select_from_search(user.sp(), query=query)
    start = start if start else '0:00'
    end = end if end else ms_to_time(user.sp().track(song_id)['duration_ms'])
    time_range = '{}-{}'.format(start,end)
    name = name or time_range
    if song_id not in user.data[element_field].keys():
        user.data['loops'][song_id] = {}
        user.data['skips'][song_id] = {}
    user.data[element_field][song_id][name] = time_range
    user.save_data()


def edit(user,
         song_id=None, 
         name=None, 
         new_start=None, 
         new_end=None, 
         element_field='loops'):
    """ edit existing loop or skip """
    if new_start or new_end:
        song_id,name = utils.select_element(user, song_id, name, element_field)
        if not (song_id and name):
            return
        old_start,old_end = user.data[element_field][song_id][name].split('-')
        start = new_start or old_start
        end = new_end or old_end
        user.data[element_field][song_id][name] = '{}-{}'.format(start,end)
        user.save_data()
        

def view(user, 
         song_id=None, 
         name=None, 
         element_field='loops'):
    """ view stored loops or skips, filtered by song and name """
    if element_field=='loops' or element_field=='skips':
        song_id,name = utils.select_element(user, song_id, name, element_field)
        if song_id not in user.data[element_field].keys():
            print(user.data[element_field])
        elif name not in user.data[element_field][song_id].keys():
            print(user.data[element_field][song_id])
        else:
            print(user.data[element_field][song_id][name])


def play(user, 
         song_id=None, 
         name='FULLSONG', 
         device=None, 
         reps=1,  
         element_field='loops',
         repeat=False,
         checks=0):
    """ play existing loop or skip """
    include = element_field=='loops'
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
    
    song_id,name = utils.select_element(user, song_id, name, element_field)
    if not song_id:
        return
    if name == 'FULLSONG':
        start_ms, end_ms = 0, user.sp().track(song_id)['duration_ms']
    else:
        times = user.data[element_field][song_id][name].split('-')
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
# =============================================================================
#          this is the where checks gets turned into how many times (spaced at interger intervals) the interval playback is checked
#          t.sleep(gap)
# =============================================================================
            if not validPlayback(user.sp(), 
                                     start_ms, 
                                     end_ms, 
                                     song_id, 
                                     user.persist_through_pause, 
                                     include):
              break
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
                    return True


def add_skip(user, 
             start=None, 
             end=None, 
             song_id=None, 
             name=None): 
    """ add skips only """
    return add(user, 
               start=start, 
               end=end, 
               song_id=song_id, 
               name=name, 
               element_field='skips')

def edit_skip(user, 
              song_id=None, 
              name=None, 
              new_start=None, 
              new_end=None):
    """ edit skips only """
    return edit(user, 
                song_id=song_id, 
                name=name, 
                new_start=new_start, 
                new_end=new_end, 
                element_field='skips')

def view_skips(user, 
               song_id=None, 
               name=None):
    """ view skips only """
    return view(user, 
                song_id=song_id, 
                name=name, 
                element_field='skips')
  
def play_skip(user, 
              song_id=None, 
              name=None, 
              device=None, 
              reps=1,  
              repeat=False):
    """ play skips only """
    return play(user, 
                song_id=song_id, 
                name=name, 
                device=device, 
                reps=1,  
                element_field='skips',
                repeat=repeat)


skip = add_skip
add_loop = loop = add
edit_loop = edit
view_loops = view
play_loop = play
