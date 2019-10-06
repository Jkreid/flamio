# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 00:03:21 2019

@author: justi

Flamio - User
"""

import os
import spotipy
import spotipy.util as util
import time as t

APP_ID='cd33a00276a645f393445c438115b958'
SECRET='b9988db76d074442aa81a37312d12d29'
REDIRECT='http://localhost:8888/lab'
SCOPES='streaming \
        user-read-playback-state \
        user-modify-playback-state \
        user-read-currently-playing'

class User:
    
    def __init__(self, 
                 spotify_username, 
                 app_password=None, 
                 confirm_password=None):
        """ Initialize new user instance w/ username and password """
        self.un=spotify_username
        # request new password in None given
        app_pw = app_password or hash(input('passowrd: '))
        pw_confirm = (confirm_password if app_password else None) or hash(input('confirm password: '))
        while app_pw != pw_confirm:
            print('passwords do not match\n')
            app_pw = hash(input('passowrd: '))
            pw_confirm = hash(input('confirm password: '))
        self.pw = app_pw
        # refresh user token and record login/last use time
        self.token_reqs = {'username':spotify_username,
                           'scope':SCOPES,
                           'client_id':APP_ID,
                           'client_secret':SECRET,
                           'redirect_uri':REDIRECT}
        self.login_time = t.time()
        self.token = util.promt_for_user_token(**self.token_reqs)
        self.spotify = spotipy.Spotify(auth=self.token)
        self.STAY_LOGGED_IN = True
        self.last_used = t.time()
        if not os.path.exists('../../data/users/{}.dat'.format(spotify_username)):
            with open('../../data/users/{}.dat'.format(spotify_username), 'w') as user_data:
                user_data.write('un:{}\npw:{}'.format(spotify_username,self.pw))
            
    
    def STAY_LOGGED_IN(self, state):
        """ Change auto login status """
        if hash(input('password: ')) == self.pw:
            self.STAY_LOGGED_IN = bool(state)
            self.last_used = t.time()
        else:
            print('incorrect password! No change made')
    
    
    def status(self): 
        """ Check token status and login / refresh token if expired """ 
        if t.time() - self.login_time > 3600:
            # request login if needed
            autologin = self.STAY_LOGGED_IN or (t.time() - self.last_used < 3600)
            attempt = self.pw if autologin else hash(input('password: '))
            while attempt != self.pw:
                if input('passwords do not match, retry? (y/n): ')[0].lower() == 'y':
                    attempt = hash(input('password: '))
                else:
                    return False # token expired and user locked out
            self.login_time = t.time()
            self.token = util.promt_for_user_token(**self.token_reqs)
            self.spotify = spotipy.Spotify(auth=self.token)
        return True # token not expired
    
    
    def request(self, action, **kwargs):
        """ Call a service request with username and spotipy object"""
        if self.status():
            action(self, **kwargs)
            self.last_used = t.time()



def new_user(username, password=None, confirm=None):
    """ Create new user object """
    return User(username, password, confirm)


def load_user(username, password):
    """ Load user object from saved data """
    if os.path.exists('../../data/users/{}.dat'.format(username)):
        with open('../../data/users/{}.dat'.format(username), 'r') as user:
            un,pw = user.readlines()
        attempt = hash(password)
        while attempt != pw:
            if input('passwords do not match, retry? (y/n) ')[0].lower() == 'y':
                attempt = hash(input('password: '))
            else:
                print('failed login')
                return False # token expired and user locked out
        return User(spotify_username=username,
                    app_password=pw,
                    confirm_password=pw)
    else:
        print('username not found')
        action = input('retry, create new user, or quit? (r/c/q) ') [0].lower()
        if action == 'r':
            un = input('username: ')
            pw = input('password: ')
            return load_user(un,pw)
        elif action == 'c':
            return new_user(username, password)
        else:
            print('quitting...')
            return False
