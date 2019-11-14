# -*- coding: utf-8 -*-
"""
Created on Mon Sep 30 00:03:21 2019

@author: justi

Flamio - User
"""

import os
import spotipy
import time as t
import json

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
                 confirm_password=None,
                 user_data=None,
                 persist=False):
        """ Initialize new user instance w/ username and password """
        self.un=spotify_username
        # request new password in None given
        app_pw = app_password or input('passowrd: ')
        pw_confirm = confirm_password or input('confirm password: ')
        while app_pw and app_pw != pw_confirm:
            print('passwords do not match\n')
            app_pw =input('passowrd: ')
            pw_confirm = input('confirm password: ')
        self.pw = app_pw
        # refresh user token and record login/last use time
        self.token_reqs = {'username':spotify_username,
                           'scope':SCOPES,
                           'client_id':APP_ID,
                           'client_secret':SECRET,
                           'redirect_uri':REDIRECT}
        self.login_time = t.time()
        self.token = spotipy.util.prompt_for_user_token(**self.token_reqs)
        self.spotify = spotipy.Spotify(auth=self.token)
        self.STAY_LOGGED_IN = True
        self.persist_through_pause = user_data['persist'] if user_data else persist
        self.data = user_data or {'name':spotify_username, 
                                 'pw':self.pw,
                                 'tlogin':self.login_time, 
                                 'persist':self.persist_through_pause,
                                 'loops':{}, 
                                 'skips':{}, 
                                 'playlists':{}
                                 }
        self.data_path = '../src/app/data/{}.json'.format(spotify_username)
        self.save_data()
                           
    
    def STAY_LOGGED_IN(self, state):
        """ Change auto login status """
        if input('password: ') == self.pw:
            self.STAY_LOGGED_IN = bool(state)
        else:
            print('incorrect password! No change made')
    
    
    def save_data(self):
        if os.path.exists(self.data_path):
            os.remove(self.data_path)
        with open(self.data_path,'w') as d:
            json.dump(self.data,d)
    
    
    def status(self): 
        """ Check token status and login / refresh token if expired """ 
        if t.time() - self.login_time > 3600:
            # request login if needed
            attempt = self.pw if self.STAY_LOGGED_IN else input('password: ')
            while attempt != self.pw:
                retry=input("passwords don't match, retry? (y/n): ")[0].lower()=='y'
                if retry:
                    attempt = input('password: ')
                else:
                    return False # token expired and user locked out
            self.login_time = t.time()
            self.token = spotipy.util.prompt_for_user_token(**self.token_reqs)
            self.spotify = spotipy.Spotify(auth=self.token)
            self.save_data()
        return True # token not expired
    
    
    def sp(self):
        """ return active spotipy object """
        if self.status(): return self.spotify
    
    def request(self, action, **kwargs):
        """ make a request with the spotipy object"""
        if self.status(): return action(self.spotify, **kwargs)
          
    def call(self, action, **kwargs):
        """ make a user call to a service function """
        if self.status(): return action(self, **kwargs)



def new_user(username, password=None, confirm=None, persist=False):
    """ Create new user object """
    return User(username, app_password=password, confirm_password=confirm, persist=persist)


def load_user(username, password):
    """ Load user object from saved data """
    data_path = '../src/app/data/{}.json'.format(username)
    if os.path.exists(data_path):
        with open(data_path) as d:
            data = json.load(d)
        un,pw = data['name'],data['pw']
        attempt = password
        while attempt != pw:
            if input("passwords don't match, retry? (y/n) ")[0].lower() == 'y':
                attempt = input('password: ')
            else:
                print('failed login')
                return False # token expired and user locked out
        return User(spotify_username=username,
                    app_password=pw,
                    confirm_password=pw,
                    user_data=data)
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