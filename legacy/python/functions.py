# -*- coding: utf-8 -*-
"""
Created on Sat May 30 15:45:51 2020

@author: justi
"""

import os
import json
import time as t
import spotipy_master.spotipy.util as util
import spotipy_master.spotipy as spotipy

#// Constants /////////////////////////////////////////////////////////////////

DATA_PATH = '.'

AUTHS = {
    'spotify':{
        'redirect_uri'  : 'http://localhost:8888/lab',
        'client_id'     : 'cd33a00276a645f393445c438115b958',
        'client_secret' : 'b9988db76d074442aa81a37312d12d29',
        'scope'         : 'streaming \
                           user-read-playback-state \
                               user-modify-playback-state \
                                   user-read-currently-playing'
    },
    'soundcloud' : {},
    'apple_music': {}
}

tokenLifetime = {
    'spotify':3600,
    'soundcloud':1200,
    'apple_music':1200
}

#// Data Storage //////////////////////////////////////////////////////////////

def get_users() -> dict:
    """
    Load user data from disk

    Returns
    -------
    dict
        DESCRIPTION.

    """
    if os.path.exists(DATA_PATH):
        SAVE_PATH = DATA_PATH + '/data.json'
        if os.path.exists(SAVE_PATH):
            with open(SAVE_PATH, 'r') as data:
                users = json.load(data)
            return users
    return {'__base__':{}}


def save(data: dict) -> None:
    """
    Save data to disk

    Parameters
    ----------
    data : dict
        DESCRIPTION.

    Returns
    -------
    None.

    """
    if not os.path.exists(DATA_PATH):
        os.mkdir(DATA_PATH)
    SAVE_PATH = DATA_PATH + '/data.json'
    if data:
        with open(SAVE_PATH, 'w') as f:
            json.dump(SAVE_PATH, f)


def load(function):
    def newFunction(*args, **kwargs):
        users = get_users()
        value = function(users, *args, **kwargs)
        return value
    return newFunction

def update(function):
    def updater(data, *args, **kwargs):
        value = function(data, *args, **kwargs)
        save(data)
        return value
    return updater

def modify(function):
    def modifier(*args, **kwargs):
        users = get_users()
        value = function(users, *args, **kwargs)
        save(users)
        return value
    return modifier

#// HTTP Request ////////////////////////////////////////////////////////

def get(
        data: dict, 
        path: str
    ):
    """
    Get data from the given path

    Parameters
    ----------
    data : dict
        DESCRIPTION.
    path : str
        DESCRIPTION.

    Returns
    -------
    data : TYPE
        DESCRIPTION.

    """
    keys = path.split('/')
    for key in keys:
        if key:
            data = data[int(key) if type(data) is list else key]
    return data


def put(
        data: dict, 
        path: str, 
        new_data
    ) -> None:
    """
    Update data at the given path with new data

    Parameters
    ----------
    data : dict
        DESCRIPTION.
    path : str
        DESCRIPTION.
    new_data : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    """
    *keys, final_key = path.split('/')
    data = get(data, '/'.join(keys))
    if type(data) is list:
        data.insert(int(final_key), new_data)
    else:
        data[final_key] = new_data


def post(
        data: dict, 
        path: str, 
        listType: bool = False
    ) -> None:
    """
    Create new data container at the given path

    Parameters
    ----------
    data : dict
        DESCRIPTION.
    path : str
        DESCRIPTION.
    listType : bool, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None.

    """
    if path[-1] == '/':
        path = path[:-1]
    put(data, path, [] if listType else {})


def delete(
        data: dict, 
        path: str
    ) -> None:
    """
    Delete data at the given path

    Parameters
    ----------
    data : dict
        DESCRIPTION.
    path : str
        DESCRIPTION.

    Returns
    -------
    None.

    """
    *keys, final_key = path.split('/')
    data = get(data, '/'.join(keys))
    del data[int(final_key) if type(data) is list else final_key]


