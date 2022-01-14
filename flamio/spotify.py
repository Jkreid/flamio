# -*- coding: utf-8 -*-
"""
Created on Tue Jul 13 23:59:45 2021

@author: justi
"""

import flamio.utils as utils
import time as t
#// Constants /////////////////////////////////////////////////////////////////

DATA_PATH = '.'

AUTH = {
    'redirect_uri'  : 'http://localhost:8888/lab',
    'client_id'     : 'cd33a00276a645f393445c438115b958',
    'client_secret' : 'b9988db76d074442aa81a37312d12d29',
    'scope'         : [
        'streaming',
        'user-read-playback-state',
        'user-modify-playback-state',
        'user-read-currently-playing'
    ]
}

#// Basic Client Classes & Functions ///////////////////////////////////////////

def add_client_credentials(function):
    def auth_request_params_method(client):
        data = function(client)
        data.update({
            'client_id':AUTH['client_id'],
            'client_secret':AUTH['client_secret']
        })
        return data
    return auth_request_params_method

def endpoint_request(function):
    def endpoint_requestor(client, endpoint, **kwargs):
        if not client.is_valid_token():
            client.reset_token()
        return function(
            client,
            f'{client.endpoint_url}/{endpoint}',
            **kwargs
        )
    return endpoint_requestor

class BaseSpotifyClient:
    
    def __init__(self):
        self.auth_url = 'https://accounts.spotify.com/api/token'
        self.auth_token = None
        self.expiration = 0
        self.expires_in = 3600
        self.exp_buffer = 1
        self.auth_timeout = (1,1)
        self.endp_timeout = (2,5)
        self.auth_retries = 2
        self.endp_retries = 1
        self.endpoint_url = 'https://api.spotify.com/v1'
        self._token_refreshed = False
    
    def is_valid_token(self):
        return self.auth_token and (t.time() < self.expiration)

    def update_header_token(self):
        self.endpoint_client.update_headers(
            {'Authorization': f'Bearer {self.auth_token}'}
        )
        self._token_refreshed = True
    
    @property
    def token_refreshed(self):
        if self._token_refreshed:
            self._token_refreshed = False
            return True
        return False

    def parse_token_info(self, token_info, call_time):
        self.expires_in = float(token_info['expires_in'])
        self.expiration = call_time + self.expires_in - self.exp_buffer
        self.auth_token = token_info['access_token']
        if 'refresh_token' in token_info:
            self.refresh_token = token_info['refresh_token']
        self.update_header_token()
    
    @add_client_credentials
    def get_cc_request_data(self):
        return {'grant_type': 'client_credentials'}
    
    @add_client_credentials
    def get_auth_request_data(self):
        return {
            'grant_type': 'authorization_code',
            'code': self.code,
            'redirect_uri':AUTH['redirect_uri']
        }
    
    @add_client_credentials
    def get_refresh_request_data(self):
        return {
            'grant_type': 'refresh_token',
            'refresh_token': self.refresh_token
        }

class SpotifyClient(BaseSpotifyClient):

    def __init__(self, session=None):
        super().__init__()
        self.session = session or utils.get_session()
        self.endpoint_client = utils.RequestClient(
            timeout=self.endp_timeout,
            url=self.endpoint_url,
            max_retries=self.endp_retries,
            sess=self.session
        )
        self.token_client = utils.RequestClient(
            timeout=self.auth_timeout,
            sess=self.session,
            url=self.auth_url,
            max_retries=self.auth_retries
        )
        self.reset_token()
    
    def token_request(self, request_data):
        call_time = t.time()
        self.parse_token_info(
            self.token_client.post(
                self.auth_url,
                data=request_data
            ),
            call_time
        )
    
    def reset_token(self):
        self.token_request(self.get_cc_request_data())
    
    @endpoint_request
    def get(self, endpoint, **kwargs):
        return self.endpoint_client.get(endpoint, **kwargs)
    
    @endpoint_request
    def post(self, endpoint, **kwargs):
        return self.endpoint_client.post(endpoint, **kwargs)
    
    @endpoint_request
    def put(self, endpoint, **kwargs):
        return self.endpoint_client.put(endpoint, **kwargs)
    
    @endpoint_request
    def delete(self, endpoint, **kwargs):
        return self.endpoint_client.delete(endpoint, **kwargs)

def get_auth_code_request_url(state):
    # in FE, redirect user to this url which will redirect to the redirect_url after auth with the code & state
    # logic to handle parsing the code & state happens only on the frontend at the redirect_url endpoint
    return utils.get_url_with_query_params(
        'https://accounts.spotify.com/authorize',
        {
            'client_id': AUTH['client_id'],
            'response_type': 'code',
            'redirect_uri': AUTH['redirect_uri'],
            'scope': ' '.join(AUTH['scope']),
            'state': state
        }
    )

class SpotifyAuthClient(SpotifyClient):
    
    def __init__(self, code=None, refresh_token=None, session=None):
        self.code = code
        self.refresh_token = refresh_token
        super().__init__(session=session)
    
    @staticmethod
    def get_auth_code_request_url(state):
        return get_auth_code_request_url(state)
    
    def reset_token(self):
        if self.refresh_token:
            self.token_request(self.get_refresh_request_data())
        elif self.code:
            self.token_request(self.get_auth_request_data())
        else:
            raise ValueError('Cannont get access token without auth code or refresh token')

def get_track(client: SpotifyClient, track_id: str):
    return client.get(f'tracks/{track_id}')

