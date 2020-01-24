# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 20:30:38 2019

@author: justi
"""

import time as t

def pause(username, service, seconds=None, users={}, path='.'):
    player = flamio.get_player(username,service,users,path)
    if service == 'spotify':
        pb = player.current_playback()
        if pb:
            if pb['is_playing']:
                player.pause_playback()
                if seconds:
                    t.sleep(seconds)
                    flamio.get_player(username,service,users,path).start_playback()
            else:
                if seconds:
                    t.sleep(seconds)
                    flamio.get_player(username,service,users,path).start_playback()
    elif service == 'soundcloud':
        pass
    elif service == 'apple_music':
        pass


def spotify_play():
    pass


def display_playing(username, service, name, song_id=None, loops=None, skips=None, users=None, path=None):
    if song_id:
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
        name += ' skip: ' + cuts if cuts else ''
        print('playing: {} -- {}'.format(song_name,name))
    else:
        print('playing mix: {}'.format(name))


def play():
    display_playing()
    if song_id:
        initialize_play()
        play_loops_w_skips()
        if pause_at_finished:
            pause()
        return True
    else:
        pass

#### consolidate lower play functions into above one
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
                
                def get_player():
                    return flamio.get_player(username,service,users,path)
                
                def inCut(progress_ms, cutzone):
                    for cut in cutzones:
                        if cut[0] <= progress_ms < cut[1]:
                            return cut[1]
                
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
                name += ' skip: ' + cuts if cuts else ''
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


def play(username,
         service,
         field,
         name, 
         reps=1,
         repeat=False, 
         device=None, 
         offset=0, 
         reverse=False,
         users={},
         path='.',
         switch_delay=False,
         switch_restart=False,
         pause_at_finish=True):
    # play
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                player = flamio.get_player(username,service,users,path)
                i,j=0,0
                print('playing mix: {}'.format(name))
                
                if service == 'spotify':
                    player.repeat('context' if repeat else 'off')
                    while (i < reps) or (player.current_playback()['repeat_state'] == 'context'):
                        for item in reversed(mix) if reverse else mix:
                            if item['field'] == 'pause':
                                time_pause_pb(username, service, item['seconds'], users=users, path=path)
                            else:
                                if not i and j < offset:
                                    continue
                                continue_play = api.play(username=username,
                                                         service=service,
                                                         users=users,
                                                         path=path,
                                                         device=device,
                                                         pause_at_finish=switch_delay,
                                                         switch_restart=switch_restart,
                                                         **item)
                                player = flamio.get_player(username,service,users,path)
                                if not continue_play:
                                    break
                        if player.current_playback()['repeat_state'] == 'off' or not continue_play:
                            break
                    pb = player.current_playback()
                    if pb:
                        if pb['is_playing']:
                            if pause_at_finish:
                                player.pause_playback()
                        return True
                
                elif service == 'soundcloud':
                    pass
                
                elif service == 'apple_music':
                    pass