# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 20:31:15 2021

@author: justi
"""
import asyncio
import time as t


class Timer:

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



def checker(method):
    async def checker_method(lm, *args, period=0, delay=2, **kwargs):
        await asyncio.sleep(delay)
        while not lm.closed:
            method(lm, *args, **kwargs)
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
        self.clock = clock or Timer(debug=debug)
        self.killOnPause = killOnPause
        self.debug = debug
        self.valid_playback = False


    def loop_stop(self, *args):
        if self.debug:
            print('stoping loop')
        self.stop = True
        self.clock.broken = True
        self.closed = True
        return args


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


    @checker
    def calibrate_clock(self):
        if self.debug:
            print('calibrating')
        self.clock.rewind(
            (self.interval[1] - self.progress)/1000
            - self.clock.time_remaining
        )


    @checker
    def status(self):
        if self.stop:
            if self.debug:
                print('really stopping loop')
            self.closed = True
            self.loop.stop()


    def _set_playback(self, playback):
        self.playback = playback
        self.valid_playback = self.playback and self.playback['item']
        self.playback_time = t.time()


    @checker
    def set_playback(self):
        if self.debug:
            print('setting playing')
        playback = self.player.current_playback()
        self._set_playback(playback)


    @checker
    def isValidTrack(self, track_id):
        if self.valid_playback and self.playback['item']['id'] == track_id:
            if self.debug:
                print('valid track check')
        else:
            if self.debug:
                print('invalid track check')
            self.loop_stop()


    @checker
    def isPlaying(self):
        if self.debug:
            print('pause check')
        if not self.playing:
            if self.debug:
                print('Paused')
            self.loop_stop()


    @checker
    def pausedOutsideLoop(self):
        if not self.playing:
            s, e = self.interval
            if not (s <= self.progress <= e):
                if self.debug:
                    print('Paused Outside Loop')
                self.loop_stop()


    @checker
    def inInterval(self):
        if self.debug:
            print('interval check')
        s, e = self.interval
        prog = self.progress
        if not (s <= prog < e) and self.debug:
            print(f'Position {prog} out of Interval: {s}, {e}')


    @checker
    def skip(self, start, end):
        if self.debug:
            print('skip check')
        if (start <= self.progress <= end):
            self.player.seek_track(end)
            self._set_playback(self.player.current_playback())
    
    async def play_interval(self, i , k, r, tr, track_id, start_ms, duration):
        if not (i or k or r or tr):
            if (self.playback and self.playing
                and track_id == self.playback['item']['id']
                ):
                start, end = self.interval
                if not (start <= self.progress < end):
                    self.player.seek_track(start_ms)
            else:
                self.player.start_playback(
                    track_id, 
                    device=self.device,
                    position_ms=start_ms
                )
        else:
            self.player.seek_track(start_ms)
        
        self._set_playback(
            self.player.current_playback()
        )
        self.clock.start_clock(duration)
        await self.clock.run()


    async def play(self, track_id, track_loops_info, track_reps, await_last_loop=False):

        self.playback = self.player.current_playback()

        for tr in range(track_reps):
            for loop_info, loop_reps in track_loops_info: 
                for i in range(loop_reps):
                    for k, (start_ms, end_ms, reps) in enumerate(loop_info):
                        self.interval = (start_ms, end_ms)
                        duration = (self.interval[1] - self.interval[0]) / 1000
                        for r in range(reps):
                            await self.play_interval(i , k, r, tr, track_id, start_ms, duration)
        if self.debug:
            print('end of loop')
        self.loop_stop()

    async def async_play(self, track_id, track_loops_info, track_reps):
        
        self.playback = self.player.current_playback()

        for tr in range(track_reps):
            for loop_info, loop_reps in track_loops_info: 
                for i in range(loop_reps):
                    for k, (start_ms, end_ms, reps) in enumerate(loop_info):
                        self.interval = (start_ms, end_ms)
                        duration = (self.interval[1] - self.interval[0]) / 1000
                        for r in range(reps):
                            await self.play_interval(i , k, r, tr, track_id, start_ms, duration)
        self.closed = True

    def run_loop(self):
        try:
            self.loop.create_task(self.status())
            self.closed = False
            self.loop.run_forever()
        except KeyboardInterrupt:
            pass
        finally:
            self.closed = True


    def play_loop(self, track_id, track_info, track_reps=1,
                  playback_period=1, await_last_loop=True):
        loop_info, skip_zones, _ = track_info
        self.loop.create_task(self.play(
            track_id, loop_info, track_reps
        ))
        self.loop.create_task(
            self.set_playback(period=playback_period)
        )
        self.loop.create_task(self.calibrate_clock())
        if self.killOnPause:
            self.loop.create_task(self.isPlaying())
        if self.debug:
            self.loop.create_task(self.inInterval())
        for start, end in skip_zones:
            self.loop.create_task(self.skip(start, end))
        self.loop.create_task(self.pausedOutsideLoop())
        self.loop.create_task(self.isValidTrack(track_id))
        self.run_loop()
    
    async def async_play_loop(self, track_id, track_info, track_reps=1,
                  playback_period=1):
        
        loop_info, skip_zones, _ = track_info
        
        coros = []
        coros.append(self.async_play(
            track_id, loop_info, track_reps
        ))
        coros.append(
            self.set_playback(period=playback_period)
        )
        coros.append(self.calibrate_clock())
        coros.append(self.isValidTrack(track_id))
        for start, end in skip_zones:
            coros.append(self.skip(start, end))
        
        coros.append(self.pausedOutsideLoop())

        if self.killOnPause:
            coros.append(self.isPlaying())
        if self.debug:
            coros.append(self.inInterval())
        
        self.closed = False
        await asyncio.wait(coros)
        self.closed = True

async def async_play_track(
    player, track_id, track_info, track_reps=1, playback_period=1,
    loop=None, lock=None, clock=None,
    killOnPause=False, device=None, debug=False
    ):
    await Looper(
        player, loop=loop, lock=lock, clock=clock, killOnPause=killOnPause,
        device=device, debug=debug
    ).async_play_loop(
        track_id, track_info, track_reps=track_reps,
        playback_period=playback_period
    )

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

