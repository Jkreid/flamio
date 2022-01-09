# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 20:31:15 2021

@author: justi
"""
import asyncio
import time as t


class Timer:

    def __init__(self, lock=None, debug=False):
        self._start_time = 0
        self._end_time = 0
        self.lock = lock or asyncio.Lock()
        self.debug = debug


    def start_clock(self, duration):
        self._start_time = t.time()
        self._end_time = self._start_time + duration
        self.duration = duration


    @property
    def time_remaining(self):
        return self._end_time - t.time()


    def isExpired(self, time_left):
        return time_left <= 0


    def isPreStart(self, time_left):
        return round(time_left, 3) > self.duration


    def _outside_interval(self):
        time_left = self.time_remaining
        return self.isExpired(time_left) or self.isPreStart(time_left)


    async def outside_interval(self):
        return self._outside_interval()


    async def rewind(self, seconds):
        async with self.lock:
            self._end_time += seconds


    async def run(self, duration):
        while not await asyncio.ensure_future(self.outside_interval()):
            if self.debug:
                print(self.time_remaining)
        if self.debug:
            print('clock done')



def checker(method):
    async def checker_method(lm, *args, period=0, **kwargs):
        while not lm.closed:
            await asyncio.ensure_future(method(lm, *args, **kwargs))
            await asyncio.sleep(period)
    return checker_method


def get_or_create_eventloop():
    try:
        return asyncio.get_event_loop()
    except RuntimeError as e:
        if "There is no current event loop in thread" in str(e):
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            return asyncio.get_event_loop()


class Looper:

    def __init__(self, player, loop=None, lock=None, clock=None, 
                 killOnPause=False, device=None, debug=False):
        self.player = player
        self.stop = False
        self.closed = True
        self.playback = {}
        self.interval = (0, 0)
        self.device = None
        self.loop = loop or get_or_create_eventloop()
        self.lock = lock or asyncio.Lock()
        self.clock = clock or Timer(self.lock, debug=debug)
        self.killOnPause = killOnPause
        self.debug = debug


    def loop_stop(self, *args):
        if self.debug:
            print('stoping loop')
        self.stop = True
        return args


    @property
    def playing(self):
        return self.playback['is_playing']


    @property
    def progress(self):
        return (self.playback['progress_ms'] + (int(
            1000*(t.time() - self.playback_time)
        ) if self.playing else 0)) if self.valid_playback else -1


    @checker
    async def calibrate_clock(self):
        if self.debug:
            print('calibrating')
        await asyncio.ensure_future(
            self.clock.rewind(
                (self.interval[1] - self.progress)/1000
                - self.clock.time_remaining
            )
        )


    @checker
    async def status(self):
        if self.stop:
            if self.debug:
                print('really stopping loop')
            self.closed = True
            await asyncio.sleep(0)
            self.loop.stop()


    def _set_playback(self, playback):
        self.playback = playback
        self.valid_playback = self.playback and self.playback['item']
        self.playback_time = t.time()


    @checker
    async def set_playback(self):
        if self.debug:
            print('setting playing')
        playback = self.player.current_playback()
        async with self.lock:
            self._set_playback(playback)


    @checker
    async def set_playback_aiohttp(self, new_player):
        playback = await asyncio.ensure_future(new_player.current_playback())
        async with self.lock:
            self._set_playback(playback)


    @checker
    async def isValidTrack(self, track_id):
        if self.valid_playback and self.playback['item']['id'] == track_id:
            if self.debug:
                print('valid track check')
        else:
            if self.debug:
                print('invalid track check')
            self.loop_stop()


    @checker
    async def isPlaying(self):
        if self.debug:
            print('pause check')
        if not self.playback['is_playing']:
            if self.debug:
                print('Paused')
            self.loop_stop()


    @checker
    async def pausedOutsideLoop(self):
        if not self.playback['is_playing']:
            s, e = self.interval
            if not (s <= self.progress <= e):
                if self.debug:
                    print('Paused Outside Loop')
                self.loop_stop()


    @checker
    async def inInterval(self):
        if self.debug:
            print('interval check')
        s, e = self.interval
        prog = self.progress
        if not (s <= prog <= e) and self.debug:
            print(f'Position {prog} out of Interval: {s}, {e}')


    @checker
    async def skip(self, start, end):
        if self.debug:
            print('skip check')
        if (start <= self.progress <= end):
            self.player.seek_track(end)
            self._set_playback(self.player.current_playback())
    
    # async def play_interval(self):
    #     duration = (self.interval[1] - self.interval[0]) / 1000
    #     for r in range(reps):
    #         if not (i or k or r or tr):
    #             if not (
    #                 self.playback
    #                 and self.playback['is_playing']
    #                 and track_id == self.playback['item']['id']
    #                     ):
    #                 self.player.start_playback(
    #                     track_id, 
    #                     device=self.device
    #                 )
    #         if start_ms or i or r or tr or k:
    #             async with self.lock:
    #                 self.player.seek_track(start_ms)
    #                 self._set_playback(
    #                     self.player.current_playback()
    #                 )
    #         not_last_loop = ((i < loop_reps - 1)
    #                             or (k < len(loop_info) - 1)
    #                             or (r < reps - 1)
    #                             or (tr < track_reps - 1)
    #                             )
    #         if not_last_loop or await_last_loop:
    #             if self.debug:
    #                 print(f'loop sleeping for {duration} secs')
    #             self.clock.start_clock(duration)
    #             await asyncio.ensure_future(
    #                 self.clock.run(duration)
    #             )


    async def play(self, track_id, track_loops_info, track_reps,
                   await_last_loop=True):

        self.playback = self.player.current_playback()

        for tr in range(track_reps):
            for loop_info, loop_reps in track_loops_info: 
                for i in range(loop_reps):
                    for k, (start_ms, end_ms, reps) in enumerate(loop_info):
                        async with self.lock:
                            self.interval = (start_ms, end_ms)
                        
                        duration = (self.interval[1] - self.interval[0]) / 1000
                        for r in range(reps):
                            if not (i or k or r or tr):
                                if not (
                                    self.playback
                                    and self.playback['is_playing']
                                    and track_id == self.playback['item']['id']
                                        ):
                                    self.player.start_playback(
                                        track_id, 
                                        device=self.device
                                    )
                            if start_ms or i or r or tr or k:
                                async with self.lock:
                                    self.player.seek_track(start_ms)
                                    self._set_playback(
                                        self.player.current_playback()
                                    )
                            not_last_loop = ((i < loop_reps - 1)
                                             or (k < len(loop_info) - 1)
                                             or (r < reps - 1)
                                             or (tr < track_reps - 1)
                                             )
                            if not_last_loop or await_last_loop:
                                if self.debug:
                                    print(f'loop sleeping for {duration} secs')
                                self.clock.start_clock(duration)
                                await asyncio.ensure_future(
                                    self.clock.run(duration)
                                )
        
        if self.debug:
            print('end of loop')
        self.loop_stop()


    def run_loop(self):
        try:
            asyncio.ensure_future(self.status())
            self.closed = False
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.closed = True


    def play_loop(self, track_id, track_info, track_reps=1,
                  playback_period=1, await_last_loop=True):
        loop_info, skip_zones, _ = track_info
        asyncio.ensure_future(self.play(
            track_id, loop_info, track_reps, await_last_loop=await_last_loop
        ))
        asyncio.ensure_future(
            self.set_playback(period=playback_period)
        )
        if self.killOnPause:
            asyncio.ensure_future(self.isPlaying())
        asyncio.ensure_future(self.calibrate_clock())
        asyncio.ensure_future(self.inInterval())
        for start, end in skip_zones:
            asyncio.ensure_future(self.skip(start, end))
        asyncio.ensure_future(self.pausedOutsideLoop())
        asyncio.ensure_future(self.isValidTrack(track_id))
        self.run_loop()


def play_track(player, track_id, track_info, track_reps=1, playback_period=1, 
               await_last_loop=True, loop=None, lock=None, clock=None, 
               killOnPause=False, device=None, debug=False):
    Looper(
        player, loop=loop, lock=lock, clock=clock, killOnPause=killOnPause,
        device=device, debug=debug
    ).play_loop(
        track_id, track_info, track_reps=track_reps,
        playback_period=playback_period, await_last_loop=await_last_loop
    )


def play_item(looper, item, playback_period=1):
    if len(item) == 3:
        track_id, track_info, track_reps = item
        looper.play_loop(
            track_id, track_info, track_reps=track_reps,
            playback_period=playback_period
        )
    elif len(item) == 1 and isinstance(item[0], (float, int)):
        looper.player.pause(item[0])
    else:
        raise ValueError('Invalid object for playing')


def play_mix(player, mix_info, mix_reps=1, playback_period=1, loop=None, 
             lock=None, killOnPause=False, device=None, debug=False):
    looper = Looper(
        player, loop=loop, lock=lock, killOnPause=killOnPause, device=device, 
        debug=debug
    )
    for _ in range(mix_reps):
        for item in mix_info:
            play_item(looper, item, playback_period=playback_period)

