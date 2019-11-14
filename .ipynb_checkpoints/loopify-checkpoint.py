# -*- coding: utf-8 -*-
"""
Created on Fri Sep 13 20:40:12 2019

@author: justi

Loopify
"""

import spotipy
import spotipy.util as util
import time as t

APP_ID='cd33a00276a645f393445c438115b958'
SECRET='b9988db76d074442aa81a37312d12d29'
REDIRECT='http://localhost:8888/lab'
SCOPES='streaming user-read-playback-state user-modify-playback-state user-read-currently-playing'


class User:
    
    def __init__(self, spotify_username, token=None):
        self.username=spotify_username
        self.loopMixes={}
        self.loop_banks={}
        self.login_time = t.time()
        self.token = token or util.promt_for_user_token(**{'username':spotify_username,
                                                            'scope':SCOPES,
                                                            'client_id':APP_ID,
                                                            'client_secret':SECRET,
                                                            'redirect_uri':REDIRECT})
        
    
    def login(self):
        self.login_time = t.time()
        pass
        #self.token = refresh_through_api(self.token)
    
    def add_LoopBank(self, song_id):
        self.loop_banks.update({song_id:LoopBank(song_id=song_id, token=self.token)})
    
    def make_loop(self, song_id, start, end):
        if song_id not in self.loop_banks.keys():
            self.loop_banks.update({song_id:LoopBank(song_id=song_id, token=self.token, start=start, end=end)})
        else:
            self.loop_banks[song_id].add_loop(start=start,end=end, token=self.token)
    
    def make_LoopMix(self, song_id, name=None, device_id=None):
        if song_id not in self.loop_banks.keys():
            self.add_LoopBank(song_id)
            if input('add loops to bank? (y/n): ')[0] == 'y':
                self.loop_banks[song_id].make_loops(self.token)
        if name:
            while name in self.loopMixes.keys():
                name = input('Name already in use. Enter new name: ')
            self.loopMixes.update({name:LoopMix(loop_bank=self.loop_banks[name], 
                                                device=device_id, 
                                                name=name)})
        else:
            lm = LoopMix(loop_bank=self.loop_banks[song_id],
                         device=device_id)
            if lm.name == '[untitled]':
                lm.name = '[untitled_{}]'.format(len(self.loopMixes))
            self.loopMixes.update({lm.name:lm})
            
    
    def play_loop(self, start, end, device_id=None, spotify=None):
        # play loop from start to end, with no loop saving
        pass
    
    def add_album_playlist(self):
        pass
    
    def play_album_playlist(self, shuffle='album'):
        pass
    
    

class LoopBank:
        
    def __init__(self, song_id, token, start=None, end=None):
        
        self.song_id = song_id
        self.loops={}
        self.token = token
        if start or end:
            self.add_loop(start=start, end=end)
    
    
    def add_loop(self, start=None, end=None, spotify=None, token=None):
        
        sp = spotify or spotipy.Spotify(auth=(token or self.token))
        
        def position_loop(start_pos,end_pos):
            
            position = lambda x: int((float(x.split(':')[0])*60 + float(x.split(':')[1]))*1000)
            
            start_position = 0 if start_pos == 'start' else position(start_pos)
            if end_pos == 'end':
                end_position = sp.audio_features(tracks=self.song_id)[0]['duration_ms']
            else:
                end_position = position(end_pos)
            
            return (start_position,end_position)
        
        start = start or input('loop start (format - min:sec - as decimals): ')
        end = end or input('loop end (format - min:sec - as decimals): ')
        
        self.loops.update({input('loop name [Hit Enter for default (order #)]:') or len(self.loops):position_loop(start,end)})
    
    def make_loops(self, spotify=None, token=None):
        sp = spotify or spotipy.Spotify(auth=(token or self.token))
        self.add_loop(sp)
        ask = input('Add new loop? (y/n): ')
        while ask[0].lower() == 'y':
            self.add_loop(sp)
            ask = input('Add new loop? (y/n): ')
            
        
            
