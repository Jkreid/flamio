# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 20:31:00 2021

@author: justi
"""

import requests
import functools
import secrets
import string

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

def gen_random_string(n=13):
    return ''.join(secrets.choice(string.ascii_lowercase + string.digits)for i in range(n))

#### data format converters

class QueryParams(dict):
    def stringify(self):
        return functools.reduce(
            lambda x, y: f'{x}&{y}',
            map(lambda x: f'{x[0]}={x[1]}', self.items())
        )

def get_url_with_query_params(url, data):
    return f'{url}?{QueryParams(data).stringify()}'

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

def get_session():
    return requests.Session()

def raise_response_error(response):
    msg = response.content.decode()
    if 'error' in msg:
        raise Exception(msg)
    raise ValueError(
        f'response status code is {response.status_code} because of {response.reason}'
    )

def req(function):
    def error_catcher(rc, *args, **kwargs):
        res = function(rc, *args, timeout=rc.timeout, **kwargs)
        if 199 < res.status_code < 230:
            if res.status_code != 204:
                return res.json()
        else:
            raise_response_error(res)
    return error_catcher

class RequestClient:
    
    def __init__(self, sess=None, url=None, max_retries=None, timeout=None):
        self.session = sess or get_session()
        self.timeout = timeout
        if url and max_retries:
            self.mount_max_retries(url, max_retries)
        
    @property
    def session(self):
        return self._session
    
    @session.setter
    def session(self, sess):
        self._session = sess
    
    def mount_max_retries(self, url, max_retries):
        self.session.mount(
            url,
            requests.adapters.HTTPAdapter(max_retries=max_retries)
        )
        
    def update_headers(self, headers):
        self.session.headers.update(headers)
    
    @req
    def get(self, url, **kwargs):
        return self.session.get(url, **kwargs)
    
    @req
    def put(self, url, **kwargs):
        return self.session.put(url, **kwargs)
    
    @req
    def post(self, url, **kwargs):
        return self.session.post(url, **kwargs)
    
    @req
    def delete(self, url, **kwargs):
        return self.session.delete(url, **kwargs)



def async_req(coroutine):
    async def async_error_catcher(rc, *args, **kwargs):
        async with await coroutine(rc, *args, timeout=rc.timeout, headers=rc.headers, **kwargs) as resp:
            if 199 < resp.status < 230:
                if resp.status != 204:
                    return await resp.json()
            else:
                raise ValueError(f'Request returned code: {resp.status}') 
    return async_error_catcher

class AsyncRequestClient:

    def __init__(self, timeout=None):
        self.timeout = timeout
        self.headers = {}
    
    def update_headers(self, headers):
        self.headers.update(headers)
    
    @async_req
    async def get(self, session, url, **kwargs):
        return await session.get(url, **kwargs)
    
    @async_req
    async def put(self, session, url, **kwargs):
        return await session.put(url, **kwargs)
    
    @async_req
    async def post(self, session, url, **kwargs):
        return await session.post(url, **kwargs)
    
    @async_req
    async def delete(self, session, url, **kwargs):
        return await session.delete(url, **kwargs)
