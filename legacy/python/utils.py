# -*- coding: utf-8 -*-
"""
Created on Tue Dec 31 01:06:54 2019

@author: justi
"""

from data import PATH
import flamio

def time_to_ms(time):
    """ '0:00' to miliseconds """
    minute,seconds = map(float,time.split(':'))
    return int(1000*(minute*60 + seconds))


def ms_to_time(ms):
    """ miliseconds to '0:00' """
    ms = int(ms)
    minute,seconds = int(ms/60000), round((ms/1000)%60,3)
    return ':'.join(map(str,(minute,seconds)))


def end_to_ms(username, 
              service, 
              song_id, 
              users={}, 
              path='.'):
    # get w/ input and update if token expired
    player = flamio.get_player(username, service, users, path)
    if service == 'spotify':
        end_ms = player.track(song_id)['duration_ms']
    elif service == 'soundcloud':
        end_ms = 900000
    elif service == 'apple_music':
        end_ms = 900000
    return ms_to_time(end_ms)


def end_to_time(username, 
                service, 
                song_id, 
                users, 
                path):
    return ms_to_time(end_to_ms(username, service, song_id, users, path))


def merged_intervals(cut_array): 
    m = [] 
    s = max_val = -1
    for a in sorted(cut_array, key = lambda x: x[0]):
        if a[0] > max_val: 
            if s > -1: 
                m.append((s,max_val))
            s,max_val = a
        else: 
            if a[1] >= max_val:
                _,max_val = a
    if max_val != -1 and (s, max_val) not in m: 
        m.append((s, max_val))
    return m


def make_cutzone(user, song_id, skips, cuts):
    always_cuts = [cut['times'] for cut in user['cut'][song_id].values() if cut['always']]
    always_skips = [skip['cuts'] for skip in user['skip'][song_id].values() if skip['always']]
    skip_cut_list = always_skips + [user['skip'][song_id][name]['cuts'] for name in skips]
    cuts_from_skips = [user['cut'][song_id][name]['times'] for skip in skip_cut_list for name in skip]
    cuts_from_names = [user['cut'][song_id][name]['times'] for name in cuts]
    all_cuts = set(always_cuts + cuts_from_skips + cuts_from_names)
    cuts_ms = [tuple(map(time_to_ms, cut_time.split('-'))) for cut_time in all_cuts]
    return merged_intervals(cuts_ms)