import json
from dataclasses import dataclass
from typing import Optional, Any
from uuid import uuid4
from http import HTTPStatus

from aiohttp import web, ClientSession
# from redis import Redis

from flamio.utils import hget_str
from flamio.redis import Redis
from flamio.play import Player
from flamio.spotify import AsyncSpotifyAuthClient
from flamio.users import LocalUser

@dataclass
class User(LocalUser):
    id: str
    spotify_token: str
    info: dict

def get_user(user_id, load_data=True):
    db_user = LocalUser(user_id, load_data=load_data)
    db_user.id = user_id
    db_user.spotify_token = db_user.refresh_token
    return db_user


routes = web.RouteTableDef()
redis = Redis(host="localhost", port=6379)

class AuthedView(web.View):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._user: Optional[User] = None

    @property
    def user_id(self):
        #return get_user_from_token(self.request.headers['Authorization'].split('Bearer')[1].strip())
        return self.request.query.get('user_id')
    
    def load_user(self, load_data=False) -> User:
        return get_user(self.user_id, load_data=load_data)
    
    @property
    def user(self):
        if not self._user:
            self._user = self.load_user(load_data=True)
        return self._user


@routes.view('/objects/tag/{tag_id}')
class TagView(AuthedView):

    @property
    def tag_id(self):
        return self.request.match_info.get('tag_id')

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")
    
    async def post(self):
        return web.Response(status=HTTPStatus.OK, text="ok")
    
    async def patch(self):
        return web.Response(status=HTTPStatus.OK, text="ok")

    async def delete(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/objects/tags')
class TagsView(AuthedView):

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/objects/mix/{mix_id}')
class MixView(AuthedView):

    @property
    def mix_id(self):
        return self.request.match_info.get('mix_id')

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")
    
    async def post(self):
        return web.Response(status=HTTPStatus.OK, text="ok")
    
    async def patch(self):
        return web.Response(status=HTTPStatus.OK, text="ok")

    async def delete(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/objects/mixes')
class MixesView(AuthedView):

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/objects/track/{track_id}')
class TrackView(AuthedView):

    @property
    def track_id(self):
        return self.request.match_info.get('track_id')

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")
    
    async def post(self):
        return web.Response(status=HTTPStatus.OK, text="ok")

    async def delete(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/objects/tracks')
class TracksView(AuthedView):

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/objects')
class ObjectsView(AuthedView):

    async def get(self):
        return web.Response(status=HTTPStatus.OK, text="ok")


@routes.view('/playing')
class PlayView(AuthedView):
    
    async def get(self):
    #     return web.Response(status=HTTPStatus.OK, text="ok")

    # async def put(self):

        async def get_and_cache_spotify_token_from_user():
            token = self.user.spotify_token #or self.load_user().spotify_token
            redis.hset(f'spotify_token:{self.user.id}', self.user.id, token)
            return token

        # data = await self.request.json()
        data = {'item':{'item_id':'5BfayLeEScEePDYXJCnvU1', 'type':'track', 'reps':1, 'extensions':{'loop_names':['dabump']}}}
        play_item = data.get('item')
        item_id = play_item.get('item_id')
        item_type = play_item.get('type')
        reps = int(play_item.get('reps'))
        extensions = play_item.get('extensions')
        
        self.user.info = data.get('objects') or self.user.info
        spotify_token = (
            hget_str(redis, f'spotify_token:{self.user.id}', self.user.id) or
            await get_and_cache_spotify_token_from_user()
        )
        redis_key = f'playing:{self.user.id}'
        
        
        async with ClientSession(trust_env=True) as session:
            async with AsyncSpotifyAuthClient(session, refresh_token=spotify_token) as client:
                player = Player(uuid4(), client)
                redis.hmset(redis_key, {
                    'item_id':item_id,
                    'type': item_type,
                    'extensions': ';'.join([f'{k}-{",".join(y)}' for k,y in extensions.items()]),
                    'player_id': player.id,
                    'reps': reps,
                })                
                if item_type == 'track':
                    await player.play_track(
                        play_item['item_id'],
                        self.user.get_track_play_info(
                            item_id,
                            **extensions
                        ),
                        track_reps=reps,
                    )
                elif item_type == 'mix':
                    await player.play_mix(
                        self.user.get_mix_play_info(item_id),
                        mix_reps=reps,
                    )
                else:
                    return web.Response(status=HTTPStatus.BAD_REQUEST, reason='error invalid play item type')
                if hget_str(redis, redis_key, 'player_id') == str(player.id):
                    redis.delete(redis_key)
        
        return web.Response(status=HTTPStatus.NO_CONTENT, text="ok no content")
    
    async def delete(self):
        return web.Response(status=HTTPStatus.NO_CONTENT, text="ok no content")


@routes.get('/livez')
async def livez(_: web.Request):
    return web.Response(status=HTTPStatus.OK, text="ok")


@routes.get('/readyz')
async def readyz(_: web.Request):
    body = {}
    try:
        redis.ping()
        body['redis'] = 'ok'
    except:
        body['redis'] = 'failed'
    return web.Response(body=json.dumps(body),
        status=HTTPStatus.INTERNAL_SERVER_ERROR if any(map(lambda x: x != 'ok', body.values())) else HTTPStatus.OK
    )

app = web.Application()
app.add_routes(routes)
web.run_app(app)