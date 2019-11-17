# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 17:18:52 2019

@author: justi

API loopify
"""
import src.api.utils.flamio as flamio
import time as t

# =============================================================================
# Loop and Skip Functions
# =============================================================================

def time_to_ms(time):
    """ '0:00' to milisecond """
    minute,seconds = map(float,time.split(':'))
    return int(1000*(minute*60 + seconds))


def ms_to_time(ms):
    """ milisecond to '0:00' """
    ms = int(ms)
    minute,seconds = int(ms/60000), round((ms/1000)%60,3)
    return ':'.join(map(str,(minute,seconds)))


def end_to_ms(username, 
              service, 
              song_id, 
              users, 
              path):
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


def new_loop(username,
             service,
             song_id,
             name=None,
             start='0:00',
             end=None,
             field='loops',
             users={},
             path='.'):
    # update
    """ add loop or skip to saved options """
    if not ((start == '0:00') and (not end) and (field == 'skips')):
        users = users or flamio.get_users(path)
        if username in users:
            if service in users[username]:
                user = users[username][service]
                end = end or end_to_time(username, service, song_id, users, path)
                time_range = '-'.join([start,end])
                name = name or time_range
                if song_id not in user[field]:
                    user[field][song_id] = {}
                user[field][song_id][name] = time_range
                flamio.save(users,path)


def new_skip(username,
             service,
             song_id,
             name=None,
             start='0:00',
             end=None,
             users={},
             path='.'):
    # update
    return new_loop(username=username,
                    service=service,
                    song_id=song_id,
                    name=name,
                    start=start,
                    end=end,
                    field='skips',
                    users=users,
                    path=path)


def delete_loop(username,
                service,
                song_id,
                name,
                field='loops',
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


def delete_skip(username,
                service,
                song_id,
                name,
                field='skips',
                users={},
                path='.'):
    # delete
    return delete_loop(username=username,
                       service=service,
                       song_id=song_id,
                       name=name,
                       field='skips',
                       users=users,
                       path=path)

def edit_loop(username,
              service,
              song_id, 
              name, 
              new_start=None, 
              new_end=None, 
              field='loops',
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
                                rename_loop(username, 
                                            service, 
                                            song_id, 
                                            name, 
                                            new_time, 
                                            field, 
                                            users, 
                                            path)
                                return
                        flamio.save(users,path)

def edit_skip(username,
              service,
              song_id, 
              name, 
              new_start=None, 
              new_end=None, 
              users={},
              path='.'):
    # update
    return edit_loop(username=username,
              service=service,
              song_id=song_id, 
              name=name, 
              new_start=new_start, 
              new_end=new_end, 
              field='skips',
              users=users,
              path=path)
        

def view_loops(username,
               service,
               song_id=None, 
               field='loops',
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

def view_skips(username,
               service,
               song_id=None, 
               users={},
               path='.'):
    # get w/ input
    return view_loops(username=username,
                      service=service,
                      song_id=song_id, 
                      field='skips',
                      users=users,
                      path=path)


def rename_loop(username,
                service,
                song_id,
                name,
                new_name,
                field='loops',
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
                    # rename in playlists and stremixes
                    for playlist in user['playlists'].values():
                        for item in playlist:
                            if item['field'] == field:
                                if item['song_id'] == song_id:
                                    if item['name'] == name:
                                        item['name'] = new_name
                    for mix in user['stremixes'].values():
                        pass
                    flamio.save(users,path)
                    

def rename_skip(username,
                service,
                song_id,
                name,
                new_name,
                users={},
                path='.'):
    # update
    return rename_loop(username=username,
                       service=service,
                       song_id=song_id,
                       name=name,
                       new_name=new_name,
                       field='skips',
                       users=users,
                       path=path)


def play(username,
         service,
         song_id, 
         name='FULLSONG', 
         device=None, 
         reps=1,  
         field='loops',
         repeat=False,
         checks=480,
         users={},
         path='.',
         start='0:0',
         end='0:0',
         buff=0):
    # play and update if token expired
    """ play existing loop or skip """
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            songSaved = song_id in user[field] and name in user[field][song_id]
            if songSaved or name == 'FULLSONG':
                # spotify play boi
                if service == 'spotify':
                    include = field == 'loops'
                    def inLoop(playback, t1, t2, include):
                        if playback:
                            return (t1 < playback['progress_ms'] < t2) == include
                        
                    def validPlayback(player, t1, t2, song_id, pauseKill, include):
                        playback = player.current_playback()
                        if playback:
                            if playback['item']:
                                if playback['item']['id'] == song_id:
                                    if playback['is_playing'] or (not pauseKill and inLoop(playback,t1,t2,include)):
                                        return playback
                    
                    def get_player():
                        return flamio.get_player(username,service,users,path)
                                    
                    if name == 'FULLSONG':
                        player = get_player()
                        start_ms = time_to_ms(start)
                        end_ms = time_to_ms(end) or player.track(song_id)['duration_ms']
                    else:
                        times = user[field][song_id][name].split('-')
                        start_ms,end_ms = map(time_to_ms, times)
                    uri = ['https://open.spotify.com/track/'+song_id]
                    player = get_player()
                    if name == 'FULLSONG':
                        if any(not time_to_ms(time) for time in [start, end]):
                            name = '{} - {} to {}'.format(field[:-1], start, ms_to_time(end_ms))
                    else:
                        name = field[:-1]+' - '+name
                    print('playing: {} -- {}'.format(player.track(song_id)['name'],name))                
                    pb = player.current_playback()
                    if pb:
                        repeat = 'track' if repeat else pb['repeat_state']
                        if (not pb['is_playing']) or (pb['item']['id'] != song_id):
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
                        while inLoop(get_player().current_playback(), start_ms+buff, end_ms-buff, include):
                            t.sleep((end_ms-start_ms)/(1000*checks))
                            if not validPlayback(get_player(), 
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
                                    player.pause_playback()
                                    return True
                # soundcloud play boi
                elif service == 'soundcloud':
                    pass
                # apple music play boi
                elif service == 'apple_music':
                    pass

# =============================================================================
# def play_skip(username,
#          service,
#          song_id, 
#          name='FULLSONG', 
#          device=None, 
#          reps=1,  
#          repeat=False,
#          checks=480,
#          users={},
#          path='.',
#          start='0:0',
#          end='0:0',
#          buff=0):
#     # play and update if token expired
#     return play_loop(username=username,
#                      service=service,
#                      song_id=song_id, 
#                      name=name, 
#                      device=device, 
#                      reps=reps,  
#                      field='skips',
#                      repeat=repeat,
#                      checks=checks,
#                      users=users,
#                      path=path,
#                      start=start,
#                      end=end,
#                      buff=buff)
# =============================================================================
