# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 20:31:00 2021

@author: justi
"""

import functools

#### algorithms

def merged_intervals(unmerged):

    def union_set(unioned_set, interval):
        if not isinstance(unioned_set[0], list):
            unioned_set = [unioned_set]
        last_interval = unioned_set[-1]
        if interval[0] > last_interval[1]:
            unioned_set.append(interval)
        else:
            last_interval[1] = max(interval[1], last_interval[1])
        return unioned_set
    
    return unmerged if len(unmerged) < 2 else functools.reduce(
        union_set, sorted(unmerged, key=lambda x: x[0])
    )

#### data format converters

def time_to_ms(time):
    assert ':' in time
    minutes, seconds = map(float, time.split(':'))
    return int(1000*(minutes*60 + seconds))

def ms_to_time(ms):
    ms = int(ms)
    minute, seconds = int(ms/60000), round((ms/1000)%60, 3)
    return ':'.join(map(str, (minute,seconds)))

def times_to_intervals(times):
    # times : List[Dict[str, str]]
    # returns : List[List[int, int]]
    return merged_intervals(
        [list(map(lambda x: time_to_ms(time[x]), ('start', 'end')))
         for time in times]
    )