@modify
def new_item(users: dict, data, *args):
    path = '/'.join(args)
    post(users, path)
    put(users, path, data)

@load
def get_item(users: dict, *args):
    return get(users, '/'.join(args))

@modify
def delete_item(users: dict, *args):
    delete(users, '/'.join(args))

@modify
def edit_item(users: dict, data, *args):
    put(users, '/'.join(args), data)

@modify
def rename_item(users: dict, new_name: str, *args):
    # TODO: Once mixes are defined
    pass

#// Tokens and Players ////////////////////////////////////////////////////////

def get_spotify_token(account_username: str):
    """
    

    Parameters
    ----------
    account_username : str
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return util.prompt_for_user_token(
        account_username, 
        **AUTHS['spotify']
    )

def get_soundcloud_token(account_username: str):
    pass

def get_apple_music_token(account_username: str):
    pass

def get_token(
        service: str, 
        account_username: str
    ):
    """
    

    Parameters
    ----------
    service : str
        DESCRIPTION.
    account_username : str
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    return {
        'spotify':get_spotify_token,
        'soundcloud':get_soundcloud_token,
        'apple_music':get_apple_music_token
    }[service](account_username)


def get_spotify_player(account: dict) -> spotipy.Spotify:
    """
    

    Parameters
    ----------
    account : dict
        DESCRIPTION.

    Returns
    -------
    spotipy.Spotify
        DESCRIPTION.

    """
    meta   = account['meta']
    player = spotipy.Spotify(auth=meta['token'])
    try:
        player.me()
        return player
    except:
        print('refreshing token')
        service = meta['service']
        account_username = meta['account_username']
        token   = get_token(service, account_username)
        meta['token'] = token
        return spotipy.Spotify(auth=token)

def get_soundcloud_player(account: dict):
    pass

def get_apple_music_player(account: dict):
    pass

def get_player(
        username: str, 
        service: str
    ):
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    account = get_streaming_account(username, service)
    return {
        'spotify':get_spotify_player,
        'soundcloud':get_soundcloud_player,
        'apple_music':get_apple_music_player
    }[service](account)

#// Users and Accounts ////////////////////////////////////////////////////////

def new_user(username: str) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    data = {
        'name':username
    }
    new_item(data, username)

def get_user(username: str) -> dict:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return get_item(username)

def delete_user(username: str) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete_item(username)


