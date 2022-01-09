# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 22:52:05 2021

@author: justi
"""

import os
import json
import flamio

from user import User, flamio_method
from player import SpotifyPlayer


class LocalUser(User):
    
    DATA_PATH = '.'
    
    def __init__(self, username, *args, player=None, **kwargs):
        super().__init__(username, *args, **kwargs)
        # self.load()
        # SpotifyPlayer(username, token_info=self.get_token_info() or None)
        self.player = player or SpotifyPlayer(username)
    
    def save(self):
        if not os.path.exists(self.DATA_PATH):
            os.mkdir(self.DATA_PATH)
        SAVE_PATH = self.DATA_PATH + f'/{self.username}.json'
        if self.info:
            with open(SAVE_PATH, 'w') as f:
                json.dump(self.info, f)
    
    def load(self):
        if os.path.exists(self.DATA_PATH):
            SAVE_PATH = self.DATA_PATH + f'/{self.username}.json'
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, 'r') as data:
                    self.info = json.load(data)
    
    def pre_method(self):
        self.load()
    
    def aft_method(self):
        # if self.player.token_refreshed: self._update_authorization(self.player.token_info)
        self.save()
    
    @flamio_method
    def play_track(self, track_id, loop_names=[], skip_names=[], reps=1,
                   include_always=True, **kwargs):
        self.player.play_track(
            track_id,
            self.get_track_play_info(
                track_id, 
                loop_names=loop_names,
                skip_names=skip_names, 
                include_always=include_always
            ),
            track_reps=reps,
            **kwargs
        )
    
    @flamio_method
    def play_mix(self, name, reps=1, include_always=True, **kwargs):
        self.player.play_mix(
            self.get_mix_play_info(
                name,
                include_always=include_always
            ),
            mix_reps=reps,
            **kwargs
        )
    
    @flamio_method
    def add_loop_time(self, track_id, *args, start='', end='', **kwargs):
        start = start or '0:00'
        end = end or self.player.end_to_time(track_id)
        flamio.add_loop_time(self.info, track_id, *args, start=start, end=end, **kwargs)
    
    @flamio_method
    def create_loop(self, track_id, *args, **kwargs):
        if track_id not in self.info['tracks']:
            self.create_track(track_id)
        flamio.create_loop(self.info, *args, **kwargs)
        
    @flamio_method
    def create_track(self, track_id, **kwargs):
        flamio.create_track(self.info, track_id, **kwargs)
        self.create_loop(track_id, '__FULL__')
        self.add_loop_time(track_id, '__FULL__')
    
    @flamio_method
    def add_current_track(self):
        self.create_track(self.player.current_track()['id'])