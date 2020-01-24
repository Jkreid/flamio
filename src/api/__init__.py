# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 22:13:03 2019

@author: justi

API
"""


import src.api.flamio as flamio
import src.api.loopify as loopify
import src.api.mixify as mixify
import src.api.skipify as skipify

class Client:
    
    def __init__(self, username, service, savepath):
        self.username = username
        self.service = service
        self.path = savepath
        self.user = flamio.get_user(username,service,path=savepath)
    
    
    def get(self, field, **kwargs):
        pass
    
    
    def put(self, field, **kwargs):
        pass
    
    
    def post(self, field, **kwargs):
        pass
    
    
    def delete(self, field, **kwargs):
        pass
    
    

def new(username, service, field, **kwargs):
    # user, loop, skip, playlist, stremix
    if field == 'users':
        flamio.new_user_and_service(username=username, service=service, **kwargs)
    elif field in ['loops', 'skips']:
        loopify.new_loop(username=username, service=service, field=field, **kwargs)
    elif field == 'playlists':
        mixify.new(username=username, service=service, **kwargs)
    elif field == 'stremixes':
        pass


def delete(username, service, field, **kwargs):
    # user, loop, skip, playlist, stremix
    if field == 'users':
        flamio.delete_user(username, service, **kwargs)
    elif field in ['loops', 'skips']:
        loopify.delete_loop(username=username, service=service, field=field, **kwargs)
    elif field == 'playlists':
        mixify.delete(username=username, service=service, **kwargs)
    elif field == 'stremixes':
        stremix.new(username=username, service=service, **kwargs)


def rename(username, service, field, **kwargs):
    # loop, skip, playlist, stremix
    if field in ['loops', 'skips']:
        loopify.rename_loop(username=username, service=service, field=field, **kwargs)
    elif field == 'playlists':
        mixify.rename(username=username, service=service, **kwargs)
    elif field == 'stremixes':
        stremix.rename(username=username, service=service, **kwargs)


def add(username, service, field, item_field, **kwargs):
    # to avoid - skip, new_skip
    # to mix - loop, skip, mix, avoid
    if field == 'playlists':
        if item_field in ['loops', 'skips']:
            mixify.add_loop(username=username, service=service, field=item_field, **kwargs)
        elif item_field in ['playlists', 'stremixes']:
            mixify.add_mix(username=username, service=service, **kwargs)
    # to stremix - loop, skip, stremix, pause
    elif field == 'stremixes':
        pass


def remove(username, service, field, name, position, users={}, path='.'):
    # from playlist - item_position
    if field == 'playlists':
        mixify.delete_item(username=username, service=service, name=name, 
                             position=position, users=users, path=path)
    # from stremix - item_position
    elif field == 'stremixes':
        pass


def multiremove(username, service, field, name, positions, users, path):
    # from playlist, from stremix
    if field in ['playlists', 'stremixes']:
        for i,position in enumerate(sorted(positions)):
            remove(username, service, field, name, 
                   position=position-i, users=users, path=path)
    

def play(username, service, field, **kwargs):
    # loop, skip, mix, avoid
    if field in ['loops', 'skips']:
        return loopify.play(username=username, service=service, field=field, **kwargs)
    elif field in ['playlists','stremixes']:
        return mixify.play(username=username, service=service, field=field, **kwargs)


def view(username, service, field, user={}, **kwargs):
    # user, loop, skip, playlist, stremix
    if field == 'users':
        pass
    elif field in ['loops', 'skips']:
        loopify.view_loop(username=username, service=service, user=user, field=field, **kwargs)
    elif field == 'playlists':
        mixify.view(username=username, service=service, user=user, **kwargs)
    elif field == 'stremixes':
        pass


def edit(username, service, field, song_id, name, **kwargs):
    # loop, skip
    if field in ['loops', 'skips']:
        loopify.edit_loop(username=username, service=service, field=field,
                          song_id=song_id, name=name, **kwargs)


def move(username, service, field, **kwargs):
    # in playlist
    if field == 'playlists':
        mixify.move_item(username=username, service=service, **kwargs)
    # in stremix
    elif field == 'stremixes':
        pass


def duplicate(username, service, field, **kwargs):
    # in playlist
    if field == 'playlists':
        mixify.duplicate_item(username=username, service=service, **kwargs)
    # in stremix
    elif field == 'stremixes':
        pass


def change_reps(username, service, field, **kwargs):
    # in playlist
    if field == 'playlists':
        mixify.change_reps(username=username, service=service, **kwargs)
    # in stremix
    elif field == 'stremixes':
        pass