def new_streaming_account(
        username: str,
        service: str,
        account_username: str
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    account_username : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    assert service in (
        'spotify', 
        'soundcloud', 
        'apple_music'
    )
    token = get_token(service, account_username)
    if not token:
        return
    meta = {
        'token':token,
        'service':service,
        'login_time':t.time(),
        'tokenLifetime':tokenLifetime[service],
        'account_username':account_username
    }
    data = {
        'meta':meta,
        'mixes':{},
        'tracks':{},
        'playlist':{}
    }
    new_item(data, username, service)

def get_streaming_account(
        username: str,
        service: str
    ) -> dict:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return get_item(username, service)

def delete_streaming_account(
        username: str,
        service: str
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete_item(username, service)

#// Time Helper Functions /////////////////////////////////////////////////////

def time_to_ms(time: str) -> int:
    """
    Time in 'X:YY.YYY' notation to miliseconds
    where X is the number of minutes
    and Y is the number of seconds to milisecond precision

    Parameters
    ----------
    time : str
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    minutes, seconds = map(float,time.split(':'))
    return int(1000*(minutes*60 + seconds))

def ms_to_time(ms: int) -> str:
    """
    Miliseconds to time in 'X:YY.YYY' notation
    where X is the number of minutes
    and Y is the number of seconds to milisecond precision

    Parameters
    ----------
    ms : int
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    ms = int(ms)
    minute,seconds = int(ms/60000), round((ms/1000)%60,3)
    return ':'.join(map(str,(minute,seconds)))

def spotify_end_to_ms(
        track_id: str,
        player: spotipy.Spotify
    ) -> int:
    """
    

    Parameters
    ----------
    track_id : str
        DESCRIPTION.
    player : spotipy.Spotify
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    return int(player.track(track_id)['duration_ms'])

def soundcloud_end_to_ms(track_id: str, player):
    pass

def apple_music_end_to_ms(track_id: str, player):
    pass

def end_to_ms(
        username: str,
        service: str,
        track_id: str
    ) -> int:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.

    Returns
    -------
    int
        DESCRIPTION.

    """
    player = get_player(username, service)
    return {
        'spotify':spotify_end_to_ms,
        'soundcloud':soundcloud_end_to_ms,
        'apple_music':apple_music_end_to_ms
    }[service](track_id, player)

def end_to_time(
        username: str,
        service: str,
        track_id: str
    ) -> str:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.

    Returns
    -------
    str
        DESCRIPTION.

    """
    return ms_to_time(end_to_ms)

#// Tracks ////////////////////////////////////////////////////////////////////

def new_track(
        username: str,
        service:str,
        track_id: str
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    meta = {
        'name':'' #utils.name(track_id)
    }
    data = {
        'meta':meta,
        'loops':{},
        'skips':{}
    }
    new_item(
        data,
        username, service, 
        'tracks', track_id
    )

def get_track(
        username: str,
        service: str,
        track_id: str
    ) -> dict:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return get_item(
        username, service, 
        'tracks', track_id
    )

def delete_track(
        username: str,
        service: str,
        track_id: str
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete_item(
        username, service,
        'tracks', track_id
    )

#// Loops /////////////////////////////////////////////////////////////////////

@modify
def new_loop(
        users: dict,
        username: str,
        service: str,
        track_id: str,
        name:str
    ) -> None:
    """
    

    Parameters
    ----------
    users : dict
        DESCRIPTION.
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    path = '/'.join([
        username, service, 
        'tracks', track_id, 
        'loops', name
    ])
    post(users, path, listType=True)

def get_loop(
        username: str,
        service: str,
        track_id: str,
        name: str
    ) -> list:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    list
        DESCRIPTION.

    """
    return get_item(
        username, service,
        'tracks', track_id,
        'loops', name
    )

def delete_loop(
        username: str,
        service: str,
        track_id: str,
        name: str
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete_item(
        username, service,
        'tracks', track_id,
        'loops', name
    )


@modify
def add_loop_time(
        users: dict,
        username: str,
        service: str,
        track_id: str,
        name: str,
        start : str = '',
        end   : str = '',
        reps  : int = 1,
        index : int = -1
    ) -> None:
    """
    

    Parameters
    ----------
    users : dict
        DESCRIPTION.
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    start : str, optional
        DESCRIPTION. The default is ''.
    end : str, optional
        DESCRIPTION. The default is ''.
    reps : int, optional
        DESCRIPTION. The default is 1.
    index : int, optional
        DESCRIPTION. The default is -1.

    Returns
    -------
    None
        DESCRIPTION.

    """
    if not (start or end):
        return
    start = start or '0:00'
    end   = end or end_to_time(username, service, track_id)
    if index < 0:
        loops = get_item(
            username, service,
            'tracks', track_id,
            'loops', name
        )
        index = len(loops)
    data = {
        'start':start,
        'end':end,
        'reps':reps
    }
    path = '/'.join([
        username, service,
        'tracks', track_id,
        'loops', name, index
    ])
    put(users, path, data)

def get_loop_time(
        username: str,
        service: str,
        track_id: str,
        name: str,
        index: int = -1
    ) -> dict:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    index : int, optional
        DESCRIPTION. The default is -1.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return get_item(
        username, service, 
        'tracks', track_id, 
        'loops', name, index
    )

def remove_loop_time(
        username: str,
        service: str,
        track_id: str,
        name: str,
        index: int = -1
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    index : int, optional
        DESCRIPTION. The default is -1.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete_item(
        username, service,
        'tracks', track_id,
        'loops', name, index
    )

#// Skip Helper Functions /////////////////////////////////////////////////////

def merged_intervals(
        skips: list[tuple(int, int)]
    ) -> list[tuple(int, int)]:
    """
    

    Parameters
    ----------
    skips : list[tuple(int, int)]
        DESCRIPTION.

    Returns
    -------
    list[tuple(int, int)]
        DESCRIPTION.

    """
    m = [] 
    s = max_val = -1
    for a in sorted(skips, key = lambda x: x[0]):
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

def times_to_intervals(
        times : list[dict[str:str]]
    ) -> list[tuple(int, int)]:
    """
    

    Parameters
    ----------
    times : list[dict[str:str]]
        DESCRIPTION.

    Returns
    -------
    list[tuple(int, int)]
        DESCRIPTION.

    """
    return merged_intervals([
        (time_to_ms(time['start']), time_to_ms(time['end'])
        ) for time in times]
    )

#// Skips /////////////////////////////////////////////////////////////////////

def new_skip(
        username: str,
        service: str,
        track_id: str,
        name:str,
        always: bool = False
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    always : bool, optional
        DESCRIPTION. The default is False.

    Returns
    -------
    None
        DESCRIPTION.

    """
    data = {
        'times':[],
        'always':always
    }
    new_item(
        data,
        username, service,
        'tracks', track_id,
        'skips', name
    )

def get_skip(
        username: str,
        service: str,
        track_id: str,
        name:str
    ) -> dict:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return get_item(
        username, service,
        'tracks', track_id,
        'skips', name
    )

def delete_skip(username: str,
        service: str,
        track_id: str,
        name:str
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete(
        username, service,
        'tracks', track_id,
        'skips', name
    )


@modify
def new_skip_time(
        users: dict,
        username: str,
        service: str,
        track_id: str,
        name: str,
        start : str  = '',
        end   : str  = '',
        index : int  = -1
    ) -> None:
    """
    

    Parameters
    ----------
    users : dict
        DESCRIPTION.
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    start : str, optional
        DESCRIPTION. The default is ''.
    end : str, optional
        DESCRIPTION. The default is ''.
    index : int, optional
        DESCRIPTION. The default is -1.

    Returns
    -------
    None
        DESCRIPTION.

    """
    start = start or '0:00'
    end   = end or end_to_time(username, service, track_id)
    if index < 0:
        skips = get_item(
            username, service, 
            'tracks', track_id, 
            'skips', name, 'times'
        )
        index = len(skips)
    data = {
        'start':start,
        'end':end
    }
    path = '/'.join([
        username, service, 
        'tracks', track_id, 
        'skips', name, 'times', index
    ])
    put(users, path, data)

def get_skip_time(
        username: str,
        service: str,
        track_id: str,
        name: str,
        index : int  = -1
    ) -> dict:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    index : int, optional
        DESCRIPTION. The default is -1.

    Returns
    -------
    dict
        DESCRIPTION.

    """
    return get_item(
        username, service, 
        'tracks', track_id, 
        'skips', name, 'times', index
    )

def delete_skip_time(
        username: str,
        service: str,
        track_id: str,
        name: str,
        index : int  = -1
    ) -> None:
    """
    

    Parameters
    ----------
    username : str
        DESCRIPTION.
    service : str
        DESCRIPTION.
    track_id : str
        DESCRIPTION.
    name : str
        DESCRIPTION.
    index : int, optional
        DESCRIPTION. The default is -1.

    Returns
    -------
    None
        DESCRIPTION.

    """
    delete_item(
        username, service, 
        'tracks', track_id, 
        'skips', name, 'times', index
    )

#// Mixes /////////////////////////////////////////////////////////////////////

# TODO: Define mixes

#// Play Functions ////////////////////////////////////////////////////////////

# TODO: Define play functions

# track
### clean
### w/ loops
### w/ skips
# pause
# mix