def end_to_ms(client: SpotifyClient, track_id: str):
    return int(get_track(client, track_id)['duration_ms'])

def get_currently_playing(client):
    return client.get('me/player/currently-playing')

def get_current_track(client):
    return get_currently_playing(client)['item']

def get_current_track_id(client):
    return get_current_track(client)['id']

def get_current_playback(client):
    return client.get('me/player')

def seek_track(client, position_ms):
    return client.put(f'me/player/seek?position_ms={position_ms}')

def pause_playback(client, device=''):
    return client.put('me/player/pause', data={'device_id': device})

def get_devices(client):
    return client.get('me/player/devices')['devices']

def get_current_device(client):
    playback = get_current_playback(client)
    if 'device' in playback:
        device = playback['device']
        return device
    return {}

def start_playback(client, track_id, device='', position_ms=0):
    return client.put(
        'me/player/play',
        json={
            'device_id': device,
            'uris': [f'spotify:track:{track_id}'],
            'position_ms': position_ms
        }
    )

def resume_playback(client, device=''):
    return client.put('me/player/play', json={'device_id': device})

#// Async Client Classes & Functions ///////////////////////////////////////////


def async_endpoint_request(coroutine):
    async def endpoint_requestor(client, path, **kwargs):
        if not client.is_valid_token():
            await client.reset_token()
        return await coroutine(
            client,
            f'{client.endpoint_url}/{path}',
            **kwargs
        )
    return endpoint_requestor

class AsyncSpotifyClient(BaseSpotifyClient):
    
    def __init__(self):
        super().__init__()
        self.auth_timeout = 1
        self.endp_timeout = 2
        self.endpoint_client = utils.AsyncRequestClient(
            timeout=self.endp_timeout,
        )
        self.token_client = utils.AsyncRequestClient(
            timeout=self.auth_timeout,
        )
    
    @classmethod
    async def create(cls, session):
        self = AsyncSpotifyClient()
        await self.reset_token(session)
        return self
    
    async def token_request(self, session, request_data):
        call_time = t.time()
        self.parse_token_info(
            await self.token_client.post(
                session,
                self.auth_url,
                data=request_data
            ),
            call_time
        )
    
    async def reset_token(self, session):
        await self.token_request(session, self.get_cc_request_data())
    
    @async_endpoint_request
    async def get(self, url, **kwargs):
        return await self.endpoint_client.get(self.session, url, **kwargs)
    
    @async_endpoint_request
    async def post(self, url, **kwargs):
        return await self.endpoint_client.post(self.session, url, **kwargs)
    
    @async_endpoint_request
    async def put(self, url, **kwargs):
        return await self.endpoint_client.put(self.session, url, **kwargs)
    
    @async_endpoint_request
    async def delete(self, url, **kwargs):
        return await self.endpoint_client.delete(self.session, url, **kwargs)



class AsyncSpotifyAuthClient(AsyncSpotifyClient):

    def __init__(self, session, code=None, refresh_token=None):
        self.code = code
        self.refresh_token = refresh_token
        self.session = session
        super().__init__()
    
    @classmethod
    async def create(cls, code=None, refresh_token=None):
        self = AsyncSpotifyAuthClient(
            code=code,
            refresh_token=refresh_token
        )
        await self.reset_token()
        return self
    
    def __aenter__(self):
        return self

    def __await__(self):
        return self.reset_token().__await__()

    @staticmethod
    def get_auth_code_request_url(state):
        return get_auth_code_request_url(state)
    
    async def __aexit__(self, exc_type, exc, tb):
        pass
    

    async def reset_token(self):
        if self.refresh_token:
            await self.token_request(self.session, self.get_refresh_request_data())
        elif self.code:
            await self.token_request(self.session, self.get_auth_request_data())
        else:
            raise ValueError('Cannont get access token without auth code or refresh token')
        return self

async def async_get_track(client: AsyncSpotifyClient, track_id: str):
    return await get_track(client, track_id)

async def async_end_to_ms(client: AsyncSpotifyClient, track_id: str):
    return int(await async_get_track(client, track_id))

async def async_get_currently_playing(client: AsyncSpotifyAuthClient):
    return await get_currently_playing(client)

async def async_get_current_track(client: AsyncSpotifyAuthClient):
    return (await async_get_currently_playing(client))['item']

async def async_get_current_track_id(client: AsyncSpotifyAuthClient):
    return (await async_get_current_track(client))['id']

async def async_get_current_playback(client: AsyncSpotifyAuthClient):
    return await get_current_playback(client)

async def async_seek_track(client: AsyncSpotifyAuthClient, position_ms: int):
    await seek_track(client, position_ms)

async def async_pause_playback(client: AsyncSpotifyAuthClient, device: str=''):
    await pause_playback(client, device)

async def async_get_devices(client: AsyncSpotifyAuthClient):
    return (await client.get('me/player/devices'))['devices']

async def async_get_current_device(client: AsyncSpotifyAuthClient):
    playback = await async_get_current_playback(client)
    if 'device' in playback:
        device = playback['device']
        return device
    return {}

async def async_start_playback(
    client: AsyncSpotifyAuthClient,
    track_id: str,
    device: str='',
    position_ms: int=0
):
    await start_playback(client, track_id, device=device, position_ms=position_ms)

async def async_resume_playback(client: AsyncSpotifyAuthClient, device: str=''):
    await resume_playback(client, device=device)