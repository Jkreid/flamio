# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 20:31:15 2021

@author: justi
"""
import asyncio
import time as t

import uuid
import flamio.utils as utils
# import flamio.play as play
import flamio.spotify as spotify
# import asyncio
# from flamio.player import Player

LAG_BUFFER = .2

class Clock:

    def __init__(self, debug=False):
        self._end_time = 0
        self.broken = False
        self.debug = debug

    def start_clock(self, duration):
        self._end_time = t.time() + duration
        self.duration = duration
        self.broken = False

    @property
    def time_remaining(self):
        return self._end_time - t.time()

    def _outside_interval(self):
        time_left = self.time_remaining
        return not (0 < round(time_left, 3) <= self.duration)
    
    def rewind(self, seconds):
        self._end_time += seconds

    async def run(self):
        while not (self.broken or self._outside_interval()):
            await asyncio.sleep(0)
            if self.debug:
                print(self.time_remaining)
        self.broken = True
        if self.debug:
            print('clock done')


def loopcheck(debug_msg):
    def checker(method):
        async def checker_method(looper, *args, period=0, delay=2, **kwargs):
            await asyncio.sleep(delay)
            while not looper.closed:
                if looper.debug:
                    print(debug_msg)
                await method(looper, *args, **kwargs)
                await asyncio.sleep(period)
        return checker_method
    return checker





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
        self.looper: Loop = looper or self.get_looper(
            playback_period=playback_period,
            killOnPause=killOnPause,
            device=device,
            debug=debug
        )
        self.playing = False
    
    def get_looper(self, playback_period=1, killOnPause=False, device='', debug=False):
        return Loop(
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
        await self.looper.play(
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
        self.looper = Loop(
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



class Loop:

    def __init__(self, player: Player, playback_period: float=1,
                 killOnPause: bool=False, device: str='', debug: bool=False):
        self.player = player
        self.clock = Clock(debug=debug)
        self.closed = True
        self.playback = {}
        self.playback_period = playback_period
        self.delay = playback_period + LAG_BUFFER
        self.interval = (0, 0)
        self.device = device
        self.killOnPause = killOnPause
        self.debug: bool = debug

    def loop_stop(self, reason: str):
        self.clock.broken = True
        self.closed = True
        if self.debug:
            print(f'stoping loop: {reason}')

    @property
    def playing(self):
        return ('is_playing' in self.playback) and self.playback['is_playing']


    @property
    def progress(self):
        return (self.playback['progress_ms'] + (int(
            1000*(t.time() - self.playback_time)
        ) if self.playing else 0)) if self.valid_playback else -1
    
    @property
    def prog_in_interval(self):
        s, e = self.interval
        return s <= self.progress < e
    
    @property
    def playback(self):
        return self._playback
    
    @playback.setter
    def playback(self, value):
        self._playback = value
        self.playback_time = t.time()
    
    @property
    def valid_playback(self):
        return 'item' in self.playback

    @loopcheck('calibrating')
    async def calibrate_clock(self):
        self.clock.rewind(
            (self.interval[1] - self.progress)/1000
            - self.clock.time_remaining
        )

    @loopcheck('setting current playback')
    async def set_playback(self):
        self.playback = await self.player.get_currently_playing()

    @loopcheck('valid track check')
    async def isValidTrack(self, track_id):
        playback_track_id = self.valid_playback and self.playback['item']['id']
        if not (playback_track_id and playback_track_id == track_id):
            self.loop_stop(f'invalid track {playback_track_id} not {track_id}')

    @loopcheck('pause check')
    async def isPlaying(self):
        if not self.playing:
            self.loop_stop('loop paused')

    @loopcheck('paused outside loop check')
    async def pausedOutsideLoop(self):
        if not self.playing:
            s, e = self.interval
            if not (s <= self.progress <= e):
                self.loop_stop('paused outside loop')

    @loopcheck('interval check')
    async def inInterval(self):
        s, e = self.interval
        prog = self.progress
        if not (s <= prog < e):
            print(f'Position {prog} out of Interval: {s}, {e}')

    @loopcheck('skip check')
    async def skip(self, start, end):
        if (start <= self.progress <= end):
            await self.player.seek_track(end)
            self.playback = await self.player.get_currently_playing()
    
    async def play_interval(self, i , k, r, tr, track_id, start_ms, duration):
        if not (i or k or r or tr):
            if (self.playback and self.playing
                and track_id == self.playback['item']['id']
                ):
                start, end = self.interval
                if not (start <= self.progress < end):
                    await self.player.seek_track(start_ms)
            else:
                await self.player.start_playback(
                    track_id, 
                    device=self.device,
                    position_ms=start_ms
                )
        else:
            await self.player.seek_track(start_ms)
        
        self.playback = await self.player.get_currently_playing()
        self.clock.start_clock(duration)
        await self.clock.run()

    async def play_loop(self, track_id, track_loops_info, track_reps):
        self.playback = await self.player.get_currently_playing()
        for tr in range(track_reps):
            for loop_info, loop_reps in track_loops_info: 
                for i in range(loop_reps):
                    for k, (start_ms, end_ms, reps) in enumerate(loop_info):
                        self.interval = (start_ms, end_ms)
                        duration = (self.interval[1] - self.interval[0]) / 1000
                        for r in range(reps):
                            await self.play_interval(i , k, r, tr, track_id, start_ms, duration)
        if self.debug:
            print('end of play loop')
        self.closed = True
    
    async def play(self, track_id, track_info, track_reps=1):
        loop_info, skip_zones, _ = track_info
        coros = []
        coros.append(self.play_loop(
            track_id, loop_info, track_reps
        ))
        coros.append(
            self.set_playback(period=self.playback_period)
        )
        coros.append(self.calibrate_clock(delay=self.delay))
        coros.append(self.isValidTrack(track_id, delay=self.delay))
        for start, end in skip_zones:
            coros.append(self.skip(start, end, delay=self.delay))
        
        coros.append(self.pausedOutsideLoop(delay=self.delay))
        if self.killOnPause:
            coros.append(self.isPlaying(delay=self.delay))
        if self.debug:
            coros.append(self.inInterval(delay=0))
        self.closed = False
        await asyncio.wait(coros)
        self.closed = True

