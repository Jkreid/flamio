# -*- coding: utf-8 -*-
"""
Created on Mon Jul 19 22:52:05 2021

@author: justi
"""

import os
import json

import aiohttp
import flamio.flamio as flamio

from flamio.user import User, flamio_method, async_flamio_method
from flamio.play import Player


class LocalUser(User):
    
    DATA_PATH = '.'
    
    def __init__(self, username, *args, player=None, refresh_token=None, load_player=False, load_data=True, **kwargs,):
        super().__init__(username, *args, **kwargs)
        if load_data:
            self.load()
        print(load_data)
        self.refresh_token = refresh_token
        print(self.refresh_token)
        print(self.info)
        if not refresh_token and 'refresh_token' in self.info['meta']:
            print('found refresh')
            self.refresh_token = self.info['meta']['refresh_token']
            print(self.refresh_token)
        if load_player:
            self.player = player or Player(refresh_token=self.refresh_token)
    
    def save(self):
        if not os.path.exists(self.DATA_PATH):
            os.mkdir(self.DATA_PATH)
        SAVE_PATH = self.DATA_PATH + f'/{self.username}.json'
        if self.info:
            with open(SAVE_PATH, 'w') as f:
                json.dump(self.info, f)
    
    def load(self):
        if os.path.exists(self.DATA_PATH):
            SAVE_PATH = self.DATA_PATH + f'/flamio/{self.username}.json'
            if os.path.exists(SAVE_PATH):
                with open(SAVE_PATH, 'r') as data:
                    self.info = json.load(data)
    
    def pre_method(self):
        self.load()
    
    def aft_method(self):
        self.save()
    
    async def async_player(self):
        async with aiohttp.ClientSession(trust_env=True) as session:
            await self.player.make_async_client(session)
            print(await self.player.async_current_playback())
    
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
    
    @async_flamio_method
    async def async_play_track(self, track_id, loop_names=[], skip_names=[], reps=1,
                   include_always=True, **kwargs):
        await self.player.async_play_track(
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