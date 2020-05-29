# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 17:18:52 2019

@author: justi

API loopify
"""
import src.api.flamio as flamio
import src.api.utils.search as search
import time as t

# =============================================================================
# Loop and Skip Functions
# =============================================================================

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
            max_val = a[1] 
            s = a[0] 
        else: 
            if a[1] >= max_val:
                max_val = a[1] 
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


def new(username,
        service,
        field,
        song_id,
        name=None,
        start='0:00',
        end=None,
        always_avoid=False,
        users={},
        path='.'):
    # update
    """ add loop or skip to saved options """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if (start != '0:00') or end or (field != 'skip'):
                end = end or end_to_time(username, service, song_id, users, path)
                time_range = '-'.join([start,end])
                name = name or time_range
                if song_id not in user[field]:
                    user[field][song_id] = {}
                user[field][song_id][name] = time_range
                flamio.save(users,path)


def delete(username,
           service,
           song_id,
           name,
           field='loop',
           users={},
           path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if song_id in user[field]:
                if name in user[field][song_id]:
                    del user[field][song_id][name]
                    flamio.save(users,path)


def edit(username,
         service,
         song_id, 
         name, 
         new_start=None, 
         new_end=None, 
         field='loop',
         users={},
         path='.'):
    # update
    """ edit existing loop or skip """
    if new_start or new_end:
        users = users or flamio.get_users(path)
        if username in users:
            if service in users[username]:
                user = users[username][service]
                if song_id in user[field]:
                    if name in user[field][song_id]:
                        old_start,old_end = user[field][song_id][name].split('-')
                        start = new_start or old_start
                        end = new_end or old_end
                        new_time = '-'.join([start,end])
                        user[field][song_id][name] = new_time
                        if ('-' in name) and (':' in name):
                            if all(map(lambda x: ':' in x, name.split('-'))):
                                rename(username, 
                                       service, 
                                       song_id, 
                                       name, 
                                       new_time, 
                                       field, 
                                       users, 
                                       path)
                                return
                        flamio.save(users,path)


def view(username,
         service,
         song_id=None, 
         field='loop',
         users={},
         path='.',
         user={}):
    # get w/ input and update if token expired
    """ view stored loops or skips, filtered by song and name """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = user or flamio.get_user(username, service, users, path)
            if song_id:
                if song_id in user[field]:
                    song_name = flamio.search.track_name(username, service, song_id, users, path)
                    for name,trange in user[field][song_id].items():
                        print(' -- '.join([song_id, song_name, name, trange]))
            else:
                if user[field]:
                    for song_id,loops in user[field].items():
                        song_name = flamio.search.track_name(username, service, song_id, users, path)
                        for name,trange in loops.items():
                            print(' -- '.join([song_id, song_name, name, trange]))


def rename(username,
           service,
           song_id,
           name,
           new_name,
           field='loop',
           users={},
           path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if song_id in user[field]:
                if name in user[field][song_id]:
                    user[field][song_id][new_name] = user[field][song_id].pop(name)
                    # rename in mixes
                    for mix in user['mix'].values():
                        for item in mix:
                            if item['field'] == field:
                                if item['song_id'] == song_id:
                                    if item['name'] == name:
                                        item['name'] = new_name
                    flamio.save(users,path)

def play(username,
         service,
         field,
         song_id,
         name='FULLSONG',
         cuts=[],
         skips=[],
         device=None, 
         reps=1,  
         repeat=False,
         checks=480,
         users={},
         path='.',
         start='0:0',
         end='0:0',
         buff=0,
         switch_restart=False,
         pause_at_finish=False):
    # play and update if token expired
    """ play existing loop or skip """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            songSaved = song_id in user[field] and name in user[field][song_id]
            if songSaved or name == 'FULLSONG':
                if name == 'FULLSONG':
                    start_ms = time_to_ms(start)
                    end_ms = time_to_ms(end) or end_to_ms(username, service, song_id, users, path)
                else:
                    times = user[field][song_id][name].split('-')
                    start_ms,end_ms = map(time_to_ms, times)
                cutzones = make_cutzone(user, song_id, skips, cuts)
                song_name = search.track_name(username, service, song_id, users, path)
                if name == 'FULLSONG':
                    if any(not time_to_ms(time) for time in [start, end]):
                        name = '{} - {} to {}'.format(field, start, ms_to_time(end_ms))
                else:
                    name = field+' - '+name
                cuts = ', '.join(map(lambda x: '{} to {}'.format(*x), cutzones))
                skip = ' skip: ' + cuts if cuts else ''
                name += skip
                
                def get_player():
                    return flamio.get_player(username,service,users,path)
                
                def inCut(progress_ms, cutzone):
                    for cut in cutzones:
                        if cut[0] <= progress_ms < cut[1]:
                            return cut[1]
                
                print('playing: {} -- {}'.format(song_name,name))
                
                # spotify play boi
                if service == 'spotify':
                    include = field == 'loop'
                    
                    def inLoop(playback, t1, t2, include):
                        if playback:
                            return (t1 <= playback['progress_ms'] < t2) == include
                        
                    def validPlayback(player, t1, t2, song_id, pauseKill, include):
                        playback = player.current_playback()
                        if playback:
                            if playback['item']:
                                if playback['item']['id'] == song_id:
                                    if playback['is_playing'] or (not pauseKill and inLoop(playback,t1,t2,include)):
                                        return playback
                    
                    uri = ['https://open.spotify.com/track/'+song_id]
                    player = get_player()
                    pb = player.current_playback()
                    if pb:
                        repeat = 'track' if repeat else pb['repeat_state']
                        if (not pb['is_playing']) or (pb['item']['id'] != song_id) or switch_restart:
                            player.start_playback(device_id=device, uris=uri)
                    else:
                        player.start_playback(device_id=device, uris=uri)
                        pb = player.current_playback()
                        repeat = 'track' if repeat else pb['repeat_state']
                    player.repeat(repeat)
                    
                    i=0
                    while pb and (i < reps or pb['repeat_state'] == 'track'):
                        player = get_player()
                        if not inLoop(player.current_playback(), start_ms, end_ms, include):
                            player.seek_track(start_ms if include else end_ms)
                            if not player.current_playback()['is_playing']:
                                player.start_playback()
                        while inLoop(player.current_playback(), start_ms+buff, end_ms-buff, include):
                            t.sleep((end_ms-start_ms - 2*buff)/(1000*checks))
                            in_cut = inCut(player.current_playback()['progress_ms'], cutzones)
                            if in_cut:
                                player.seek_track(min(in_cut,end_ms))
                            if not validPlayback(player, 
                                                 start_ms, 
                                                 end_ms, 
                                                 song_id, 
                                                 user['pauseKill'], 
                                                 include):
                              break
                        pb = validPlayback(get_player(), 
                                           start_ms, 
                                           end_ms, 
                                           song_id, 
                                           user['pauseKill'], 
                                           include)
                        i+=1
                    
                    player = get_player()
                    pb = player.current_playback()
                    if pb:
                        if pb['is_playing']:
                            if pb['item']:
                                if pb['item']['id'] == song_id:
                                    if pause_at_finish:
                                        player.pause_playback()
                            return True
                # soundcloud play boi
                elif service == 'soundcloud':
                    pass
                # apple music play boi
                elif service == 'apple_music':
                    pass