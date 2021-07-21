# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 11:31:40 2021

@author: justi
"""
import utils
import play
import spotify
import time as t

from abc import ABC, abstractmethod

class Player(ABC):
    
    def __init__(self, *args, **kwargs):
        super().__init__()
    
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
    
    @property
    @abstractmethod
    def username(self):
        pass
    
    @abstractmethod
    def current_playback(self):
        pass
    
    @abstractmethod
    def start_playback(self):
        pass
    
    @abstractmethod
    def pause_playback(self):
        pass
    
    @abstractmethod
    def resume_playback(self):
        pass
    
    @abstractmethod
    def pause(self):
        pass
    
    @abstractmethod
    def seek_track(self):
        pass
    
    @abstractmethod
    def current_track(self):
        pass
    
    @abstractmethod
    def devices(self):
        pass
    
    @abstractmethod
    def current_device(self):
        pass


class SpotifyPlayer(Player):
    
    def __init__(self, username, refresh_time=0, token=None):
        super().__init__()
        self.username = username
        self.token = token
        self._refresh_time = refresh_time
        self._refresh_token()
    
    @property
    def username(self):
        return self._username
    
    @username.setter
    def username(self, name):
        self._username = name
    
    def _is_valid_token(self):
        return t.time() - self._refresh_time < spotify.tokenLifetime
    
    def _set_refresh_time(self, refresh_time):
        self._refresh_time = refresh_time

    def _refresh_token(self):
        old_token = self.token
        new_time = t.time()
        self.token = spotify.get_token(self.username)
        self.player = spotify.get_player(self.token)
        if (old_token != self.token) and self._refresh_time:
            self._refresh_time = new_time

    @spotify.token_checker
    def current_playback(self):
        return spotify.current_playback(self.player)
    
    @spotify.token_checker
    def start_playback(self, track_id, device=None):
        return spotify.start_playback(self.player, track_id, device=device)
    
    @spotify.token_checker
    def pause_playback(self, device=None):
        return spotify.pause_playback(self.player, device=device)
    
    @spotify.token_checker
    def resume_playback(self, device=None):
        return spotify.resume_playback(self.player, device=device)
    
    def pause(self, duration=0, device=None):
        self.pause_playback(device)
        if duration >= 0:
            t.sleep(duration)
            self.resume_playback(device)
    
    @spotify.token_checker
    def seek_track(self, position_ms):
        return spotify.seek_track(self.player, position_ms)
    
    @spotify.token_checker
    def current_track(self):
        return spotify.get_current_track(self.player)
    
    @spotify.token_checker
    def devices(self):
        return spotify.get_devices(self.player)
    
    @spotify.token_checker
    def current_device(self):
        return spotify.get_current_device(self.player)

    @spotify.token_checker
    def end_to_ms(self, track_id):
        return spotify.end_to_ms(self.player, track_id)

    def end_to_time(self, track_id):
        return utils.ms_to_time(self.end_to_ms(track_id))