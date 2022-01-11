# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 11:31:40 2021

@author: justi
"""
import utils
import play
import spotify
import asyncio
import time


class Player:
    
    def __init__(self, code=None, refresh_token=None, session=None, is_async=False):
        if session and is_async:
            self.client = spotify.AsyncSpotifyAuthClient.create(
                session, code=code, refresh_token=refresh_token
            )
        else:
            self.client = spotify.SpotifyAuthClient(
            code=code, refresh_token=refresh_token
        )
        
    
    def play_track(self, *args, **kwargs):
        return play.play_track(self, *args, **kwargs)
    
    def play_item(self, *args, 
                  killOnPause=False, 
                  device=None, 
                  debug=False, 
                  **kwargs):
        return play.play_item(
            play.Looper(
                self, 
                killOnPause=killOnPause, 
                device=device, 
                debug=debug
            ),
            *args, 
            **kwargs
        )
    
    def play_mix(self, *args, **kwargs):
        return play.play_mix(self, *args, **kwargs)

    def current_playback(self):
        return spotify.current_playback(self.client)
    
    def start_playback(self, track_id, device=None, position_ms=0):
        return spotify.start_playback(self.client, track_id, device=device, position_ms=position_ms)
    
    def pause_playback(self, device=None):
        return spotify.pause_playback(self.client, device=device)
    
    def resume_playback(self, device=None):
        return spotify.resume_playback(self.client, device=device)
    
    def pause(self, duration=0, device=None, resume=False):
        self.pause_playback(device)
        if duration >= 0:
            time.sleep(duration)
            if resume:
                self.resume_playback(device)
    
    def seek_track(self, position_ms):
        return spotify.seek_track(self.client, position_ms)
    
    def current_track(self):
        return spotify.get_current_track(self.client)
    
    def devices(self):
        return spotify.get_devices(self.client)
    
    def current_device(self):
        return spotify.get_current_device(self.client)

    def end_to_ms(self, track_id):
        return spotify.end_to_ms(self.client, track_id)

    def end_to_time(self, track_id):
        return utils.ms_to_time(self.end_to_ms(track_id))
    
    async def async_current_playback(self):
        return await spotify.async_current_playback(self.client)
    
    async def async_start_playback(self, track_id, device=None, position_ms=0):
        return await spotify.async_start_playback(self.client, track_id, device=device, position_ms=position_ms)
    
    async def async_pause_playback(self, device=None):
        return await spotify.async_pause_playback(self.client, device=device)
    
    async def async_resume_playback(self, device=None):
        return await spotify.async_resume_playback(self.client, device=device)
    
    async def async_pause(self, duration=0, device=None, resume=False):
        await self.async_pause_playback(device)
        if duration >= 0:
            await asyncio.sleep(duration)
            if resume:
                await self.async_resume_playback(device)
    
    async def async_seek_track(self, position_ms):
        return await spotify.async_seek_track(self.client, position_ms)
    
    async def async_current_track(self):
        return await spotify.async_get_current_track(self.client)
    
    async def async_devices(self):
        return await spotify.async_get_devices(self.client)
    
    async def async_current_device(self):
        return await spotify.async_get_current_device(self.client)

    async def async_end_to_ms(self, track_id):
        return await spotify.async_end_to_ms(self.client, track_id)

    async def async_end_to_time(self, track_id):
        return utils.ms_to_time(await self.async_end_to_ms(track_id))