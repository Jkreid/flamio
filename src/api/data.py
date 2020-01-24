# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 15:43:06 2019

@author: justi

"""
import os
import json
import time as t
import spotipy_master.spotipy.util as util
from spotipy_master.spotipy.client import SpotifyException

PATH = '.'
FILENAME = '/users.json'
AUTHS = {
         'spotify':{
                    'redirect_uri':'http://localhost:8888/lab',
                    'client_id':'cd33a00276a645f393445c438115b958',
                    'client_secret':'b9988db76d074442aa81a37312d12d29',
                    'scope':'streaming \
                             user-read-playback-state \
                             user-modify-playback-state \
                             user-read-currently-playing'
                   },
         'soundcloud':{},
         'apple_music':{}
        }


def untitled(obj):
    num = 1
    names = list(obj.keys())
    untitleds = list(filter(lambda n: 'untitled' in n, names))
    while 'untitled {}'.format(num) in untitleds:
        num += 1
    return 'untitled {}'.format(num)


def load():
    """ Load users dictonary from json file if the file exists
        If non-existant, return base dictonary """
    try:
        with open('{}/{}'.format(PATH, FILENAME), 'r') as u:
            users = json.load(u)
        return users
    except FileNotFoundError as e:
        print('Data file {} not found'.format(e.filename))
        return {'__base__':{}}


def save(users=None, user=None):
    """ Write users dictionary to json file """
    users = users or load()
    if users:
        if not os.path.exists(PATH):
            os.mkdir(PATH)
        if user:
            users[user['name']] = user
        with open(PATH + FILENAME, 'w') as u:
            json.dump(users, u)
    else:
        print('No user data to be saved')
    return users,user


def get(username, 
        service, 
        dtype, 
        users=None,
        name=None, 
        track_id=None):
    """ Get item from users dictionary """
    try:
        if dtype == 'token':
            return util.prompt_for_user_token(username=username, 
                                              **AUTHS[service])
        users = users or load()
        if dtype == 'user':
            return users[username][service]
        elif dtype == 'mix':
            return users[username][service]['mix'][name]
        else:
            return users[username][service]['track'][track_id][dtype][name]
    except KeyError as e:
        raise NameError('Item {} not found'.format(e))


def create(username, 
           service=None,
           dtype=None,
           users=None, 
           name=None, 
           track_id=None,
           service_username=None):
    #body
    users = users or load()
    user = {'name':username} if username not in users else users[username]
    if service:
        if service in ['spotify']:#, 'soundcloud', 'apple_music']:
            if service not in users:
                tokenLifetime = {'spotify':3600, 
                                 'soundcloud':1200, 
                                 'apple_music':1200
                                 }
                try:
                    login_time = t.time()
                    token = get(service_username, service, 'token')
                    user[service] = {'login_time':login_time,
                                     'username':service_username,
                                     'token_lifetime':tokenLifetime[service],
                                     'token':token,
                                     'track':{},
                                     'mix':{},
                                     }
                except SpotifyException:
                    print('{} account with username {} does not exist or does\
                          not have proper permissions')
            if track_id:
                if track_id not in user[service]['track']:
                    user[service]['track'][track_id] = {'loop':{},
                                                        'skip':{}
                                                        }
                if dtype == 'loop':
                    name = name or untitled(user[service]['track'][track_id][dtype])
                    user[service]['track'][track_id][dtype][name] = {'intervals':[],
                                                                     'reps':[]
                                                                     }
                elif dtype == 'skip':
                    name = name or untitled(user[service]['track'][track_id][dtype])
                    user[service]['track'][track_id][dtype][name] = {'intervals':[],
                                                                     'always':[]
                                                                     }
            elif dtype == 'mix':
                name = name or untitled(user[service]['mix'])
                user[service][dtype][name] = []
    
    return save(users, user)


def delete():
    pass


def add():
    pass


def remove():
    pass


def rename():
    pass


def edit():
    pass


def change_reps():
    pass


def change_always_flag():
    pass


