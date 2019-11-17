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
# import src.api.utils.select as select
# import src.api.utils.search as search
# import src.api.loopify as loopify
# import src.api.playlist as playlist
# import src.api.stremix as stremix
# import src.api as api
# =============================================================================

def test_spotify():
    
    token = util.prompt_for_user_token(username='12125880630', 
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
    
    assert username == '12125880630'


def test_newUser():
    
    flamio.new_user_and_service(username='jr', service='spotify', service_un='12125880630')

    assert 'jr' in flamio.get_users('/Users/justi/Documents/public_repos/flamio/src')


def test_getUser():
    
    users=flamio.get_users('/Users/justi/Documents/public_repos/flamio/src')
    
    assert 'jr' in users

def test_getPlayer():
    
    player = flamio.get_player(username='jr',service='spotify')
    
    assert player.me()['id'] == '12125880630'
