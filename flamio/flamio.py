# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 00:45:49 2021

@author: justi
"""

import flamio.utils as utils


#// Path Functions ////////////////////////////////////////////////////////////

def pathError(path_function):
    def pathFunction(*args, **kwargs):
        try:
            return path_function(*args, **kwargs)
        except IndexError as ie:
            raise ie
        except KeyError as ke:
            raise ke
    return pathFunction

@pathError
def get(data, *path):
    for key in path:
        data = data[key]
    return data

@pathError
def insert(data, update, *path):
    *keys, final_key = path
    data = get(data, *keys)
    if isinstance(data, list):
        data.insert(final_key, update)
    else:
        data[final_key] = update

@pathError
def edit(data, update, *path):
    *keys, final_key = path
    data = get(data, *keys)
    data[final_key] = update

@pathError
def create(data, *path, isList=False):
    insert(data, [] if isList else {}, *path)

@pathError
def delete(data, *path):
    *keys, final_key = path
    data = get(data, *keys)
    del data[final_key]

def multidelete(data, positions, *path):
    if isinstance(get(data, *path), list):
        for i, pos in enumerate(sorted(positions)):
            new_path = f'{"/".join(map(str, path))}/{pos - i}'.split('/')
            delete(data, *new_path)

def duplicate(data, copy_position, paste_position, *path):
    items = get(data, *path)
    if isinstance(items, list):
        items.insert(paste_position, items[copy_position])

def move(data, init_position, new_position, *path):
    items = get(data, *path)
    if isinstance(items, list):
        items.insert(new_position, items.pop(init_position))

def swap(data, position_x, position_y, *path):
    items = get(data, *path)
    if isinstance(items, list):
        position_x, position_y = sorted((position_x, position_y))
        items.insert(position_x, items.pop(position_y))
        items.insert(position_y, items.pop(position_x + 1))

def add(data, update, *path):
    create(data, *path, isList=isinstance(update, list))
    insert(data, update, *path)

#// Tracks ////////////////////////////////////////////////////////////////////

def create_track(uinfo, track_id, track_info={}):
    data = {
        'meta':{'track_info':track_info},
        'loops':{},
        'skips':{},
        'tags':[],
        'volumes':{},
    }
    add(uinfo, data, 'tracks', track_id)

def get_track(uinfo, track_id):
    return get(uinfo, 'tracks', track_id)

def delete_track(uinfo, track_id):
    delete(uinfo, 'tracks', track_id)

#// Tags /////////////////////////////////////////////////////////////////////

def create_tag(uinfo, tag):
    create(uinfo, 'tags', tag, isList=True)

def get_tag(uinfo, tag):
    return get(uinfo, 'tags', tag)

def delete_tag(uinfo, tag):
    for x in get_tag(uinfo, tag):
        obj, name = x.split('/')
        r = remove_tag_from_track if obj == 'tracks' else remove_tag_from_mix
        r(uinfo, name, tag)
    delete(uinfo, 'tags', tag)

def rename_tag(uinfo, tag, new_name):
    create_tag(uinfo, new_name)
    for x in get_tag(uinfo, tag):
        obj, name = x.split('/')
        if obj == 'tracks':
            add_tag_to_track(uinfo, name, tag)
            remove_tag_from_track(uinfo, name, tag)
        else:
            add_tag_to_mix(uinfo, name, tag)
            remove_tag_from_mix(uinfo, name, tag)
    delete(uinfo, 'tags', tag)

def get_track_tags(uinfo, track_id):
    return get(uinfo, 'tracks', track_id, 'tags')

def add_tag_to_track(uinfo, track_id, tag):
    get_tag(uinfo, tag).append(f'tracks/{track_id}')
    get_track_tags(uinfo, track_id).append(tag)

def remove_tag_from_track(uinfo, track_id, tag):
    get_tag(uinfo, tag).remove(f'tracks/{track_id}')
    get_track_tags(uinfo, track_id).remove(tag)

def get_mix_tags(uinfo, name):
    return get(uinfo, 'mixes', name, 'tags')

def add_tag_to_mix(uinfo, name, tag):
    get_tag(uinfo, tag).append(f'mixes/{name}')
    get_mix_tags(uinfo, name).append(tag)

def remove_tag_from_mix(uinfo, name, tag):
    get_tag(uinfo, tag).remove(f'mixes/{name}')
    get_mix_tags(uinfo, name).remove(tag)

#// Loops /////////////////////////////////////////////////////////////////////

def create_loop(uinfo, track_id, name):
    create(uinfo, 'tracks', track_id, 'loops', name, isList=True)

def get_loop(uinfo, track_id, name):
    return get(uinfo, 'tracks', track_id, 'loops', name)

def delete_loop(uinfo, track_id, name):
    delete(uinfo, 'tracks', track_id, 'loops', name)

def add_loop_time(uinfo, track_id, name, 
                  start='',
                  end='',
                  reps=1,
                  volume=100,
                  index=0):
    data = {
        'start':start,
        'end':end,
        'reps':reps,
        'volume':100
    }
    insert(uinfo, data, 'tracks', track_id, 'loops', name, index)

def get_loop_time(uinfo, track_id, name, index):
    return get(uinfo, 'tracks', track_id, 'loops', name, index)

def edit_loop_time(uinfo, track_id, name, 
                   start='',
                   end='',
                   reps=0,
                   volume=0,
                   index=0):
    current = get_loop_time(uinfo, track_id, name, index)
    data = {
        'start':start or current['start'],
        'end':end or current['end'],
        'reps':reps or current['reps'],
        'volume':volume or current['volume']
    }
    edit(uinfo, data, 'tracks', track_id, 'loops', name, index)

def delete_loop_time(uinfo, track_id, name, index):
    delete(uinfo, 'tracks', track_id, 'loops', name, index)

def multidelete_loop_times(uinfo, track_id, name, positions):
    multidelete(uinfo, positions, 'tracks', track_id, 'loops', name)

def duplicate_loop_time(uinfo, track_id, name, copy_position, paste_position):
    duplicate(uinfo, copy_position, paste_position,
              'tracks', track_id, 'loops', name)

def move_loop_time(uinfo, track_id, name, init_position, new_position):
    move(uinfo, init_position, new_position,
         'tracks', track_id, 'loops', name)

def swap_loop_times(uinfo, track_id, name, position_x, position_y):
    swap(uinfo, position_x, position_y,
         'tracks', track_id, 'loops', name)

#// Skips /////////////////////////////////////////////////////////////////////

def create_skip(uinfo, track_id, name, always=False):
    data = {
        'times':[],
        'always':always
    }
    add(uinfo, data, 'tracks', track_id, 'skips', name)

def get_skip(uinfo, track_id, name):
    return get(uinfo, 'tracks', track_id, 'skips', name)

def delete_skip(uinfo, track_id, name):
    delete(uinfo, 'tracks', track_id, 'skips', name)

def add_skip_time(uinfo, track_id, name,
                  start='',
                  end='',
                  index=0):
    data = {
        'start':start,
        'end':end
    }
    insert(uinfo, data, 'tracks', track_id, 'skips', name, 'times', index)

def get_skip_time(uinfo, track_id, name, index):
    return get(uinfo, 'tracks', track_id, 'skips', name, 'times', index)

def edit_skip_time(uinfo, track_id, name,
                   start='',
                   end='',
                   index=0):
    current = get_skip_time(uinfo, track_id, name, index)
    data = {
        'start':start or current['start'],
        'end':end or current['end']
    }
    edit(uinfo, data, 'tracks', track_id, 'skips', name, 'times', index)

def delete_skip_time(uinfo, track_id, name, index):
    delete(uinfo, 'tracks', track_id, 'skips', name, 'times', index)

def multidelete_skip_times(uinfo, track_id, name, positions):
    multidelete(uinfo, positions, 'tracks', track_id, 'skips', name, 'times')

def duplicate_skip_time(uinfo, track_id, name, copy_position, paste_position):
    duplicate(uinfo, copy_position, paste_position,
              'tracks', track_id, 'skips', name, 'times')

def move_skip_time(uinfo, track_id, name, init_position, new_position):
    move(uinfo, init_position, new_position,
         'tracks', track_id, 'skips', name, 'items')

def swap_skip_times(uinfo, track_id, name, position_x, position_y):
    swap(uinfo, position_x, position_y,
         'tracks', track_id, 'skips', name, 'items')

#// Mixes /////////////////////////////////////////////////////////////////////

def create_mix(uinfo, name):
    data = {
        'items':[],
        'tags':[],
        'meta':{}
    }
    add(uinfo, data, 'mixes', name)

def get_mix(uinfo, name):
    return get(uinfo, 'mixes', name)

def delete_mix(uinfo, name):
    delete(uinfo, 'mixes', name)

def add_mix_item(uinfo, name, data, index):
    insert(uinfo, data, 'mixes', name, 'items', index)

def get_mix_item(uinfo, name, index):
    return get(uinfo, 'mixes', name, 'items', index)

def edit_mix_item(uinfo, name, data, index):
    current = get_mix_item(uinfo, name, index)
    if all(x in current for x in data.keys()):
        new_data = {x:y or current[x] for x,y in data.items()}
        edit(uinfo, new_data, 'mixes', name, 'items', index)

def delete_mix_item(uinfo, name, index):
    delete(uinfo, 'mixes', name, 'items', index)

def multidelete_mix_items(uinfo, track_id, name, positions):
    multidelete(uinfo, positions, 'mixes', name, 'items')

def duplicate_mix_item(uinfo, name, copy_position, paste_position):
    duplicate(uinfo, copy_position, paste_position,
              'mixes', name, 'items')

def move_mix_item(uinfo, name, init_position, new_position):
    move(uinfo, init_position, new_position,
         'mixes', name, 'items')

def swap_mix_items(uinfo, name, position_x, position_y):
    swap(uinfo, position_x, position_y,
         'mixes', name, 'items')

def loop_rep_check(function):
    def loop_rep_safe_function(*args, loops=[], **kwargs):
        for i, loop in enumerate(loops):
            try:
                assert not isinstance(loop, str)
                iter(loop)
            except:
                loops[i] = (loop, 1)
        return function(*args, loops=loops, **kwargs)
    return loop_rep_safe_function

@loop_rep_check
def add_mix_track(uinfo, name, track_id, loops=[], skips=[], reps=1, index=0):
    data = {
        'track_id':track_id,
        'track_reps':reps,
        'loops':loops,
        'skips':skips
    }
    add_mix_item(uinfo, name, data, index)

def add_mix_pause(uinfo, name, duration, index=0):
    data = {'duration':duration}
    add_mix_item(uinfo, name, data, index)

def add_mix_mix(uinfo, name, mix_name, reps=1, index=0):
    assert name != mix_name
    data = {
        'name':mix_name,
        'mix_reps':reps
    }
    add_mix_item(uinfo, name, data, index)

@loop_rep_check
def edit_mix_track(uinfo, name, track_id, loops=[], skips=[], reps=0, index=0):
    data = {
        'track_id':track_id,
        'track_reps':reps,
        'loops':loops,
        'skips':skips
    }
    edit_mix_item(uinfo, name, data, index)

def edit_mix_pause(uinfo, name, duration=0, index=0):
    data = {'duration':duration}
    edit_mix_item(uinfo, name, data, index)

def edit_mix_mix(uinfo, name, mix_name='', reps=0, index=0):
    data = {
        'name':mix_name,
        'mix_reps':reps
    }
    edit_mix_item(uinfo, name, data, index)

#// Data Formatters ///////////////////////////////////////////////////////////

def get_play_info_from_loop(loop):
    return [
        (utils.time_to_ms(interval['start']),
         utils.time_to_ms(interval['end']),
         interval['reps'])
        for interval in loop
    ]

@loop_rep_check
def get_track_loop_infos(uinfo, track_id, loops=[]):
    return [(get_play_info_from_loop(
        get_loop(uinfo, track_id, loop_name)
    ), loop_reps) for loop_name, loop_reps in loops]

def get_track_always_skip_name_list(uinfo, track_id):
    return [name 
            for name, data in get_track(uinfo, track_id)['skips'].items() 
            if data['always']]

def get_track_skip_times(uinfo, track_id, skip_names=[], include_always=True):
    return [data['times'] 
            for name, data in get_track(uinfo, track_id)['skips'].items() 
            if name in skip_names or (data['always'] and include_always)]

def skips_times_to_intervals(skip_times):
    # skip_names : List[str]
    return utils.times_to_intervals(
        [times
         for skip_time in skip_times 
             for times in skip_time]
    )

def skips_to_intervals(uinfo, track_id, skip_names=[], include_always=True):
    return skips_times_to_intervals(
        get_track_skip_times(uinfo, track_id, skip_names,
                             include_always=include_always)
    )

def get_track_volume_info(uinfo, track_id, loop_names=[]):
    pass

def get_track_play_info(uinfo, track_id, loop_names=[], skip_names=[],
                        include_always=True):
    return (get_track_loop_infos(uinfo, track_id, loops=loop_names),
            skips_to_intervals(uinfo, track_id, skip_names=skip_names,
                               include_always=include_always),
            get_track_volume_info(uinfo, track_id, loop_names))

def get_item_play_info(uinfo, item, include_always=True):
    if 'track_id' in item:
        return [(
            item['track_id'], 
            get_track_play_info(
                uinfo, item['track_id'], item['loops'], item['loops'], 
                include_always=include_always
            ), 
            item['track_reps']
        )]
    elif 'name' in item:
        return get_mix_play_info(
            uinfo, item['name'], 
            include_always=include_always
        )*item['mix_reps']
    elif 'duration' in item:
        return [(item['duration'],)]
    else:
        raise ValueError('Invalid object in mix')

        
def get_mix_play_info(uinfo, name, include_always=True):
    info = []
    for item in get_mix(uinfo, name)['items']:
        info += get_item_play_info(uinfo, item, include_always=include_always)
    return info
        