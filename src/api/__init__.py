# -*- coding: utf-8 -*-
"""
Created on Tue Nov 12 22:13:03 2019

@author: justi
"""

import os
import sys
sys.path.insert(1, os.path.realpath('../..'))
import src.api.utils.flamio as flamio
import src.api.loopify as loopify
import src.api.playlist as playlist
import src.api.stremix as stremix


def new(username, service, field, **kwargs):
    # user, loop, skip, playlist, stremix
    if field == 'users':
        flamio.new_user_and_service(username=username, service=service, **kwargs)
    elif field in ['loops', 'skips']:
        loopify.new_loop(username=username, service=service, field=field, **kwargs)
    elif field == 'playlists':
        playlist.new(username=username, service=service, **kwargs)
    elif field == 'stremixes':
        pass


def delete(username, service, field, **kwargs):
    # user, loop, skip, playlist, stremix
    if field == 'users':
        flamio.delete_user(username, service, **kwargs)
    elif field in ['loops', 'skips']:
        loopify.delete_loop(username=username, service=service, field=field, **kwargs)
    elif field == 'playlists':
        playlist.new(username=username, service=service, **kwargs)
    elif field == 'stremixes':
        stremix.new(username=username, service=service, **kwargs)


def rename(username, service, field, **kwargs):
    # loop, skip, playlist, stremix
    if field in ['loops', 'skips']:
        loopify.rename_loop(username=username, service=service, field=field, **kwargs)
    elif field == 'playlists':
        playlist.rename(username=username, service=service, **kwargs)
    elif field == 'stremixes':
        stremix.rename(username=username, service=service, **kwargs)


def add(username, service, field, item_field, **kwargs):
    # to playlist - loop, skip, stremix, playlist
    if field == 'playlists':
        if item_field in ['loops', 'skips']:
            playlist.add_loop(username=username, service=service, field=item_field, **kwargs)
        elif item_field in ['playlists', 'stremixes']:
            playlist.add_mix(username=username, service=service, **kwargs)
    # to stremix - loop, skip, stremix, pause
    elif field == 'stremixes':
        pass


def remove(field, username, service, name, position, users={}, path='.'):
    # from playlist - item_position
    if field == 'playlists':
        playlist.delete_item(username=username, service=service, name=name, 
                             position=position, users=users, path=path)
    # from stremix - item_position
    elif field == 'stremixes':
        pass


def multiremove(username, service, field, name, positions, users, path):
    for i,position in enumerate(sorted(positions)):
        remove(field, username, service, name, 
               position=position-i, users=users, path=path)
    

def play(field, username, service, device=None, users={}, path='.', **kwargs):
    # loop, skip, playlist, stremix
    if field in ['loops', 'skips']:
        loopify.play(username=username, service=service, field=field,
                     device=device, users=users, path=path, **kwargs)
    elif field == 'playlists':
        playlist.play(username=username, service=service, device=device, users=users, 
                      path=path, **kwargs)
    elif field == 'stremixes':
        stremix.play(username=username, service=service, device=device, users=users, 
                     path=path, **kwargs)


def view(username, service, field, user={}, **kwargs):
    # user, loop, skip, playlist, stremix
    if field == 'users':
        pass
    elif field in ['loops', 'skips']:
        loopify.view_loop(username=username, service=service, user=user, field=field, **kwargs)
    elif field == 'playlists':
        playlist.view(username=username, service=service, user=user, **kwargs)
    elif field == 'stremixes':
        pass


