# -*- coding: utf-8 -*-
"""
Created on Mon Nov 11 21:55:54 2019

@author: justi
"""

import sys
sys.path.insert(1, '/Users/justi/Documents/public_repos/flamio/src/api')

import utils
import utils.select as select
import utils.search as search
import loopify
import playlist
import stremix

# =============================================================================
# import spotipy
# import spotipy.util as util
# =============================================================================


# =============================================================================
# def test_import():
#     
#     sp = spotipy.Spotify(auth='BQA2FS5yEZZL8Pa0IUUZrXNNQ-W9Ia9Iz7vru2Y4glAQnZW95v8PoYWTNqoowwuJNR4A2GNyZCO5PIfpRk1SLt1rFtG4fuFxO8JHgIVGl7qxZrBmHQWKJCL2UzBbZ4CXAq2T_fYD9kY3CdRWaTm3TxcQVJ0VKgJ3xA')
# 
#     assert sp.current_playback() != None
# =============================================================================





# =============================================================================
# def test_import_util():
#     
#     token = spotipy.util.prompt_for_user_token(username='12125880630', **{
#                                                 'redirect_uri':'http://localhost:8888/lab',
#                                                 'client_id':'cd33a00276a645f393445c438115b958',
#                                                 'client_secret':'b9988db76d074442aa81a37312d12d29',
#                                                 'scope':'streaming \
#                                                          user-read-playback-state \
#                                                          user-modify-playback-state \
#                                                          user-read-currently-playing'
#                                                })
#     
#     assert token != None
# =============================================================================


def test_newUser():
    
    utils.flamio.new_user_and_service(username='jr', service='spotify', service_un='12125880630')
    
    assert 'jr' in utils.flamio.get_users('/Users/justi/Documents/public_repos/flamio/src')


def test_getUser():
    
    users=utils.flamio.get_users('/Users/justi/Documents/public_repos/flamio/src')
    
    assert 'jr' in users

def test_getPlayer():
    
    users=utils.flamio.get_users('/Users/justi/Documents/public_repos/flamio/src')
    player = utils.flamio.get_player(username='jr',service='spotify',users=users)
    
    assert player.current_playback() != None

def test_get_song_id():
    
    songid = select.from_search('jr','spotify','full bloom',field='track')
    
    assert songid != None
