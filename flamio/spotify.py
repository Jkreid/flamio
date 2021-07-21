# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 23:59:45 2021

@author: justi
"""

import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
#// Constants /////////////////////////////////////////////////////////////////

DATA_PATH = '.'

AUTH = {
    'redirect_uri'  : 'http://localhost:8888/lab',
    'client_id'     : 'CLIENT_ID',
    'client_secret' : 'CLIENT_SECRET',
    'scope'         : 'streaming \
                       user-read-playback-state \
                           user-modify-playback-state \
                               user-read-currently-playing'
}

tokenLifetime = 3600


#// Tokens and Players ////////////////////////////////////////////////////////

def prompt_for_user_token(username, scope=None, client_id = None,
        client_secret = None, redirect_uri = None, cache_path = None):

    """ Function taken & modified from the spotipy library """

    ''' prompts the user to login if necessary and returns
        the user token suitable for use with the spotipy.Spotify 
        constructor

        Parameters:

         - username - the Spotify username
         - scope - the desired scope of the request
         - client_id - the client id of your app
         - client_secret - the client secret of your app
         - redirect_uri - the redirect URI of your app
         - cache_path - path to location to save tokens

    '''

    cache_path = cache_path or ".cache-" + username
    sp_oauth = SpotifyOAuth(client_id, client_secret, redirect_uri, 
        scope=scope, cache_path=cache_path)

    # try to get a valid token for this user, from the cache,
    # if not in the cache, then create a new token (this will send
    # the user to a web page where they can authorize this app)

    token_info = sp_oauth.get_cached_token()

    if not token_info:
        print('''

            User authentication requires interaction with your
            web browser. Once you enter your credentials and
            give authorization, you will be redirected to
            a url.  Paste that url you were directed to to
            complete the authorization.

        ''')
        
        auth_url = sp_oauth.get_authorize_url()
        try:
            r = requests.get(auth_url)
            response = r.url
            code = sp_oauth.parse_response_code(response)
            token_info = sp_oauth.get_access_token(code)
        except Exception as e:
            print(e)
            try:
                import webbrowser
                webbrowser.open(auth_url)
                print("Opened %s in your browser" % auth_url)
            except:
                print("Please navigate here: %s" % auth_url)
    
            print()
            print()
            try:
                response = raw_input("Enter the URL you were redirected to: ")
            except NameError:
                response = input("Enter the URL you were redirected to: ")
            code = sp_oauth.parse_response_code(response)
            token_info = sp_oauth.get_access_token(code)
     
    # Auth'ed API request
    if token_info:
        return token_info['access_token']
    else:
        return None


def get_token(account_username: str):
    return prompt_for_user_token(
        account_username,
        **AUTH
    )

def get_player(token):
    return spotipy.Spotify(auth=token)

def token_checker(method):
    def player_method(player, *args, **kwargs):
        if not player._is_valid_token():
            player._refresh_token(token=get_token(player.username))
        try:
            value = method(player, *args, **kwargs)
        except spotipy.SpotifyException:
            player._refresh_token(token=get_token(player.username))
            value = method(player, *args, **kwargs)
        return value
    return player_method

#// Utils /////////////////////////////////////////////////////////////

def end_to_ms(
        player: spotipy.Spotify,
        track_id: str
    ) -> int:
    return int(player.track(track_id)['duration_ms'])

def get_current_track(player):
    return player.current_playback()['item']

def get_current_track_id(player):
    return get_current_track(player)['id']

def current_playback(player: spotipy.Spotify):
    return player.current_playback()

def seek_track(player, position_ms):
    player.seek_track(position_ms)

def pause_playback(player, device=None):
    player.pause_playback(device_id=device)

def get_devices(player):
    return player.devices()['devices']

def get_current_device(player):
    playback = player.current_playback()
    if playback:
        device = playback['device']
        return device
    else:
        return {}

def start_playback(player, track_id, device=None):
    player.start_playback(
        device_id=device,
        uris=[f'https://open.spotify.com/track/{track_id}']
    )

def resume_playback(player, device=None):
    player.start_playback(
        device_id=device,
    )

