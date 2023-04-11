# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 11:31:40 2021

@author: justi
"""
import uuid
import flamio.utils as utils
import flamio.play as play
import flamio.spotify as spotify
import asyncio

class Player:
    
    def __init__(
        self, id: uuid.UUID, client: spotify.AsyncSpotifyAuthClient, looper=None,
        playback_period=1,
        killOnPause=False,
        device='',
        debug=False
    ):
        self.id = id
        self.client = client
        self.looper: play.Loop = looper or self.set_looper(
            playback_period=playback_period,
            killOnPause=killOnPause,
            device=device,
            debug=debug
        )
        self.playing = False
    
    def set_looper(self, playback_period=1, killOnPause=False, device='', debug=False):
        self.looper = play.Loop(
            self, 
            playback_period=playback_period,
            killOnPause=killOnPause,
            device=device,
            debug=debug
        )

    async def play_track(
        self, track_id, track_info, track_reps=1, playback_period=1,
        killOnPause=False, device='', debug=False
    ):
        self.playing = True
        await self.looper(
            self,
            playback_period=playback_period,
            killOnPause=killOnPause,
            device=device,
            debug=debug
        ).play(
            track_id, track_info, track_reps=track_reps
        )
        self.playing = False
    
    async def _play_item(self, item):
        if len(item) == 3:
            track_id, track_info, track_reps = item
            await self.looper.play(
                track_id, track_info, track_reps=track_reps
            )
        elif len(item) == 1 and isinstance(item[0], (float, int)):
            await self.pause(item[0])
        else:
            raise ValueError('Invalid object for playing')
    
    async def play_mix(
        self, mix_info, mix_reps=1, playback_period=1,
        killOnPause=False, device=None, debug=False
    ):
        self.playing = True
        self.looper(
            self, 
            playback_period=playback_period, 
            killOnPause=killOnPause, 
            device=device, 
            debug=debug
        )
        for _ in range(mix_reps):
            for item in mix_info:
                await self._play_item(item)
        self.playing = False
    
    async def get_currently_playing(self):
        return await spotify.async_get_currently_playing(self.client)
    
    async def get_current_track(self):
        return await spotify.async_get_current_track(self.client)
    
    async def get_current_track_id(self):
        return await spotify.async_get_current_track_id(self.client)

    async def get_current_playback(self):
        return await spotify.async_get_current_playback(self.client)
    
    async def start_playback(self, track_id, device='', position_ms=0):
        return await spotify.async_start_playback(self.client, track_id, device=device, position_ms=position_ms)
    
    async def pause_playback(self, device=''):
        return await spotify.async_pause_playback(self.client, device=device)
    
    async def resume_playback(self, device=''):
        return await spotify.async_resume_playback(self.client, device=device)
    
    async def pause(self, duration=0, device='', resume=False):
        await self.pause_playback(device)
        if duration >= 0:
            await asyncio.sleep(duration)
            if resume:
                await self.resume_playback(device)
    
    async def seek_track(self, position_ms):
        return await spotify.async_seek_track(self.client, position_ms)
    
    async def get_devices(self):
        return await spotify.async_get_devices(self.client)
    
    async def get_current_device(self):
        return await spotify.async_get_current_device(self.client)

    async def end_to_ms(self, track_id):
        return await spotify.async_end_to_ms(self.client, track_id)

    async def end_to_time(self, track_id):
        return utils.ms_to_time(await self.end_to_ms(track_id))