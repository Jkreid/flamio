# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 21:07:13 2019

@author: justi

API mixify
"""

import src.api.flamio as flamio
import src.api as api
import time as t
#==============================================================================
# Mix Functions
#==============================================================================

### mix positon arguments are 1 indexed

def new(username,
        service,
        field,
        name=None,
        users={},
        path= '.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            mixes = user[field]
            if name not in mixes:
                if not name:
                    untitled = sorted(list(filter(lambda x: 'untitled' in x, mixes)))
                    number = int(untitled[-1].split(' ')[-1]) + 1
                    while 'untitled {}'.format(number) in untitled:
                        number += 1
                    name = 'untitled {}'.format(number)
                mixes[name] = []
                flamio.save(users,path)


def add_loop(username,
             service,
             obj_field,
             name,
             song_id,
             loop_name='FULLSONG',
             position=None, 
             item_field='loop', 
             reps=1,
             users={},
             path='.',
             start=None,
             end=None):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[obj_field]:
                if song_id in user[item_field] or loop_name == 'FULLSONG':
                    if loop_name == 'FULLSONG' or loop_name in user[item_field][song_id]:
                        mix = user['mix'][name]
                        loop = {'field':item_field, 
                                'song_id':song_id, 
                                'name':loop_name, 
                                'reps':reps}
                        if item_field == 'loops' and loop_name == 'FULLSONG':
                            if start or end:
                                if start:
                                    loop['start'] = start
                                if end:
                                    loop['end'] = end
                            else:
                                loop['buff'] = 500
                        position = position or len(mix) + 1
                        mix.insert(position-1, loop)
                        flamio.save(users,path)


def add_skip(username,
             service,
             obj_field,
             name,
             song_id,
             loop_name='FULLSONG',
             position=None, 
             reps=1,
             users={},
             path='.',
             start=None,
             end=None):
    # update
    return add_loop(username=username,
                    service=service,
                    obj_field,
                    name=name,
                    song_id=song_id,
                    loop_name=loop_name,
                    position=position, 
                    item_field='skip', 
                    reps=reps,
                    users=users,
                    path=path,
                    start=start,
                    end=end)


def add_mix(username,
            service,
            obj_field,
            name,
            item_name,
            item_field='mix',
            position=None,
            reps=1,
            users={},
            path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[obj_field]:
                if item_name in user[item_field]:
                    mix = user[obj_field][name]
                    mix = {'field':item_field, 
                            'name':item_name, 
                            'reps':reps}
                    position = position or len(mix) + 1
                    mix.insert(position-1, mix)
                    flamio.save(users,path)


def add_pause(username,
              service,
              field,
              duration,
              position=None,
              users={},
              path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                pause = {'field':'pause', 
                        'seconds':duration}
                position = position or len(mix) + 1
                mix.insert(position-1, pause)
                flamio.save(users,path)


def move_item(username,
              service,
              field,
              name, 
              init_position, 
              new_position=0,
              users={},
              path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                num_loops = len(mix)
                if init_position and -num_loops <= init_position <= num_loops:
                    new_position = new_position or num_loops
                    mix.insert(new_position-1, mix.pop(init_position-1))
                    flamio.save(users,path)


def duplicate_item(username,
                   service,
                   field,
                   name,
                   init_position, 
                   paste_position=None, 
                   reps=None,
                   users={},
                   path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                num_loops = len(mix)
                if init_position and -num_loops <= init_position <= num_loops:
                    paste_position = paste_position or num_loops+1
                    mix.insert(paste_position-1, mix[init_position-1])
                    if reps:
                        change_reps(username, 
                                    service, 
                                    name, 
                                    min(paste_position,len(mix)), 
                                    reps, 
                                    users, 
                                    path)
                    flamio.save(users,path)


def remove(username, 
                service,
                field,
                name, 
                position=0,
                users={},
                path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                num_loops = len(mix)
                if position and -num_loops <= position <= num_loops:
                    mix.pop(position-1)
                    flamio.save(users,path)


def change_reps(username,
                service,
                field,
                name,
                position=0,
                reps=1,
                users={},
                path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                num_loops = len(mix)
                if position and -num_loops <= position <= num_loops:
                    mix[position-1]['reps'] = reps
                    flamio.save(users,path)


def time_pause_pb(username, service, seconds, users={}, path='.'):
    player = flamio.get_player(username,service,users,path)
    if service == 'spotify':
        pb = player.current_playback()
        if pb:
            if pb['is_playing']:
                player.pause_playback()
                t.sleep(seconds)
                flamio.get_player(username,service,users,path).start_playback()
            else:
                t.sleep(seconds)
                flamio.get_player(username,service,users,path).start_playback()
    elif service == 'soundcloud':
        pass
    elif service == 'apple_music':
        pass


def view(field,
         name,
         user={},
         username=None, 
         service=None,
         users={},
         path='.'):
    # get w/ input
    user = user or flamio.get_user(username, service, users, path)
    if name in user[field]:
        mix = user[field][name]
        for i,item in enumerate(mix):
            info = ', '.join(['{}: {}'.format(context, value) for context,value in item.items()])
            print('{}. {}'.format(i+1,info))


def delete(username,
           service,
           field,
           name,
           users={},
           path='.'):
    # delete
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                del user[field][name]
                flamio.save(users,path)


def rename(username,
           service,
           field,
           name,
           new_name,
           users={},
           path='.'):
    # update
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                user[field][new_name] = user[field].pop(name)
                # rename in mixes
                for mix in user['mix'].values():
                    for item in mix:
                        if item['field'] == 'mix':
                            if item['name'] == name:
                                item['name'] = new_name
                flamio.save(users,path)


def unpack_nested(username, service, field, name, position, users={}, path='.'):
    users = users or flamio.get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            if name in user[field]:
                mix = user[field][name]
                num_loops = len(mix)
                if position and -len(mix) <= position <= num_loops:
                    nested_mix = mix.pop(position-1)
                    if nested_mix['field'] == 'mix':
                        for item in reversed(nested_mix):
                            mix.insert(position-1,item)
                        flamio.save(users,path)


def zip_to_mix(uesrname, service, field, name, new_name=None, postition_1, position_2, users={}, path='.'):
    first,last = sorted(map(int, (postition_1, position_2)))
    new(username, service, field, new_name, users, path)
    for item in mix[first_position-1:end_position]:
        add_item(username, service, mix_name=new_name, users=users, path=path, **item)


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