# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 21:55:54 2019

@author: justi
"""

import os
import sys
sys.path.insert(1, os.path.realpath('../'))
import spotipy_master.spotipy as spotipy
import spotipy.util as util
import src.api.utils.flamio as flamio
# =============================================================================
# import src.api as api
# import src.api.utils.select as select
# import src.api.utils.search as search
# import src.api.loopify as loopify
# import src.api.playlist as playlist
# import src.api.stremix as stremix
# =============================================================================

USERNAME = {'flamio':'jr', 'spotify':'12125880630', 'soundcloud':'', 'apple_music':''}
path='./test_data'



def test_spotify():
    
    token = util.prompt_for_user_token(username=USERNAME['spotify'], 
                                       **{
                                        'redirect_uri':'http://localhost:8888/lab',
                                        'client_id':'cd33a00276a645f393445c438115b958',
                                        'client_secret':'b9988db76d074442aa81a37312d12d29',
                                        'scope':'streaming \
                                                 user-read-playback-state \
                                                 user-modify-playback-state \
                                                 user-read-currently-playing'
                                         }
                                       )
    username=spotipy.Spotify(auth=token).me()['id']
    
    assert username == USERNAME['spotify']


def test_soundcloud():
    pass


def test_apple_music():
    pass


def test_new_user_spotify():
    
    flamio.new_user_and_service(path=path, username=USERNAME['flamio'], service='spotify', service_un=USERNAME['spotify'])

    assert USERNAME['flamio'] in flamio.get_users(path)
    assert USERNAME['spotify'] in flamio.get_users(path)[USERNAME['flamio']]['spotify']['username']
    

def test_new_loop():
    pass


def test_new_skip():
    pass


def test_new_playlist():
    pass


def test_new_stremix():
    pass


def test_delete_user():
    pass
    

def test_delete_loop():
    pass


def test_delete_skip():
    pass


def test_delete_playlist():
    pass


def test_delete_stremix():
    pass


def test_rename_loop():
    pass


def test_rename_skip():
    pass


def test_rename_playlist():
    pass


def test_rename_stremix():
    pass