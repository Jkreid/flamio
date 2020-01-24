# -*- coding: utf-8 -*-
"""
Created on Mon Dec  2 21:44:29 2019

@author: justi
"""

import time as t
import spotipy_master.spotipy as spotipy
import spotipy_master.spotipy.util as util

# =============================================================================
# Streaming Service App Global Variables
# =============================================================================
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

# =============================================================================
# Functions
# =============================================================================


def get_token(user):
    service = user['service']
    if service == 'spotify':
        return util.prompt_for_user_token(username=user['username'], **AUTHS[service])


def get_player(user):
    service = user['service']
    if service == 'spotify':
        player = spotipy.Spotify(auth=user['token'])
        try:
            player.me()
            return player
        except:
            token = get_token(user)
            user['token'] = token
            return spotipy.Spotify(auth=token)


# =============================================================================
# Client Wrapper
# =============================================================================
# Client Objects from streaming services and Flamio Client Object are parents of the client wrapper