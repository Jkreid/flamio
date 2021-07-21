# -*- coding: utf-8 -*-
"""
Created on Sat Jul 17 11:31:40 2021

@author: justi
"""

from abc import ABC, abstractmethod

import flamio


def flamio_method(method):
    def data_wrapped(user, *args, **kwargs):
        user.pre_method()
        value = method(user, *args, **kwargs)
        user.aft_method()
        return value
    return data_wrapped
    

class User(ABC):
    
    #// User Methods //////////////////////////////////////////////////////////
    
    def __init__(self, username, *args, info={}, **kwargs):
        self.username = username
        self.info = info
        super().__init__()
    
    @abstractmethod
    def save(self):
        # save self._info to saved data
        pass
    
    @abstractmethod
    def load(self):
        # set self._info by accessing saved data
        pass
    
    @abstractmethod
    def pre_method(self):
        pass
    
    @abstractmethod
    def aft_method(self):
        pass
    
    @property
    def info(self):
        return self._info
    
    @info.setter
    def info(self, info):
        self._info = info
    
    #// Flamio Methods ////////////////////////////////////////////////////////
    
    @flamio_method
    def create_track(self, *args, **kwargs):
        flamio.create_track(self.info, *args, **kwargs)
    
    @flamio_method
    def get_track(self, *args, **kwargs):
        return flamio.get_track(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_track(self, *args, **kwargs):
        flamio.delete_track(self.info, *args, **kwargs)
        
    @flamio_method
    def create_tag(self, *args, **kwargs):
        flamio.create_tag(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_tag(self, *args, **kwargs):
        flamio.delete_tag(self.info, *args, **kwargs)
    
    @flamio_method
    def get_tag(self, *args, **kwargs):
        return flamio.get_tag(self.info, *args, **kwargs)
    
    @flamio_method
    def rename_tag(self, *args, **kwargs):
        flamio.rename_tag(self.info, *args, **kwargs)
    
    @flamio_method
    def get_track_tags(self, *args, **kwargs):
        return flamio.get_track_tags(self.info, *args, **kwargs)
    
    @flamio_method
    def add_tag_to_track(self, *args, **kwargs):
        flamio.add_tag_to_track(self.info, *args, **kwargs)
    
    @flamio_method
    def remove_tag_from_track(self, *args, **kwargs):
        flamio.remove_tag_from_track(self.info, *args, **kwargs)

    @flamio_method
    def get_mix_tags(self, *args, **kwargs):
        return flamio.get_mix_tags(self.info, *args, **kwargs)

    @flamio_method
    def add_tag_to_mix(self, *args, **kwargs):
        flamio.add_tag_to_mix(self.info, *args, **kwargs)
    
    @flamio_method
    def remove_tag_from_mix(self, *args, **kwargs):
        flamio.remove_tag_from_mix(self.info, *args, **kwargs)
        
    @flamio_method
    def create_loop(self, *args, **kwargs):
        flamio.create_loop(self.info, *args, **kwargs)
    
    @flamio_method
    def get_loop(self, *args, **kwargs):
        return flamio.get_loop(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_loop(self, *args, **kwargs):
        flamio.delete_loop(self.info, *args, **kwargs)
    
    @flamio_method
    def add_loop_time(self, *args, **kwargs):
        flamio.add_loop_time(self.info, *args, **kwargs)
    
    @flamio_method
    def get_loop_time(self, *args, **kwargs):
        return flamio.get_loop_time(self.info, *args, **kwargs)
    
    @flamio_method
    def edit_loop_time(self, *args, **kwargs):
        flamio.edit_loop_time(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_loop_time(self, *args, **kwargs):
        flamio.delete_loop_time(self.info, *args, **kwargs)
    
    @flamio_method
    def multidelete_loop_times(self, *args, **kwargs):
        flamio.multidelete_loop_times(self.info, *args, **kwargs)
    
    @flamio_method
    def duplicate_loop_time(self, *args, **kwargs):
        flamio.duplicate_loop_time(self.info, *args, **kwargs)
    
    @flamio_method
    def move_loop_time(self, *args, **kwargs):
        flamio.move_loop_time(self.info, *args, **kwargs)
    
    @flamio_method
    def swap_loop_times(self, *args, **kwargs):
        flamio.swap_loop_times(self.info, *args, **kwargs)
        
    @flamio_method
    def create_skip(self, *args, **kwargs):
        flamio.create_skip(self.info, *args, **kwargs)
    
    @flamio_method
    def get_skip(self, *args, **kwargs):
        return flamio.get_skip(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_skip(self, *args, **kwargs):
        flamio.delete_skip(self.info, *args, **kwargs)
    
    @flamio_method
    def add_skip_time(self, *args, **kwargs):
        flamio.add_skip_time(self.info, *args, **kwargs)
    
    @flamio_method
    def get_skip_time(self, *args, **kwargs):
        return flamio.get_skip_time(self.info, *args, **kwargs)
    
    @flamio_method
    def edit_skip_time(self, *args, **kwargs):
        flamio.edit_skip_time(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_skip_time(self, *args, **kwargs):
        flamio.delete_skip_time(self.info, *args, **kwargs)
    
    @flamio_method
    def multidelete_skip_times(self, *args, **kwargs):
        flamio.multidelete_skip_times(self.info, *args, **kwargs)
    
    @flamio_method
    def duplicate_skip_time(self, *args, **kwargs):
        flamio.duplicate_skip_time(self.info, *args, **kwargs)
    
    @flamio_method
    def move_skip_time(self, *args, **kwargs):
        flamio.move_skip_time(self.info, *args, **kwargs)
    
    @flamio_method
    def swap_skip_times(self, *args, **kwargs):
        flamio.swap_skip_times(self.info, *args, **kwargs)
        
    @flamio_method
    def create_mix(self, *args, **kwargs):
        flamio.create_mix(self.info, *args, **kwargs)
    
    @flamio_method
    def get_mix(self, *args, **kwargs):
        return flamio.get_mix(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_mix(self, *args, **kwargs):
        flamio.delete_mix(self.info, *args, **kwargs)
    
    @flamio_method
    def add_mix_item(self, *args, **kwargs):
        flamio.add_mix_item(self.info, *args, **kwargs)
    
    @flamio_method
    def get_mix_item(self, *args, **kwargs):
        return flamio.get_mix_item(self.info, *args, **kwargs)
    
    @flamio_method
    def edit_mix_item(self, *args, **kwargs):
        flamio.edit_mix_item(self.info, *args, **kwargs)
    
    @flamio_method
    def delete_mix_item(self, *args, **kwargs):
        flamio.delete_mix_item(self.info, *args, **kwargs)
    
    @flamio_method
    def multidelete_mix_items(self, *args, **kwargs):
        flamio.multidelete_mix_items(self.info, *args, **kwargs)
    
    @flamio_method
    def duplicate_mix_item(self, *args, **kwargs):
        flamio.duplicate_mix_item(self.info, *args, **kwargs)
    
    @flamio_method
    def move_mix_item(self, *args, **kwargs):
        flamio.move_mix_item(self.info, *args, **kwargs)
    
    @flamio_method
    def swap_mix_items(self, *args, **kwargs):
        flamio.swap_mix_items(self.info, *args, **kwargs)
    
    @flamio_method
    def add_mix_track(self, *args, **kwargs):
        flamio.add_mix_track(self.info, *args, **kwargs)
    
    @flamio_method
    def add_mix_pause(self, *args, **kwargs):
        flamio.add_mix_pause(self.info, *args, **kwargs)
    
    @flamio_method
    def add_mix_mix(self, *args, **kwargs):
        flamio.add_mix_mix(self.info, *args, **kwargs)
    
    @flamio_method
    def edit_mix_track(self, *args, **kwargs):
        flamio.edit_mix_track(self.info, *args, **kwargs)
    
    @flamio_method
    def edit_mix_pause(self, *args, **kwargs):
        flamio.edit_mix_pause(self.info, *args, **kwargs)
    
    @flamio_method
    def edit_mix_mix(self, *args, **kwargs):
        flamio.edit_mix_mix(self.info, *args, **kwargs)
        
    @flamio_method
    def get_track_play_info(self, *args, **kwargs):
        return flamio.get_track_play_info(self.info, *args, **kwargs)
    
    @flamio_method
    def get_item_play_info(self, *args, **kwargs):
        return flamio.get_item_play_info(self.info, *args, **kwargs)
         
    @flamio_method
    def get_mix_play_info(self, *args, **kwargs):
        return flamio.get_mix_play_info(self.info, *args, **kwargs)
