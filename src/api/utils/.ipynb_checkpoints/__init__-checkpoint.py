# -*- coding: utf-8 -*-
"""
Created on Fri Nov  1 17:15:38 2019

@author: justi

API utils
"""

import os
import json
import spotipy
import time as t

# =============================================================================
# Streaming Service App Global Variables
# =============================================================================
AUTHENICATORS = {
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

# =============================================================================
# Functions
# =============================================================================

def get_users(path):
    # get w/ input
    path +='/users.json'
    if os.path.exist(path):
        with open(path, 'r') as d:
            users = json.load(d)
        return users
    return {}

def get_user(username, 
             service, 
             users={}, 
             path='.'):
    # get w/ input
    users = users or get_users(path)
    if users:
        if username in users[username]:
            return users[username][service]
    return {}


def save(users, path='.'):
    # update
    if users:
        with open(path, 'w') as f:
            json.dump(users, f)

def new_user(username, 
             users={}, 
             path='.'):
    # update
    users = users or get_users(path)
    users[username] = {
                       'name':username, 
                       'spotify':{}, 
                       'soundcloud':{}, 
                       'apple_music':{}
                      }
    save(users, path=path)


def get_token(service,
              s_username):
    # get w/ input
    if service == 'spotify':
        token = spotipy.util.prompt_for_user_token(username=s_username,
                                                   **AUTHENICATORS[service])
    elif service == 'soundcloud':
        token = None
    elif service == 'apple_music':
        token = None
    else:
        token = None
    return token


def refresh_token(username,
                  service,
                  users={},
                  path='.'):
    # update
    users = users or get_users(path)
    user = users[username][service]
    if t.time() - user['login_time'] > user['refresh']:
        user['login_time']  = t.time()
        user['token'] = get_token(service=service, username=user['username'])
        save(users=users, path=path)


def add_service(service_un,
                username, 
                service, 
                users={}, 
                path='.'):
    # update
    users = users or get_users(path)
    user = get_user(username=username, service=service, users=users)
    tokenLifetime = {'spotify':3600, 'soundcloud':1200, 'apple_music':1200}
    if not user:
        users = get_users(path=path, users=users)
        if service and (username in users):
            token = get_token(service=service, username=service_un)
            if token:
                users[username][service] = {
                                            'flamio_name':username,
                                            'service':service,
                                            'pauseKill':False,
                                            'login_time':t.time(),
                                            'refresh':tokenLifetime[service],
                                            'username':service_un,
                                            'token':token,
                                            'loops':{},
                                            'skips':{},
                                            'playlists':{},
                                            'stremixes':{}
                                           }
                save(users=users, path=path)

def new_user_and_service(username,
                         service,
                         service_un,
                         users={},
                         path='.'):
    # update
    users = get_users(path)
    if username not in users:
        users[username] = {
                           'name':username, 
                           'spotify':{}, 
                           'soundcloud':{}, 
                           'apple_music':{}
                          }
        add_service(service_un, service, users=users, path=path)

def get_player(username, 
               service, 
               users={}, 
               path='.'):
    # get w/ input and update
    users = users or get_users(path)
    if username in users:
        if service in users[username]:
            user = users[username][service]
            refresh_token(username, service, users=users, path=path)
            if service == 'spotify':
                return spotipy.Spotify(auth=user['token'])
            elif service == 'soundcloud':
                pass
            elif service == 'apple_music':
                pass