class LoopMix:
    
    def __int__(self, loop_bank, device=None, name=None):
        self.device = device
        self.song_id = loop_bank.song_id
        self.loop_bank = loop_bank.loops
        self.loops = []
        self.name = name or input('Enter name: ') or '[untitled]'
    
    
    def add_to_bank(self, loop_name, t1, t2):
        self.loop_bank.update({loop_name:(t1,t2)})
    
    
    def add(self, loop_name, positions=['end'], xtimes=[1], spotify=None):
        
        positions = positions if type(positions) is list else [positions]
        xtimes = xtimes if type(xtimes) is list else [xtimes]
        
        if loop_name in self.loop_bank.keys():
            for p,x in zip(positions,xtimes):
                
                t1,t2 = self.loop_bank[loop_name]
                if p == 'end' or p == len(self.loops):
                    self.loops.append((t1,t2,x))
                else:
                    if not type(x) is int:
                        x = 1
                    self.loops.insert(p, (t1,t2,x))

                
    def remove(self, loop_name, positions, multiplicities):
        pass
    
    
    def move_loop(self, loop_name, old_positions, new_positions, old_mults, new_mults):
        pass
    
    
    def add_pauses(self, positions, durations):
        
        positions = positions if type(positions) is list else [positions]
        durations = durations if type(durations) is list else [durations]
        
        for p,d in zip(positions,durations):
            
            position = lambda x: int((float(x.split(':')[0])*60 + float(x.split(':')[1]))*1000)
            
            if type(d) is int: # miliseconds
                pass
            elif type(d) is float: # seconds
                d = int(d*1000)
            else: # 'min:sec' notation
                d = position(d)
            
            if p == 'end' or p == len(self.loops):
                self.loops.append((0, d, 0))
            else:
                self.loops.insert(p, (0, d, 0))

    
    def play(self,
             token,
             device_id=None, 
             ntimes=None, 
             through_pause=None):
        """ play the loop on the given, defaulted or playing device according to rules of given arguments"""
        
        ### 1. Checking conditions, setting variables, and defining utility functions  -------------------------------------
        
        # if ntimes, default through_pause to True - otherwise, defualt to None (acts as false)
        through_pause = True if ntimes and through_pause!=False else through_pause
        
        # make the spotify object from the given token
        sp = spotipy.Spotify(auth=token)
        
        # find user inputed device or the loop's default device and end function if none found
        if device_id=='defualt' or device_id=='-d':
            device_id = self.device
        if not sp.current_playback():
            if not device_id or self.device:
                input('No device currently identified or defaulted! Hit enter when device selected');
            else:
                device_id = device_id or self.device
        else:
            device_id = device_id or sp.current_playback()['device']['id']
        
        # define potential loop kill flags
        FLAG_songChange = lambda: sp.current_user_playing_track()['item']['uri'].split(':')[-1] != self.song_id.split('/')[-1]
        FLAG_outsideLoop = lambda t1,t2: not (t1< sp.current_playback()['progress_ms'] < t2)
        FLAG_paused = lambda : not sp.current_playback()['is_playing']
        
        # define loop/kill-loop function
        def kill_loop(loopmix, device, persist):
            """ Let loop play and check flags for if kill condition is met and return bool(kill)"""
            
            # all loops except for the last are given an integer multiplicity number for consecutive plays
            # num == 0 means pause for a time of t2-t1
            for t1,t2,num in loopmix[:-1]:
                if num:
                    for _ in range(num):
                        sp.seek_track(position_ms=t1, device_id=device)
                        while (not FLAG_paused() or persist) and not FLAG_outsideLoop(t1,t2) and not FLAG_songChange(): 
                            if not sp.current_playback():
                                return True
                        if FLAG_songChange() or (FLAG_paused() and (not persist or FLAG_outsideLoop(t1,t2))): 
                            return True
                else:
                    if sp.current_playback():
                        if not FLAG_paused():
                            sp.pause_playback()
                        t.sleep((t2-t1)/1000)
                        if sp.current_playback():
                            if not FLAG_paused():
                                sp.start_playback(device_id=sp.current_playback()['device']['id'])
                    if FLAG_songChange() or (not persist and FLAG_paused()):
                        return True
            
            # the final loop is defined and can be played like the earlier ones or looped continuously
            t1,t2,num = loopmix[-1]
            if num == 'loop' or 'l':
                while not (FLAG_paused() and FLAG_outsideLoop(t1,t2)) and not FLAG_songChange():
                    sp.seek_track(position_ms=t1, device_id=device)
                    while (not FLAG_paused() or persist) and not FLAG_outsideLoop(t1,t2) and not FLAG_songChange():
                        if not sp.current_playback():
                                return True
                return True
            else:
                if num:
                    num = num if type(num) is int else 1
                    for _ in range(num):
                        sp.seek_track(position_ms=t1, device_id=device)
                        while (not FLAG_paused() or persist) and not FLAG_outsideLoop(t1,t2) and not FLAG_songChange(): 
                            if not sp.current_playback():
                                return True
                        if FLAG_songChange() or (FLAG_paused() and (not persist or FLAG_outsideLoop(t1,t2))): 
                            return True
                else:
                    if sp.current_playback():
                        if not FLAG_paused():
                            sp.pause_playback()
                        t.sleep((t2-t1)/1000)
                        if sp.current_playback():
                            if not FLAG_paused():
                                sp.start_playback(device_id=sp.current_playback()['device']['id'])
                    if FLAG_songChange() or (not persist and FLAG_paused()):
                        return True
            
            # escape the loop alive, return False
            return False
                
        ### 2. Playing the loops and killing them if neccessary (pause if finished without kill)  --------------------------
        
        # initalize playback
        if sp.current_playback():
            if not FLAG_paused():
                sp.pause_playback()
        else:
            print("still no playback device selected. I'm dissapointed fam...")
            return
        if sp.current_playback()['repeat_state'] == 'track':
            sp.start_playback(device_id=device_id, uris=[self.song_id])
            sp.repeat('track')
        else:
            sp.start_playback(device_id=device_id, uris=[self.song_id])
        
        # play loops ntimes(>=1) and then continue while spotify repeat mode is set to track. kill loops if conditions met
        for _ in range(ntimes or 1):
            device_id = sp.current_playback()['device']['id']
            if kill_loop(self.loops, device_id, through_pause):
                return
        while sp.current_playback()['repeat_state'] == 'track':
            device_id = sp.current_playback()['device']['id']
            if kill_loop(self.loops, device_id, through_pause):
                return
        
        sp.pause_playback()
        
        