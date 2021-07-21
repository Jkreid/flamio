# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 22:52:05 2021

@author: justi
"""

import os
import json

from user import User
from player import SpotifyPlayer


class LocalUser(User):
    
    DATA_PATH = '.'
    
    def __init__(self, username, *args, player=None, **kwargs):
        super().__init__(username, *args, **kwargs)
        self.player = player or SpotifyPlayer(username)
    
    def save(self):
        if not os.path.exists(self.DATA_PATH):
            os.mkdir(self.DATA_PATH)
        SAVE_PATH = self.DATA_PATH + f'/{self.username}.json'
        if self.info:
            with open(SAVE_PATH, 'w') as f:
                json.dump(self.info, f)
    
    def load(self):
        info = {'meta':{}, 'tracks':{}, 'mixes':{}, 'tags':{}}
        if os.path.exists(self.DATA_PATH):
            SAVE_PATH = self.DATA_PATH + f'/{self.username}.json'
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, 'r') as data:
                    info = json.load(data)
        self.info = info
    
    def pre_method(self):
        self.load()
    
    def aft_method(self):
        self.save()
    
    def play_track(self, track_id, loop_names=[], skip_names=[], reps=1,
                   include_always=True, **kwargs):
        track_info = self.get_track_play_info(
            track_id, 
            loop_names=loop_names,
            skip_names=skip_names, 
            include_always=include_always
        )
        self.player.play_track(track_id, track_info, track_reps=reps, **kwargs)
    
    def play_mix(self, name, reps=1, include_always=True, **kwargs):
        mix_info = self.get_mix_play_info(name, include_always=include_always)
        self.player.play_mix(mix_info, mix_reps=reps, **kwargs)
    
    
    