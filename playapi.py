from aiohttp import web, ClientSession
from flamio.player import Player

from flamio.spotify import AsyncSpotifyAuthClient

routes = web.RouteTableDef()

def get_player(coroutine):
    async def endpoint_with_player(req: web.Request):
        token = req.rel_url.query['refresh_token']
        #header = req.headers
        #req_body = await req.json()
        #method = req.method
        async with ClientSession(trust_env=True) as session:
            async with AsyncSpotifyAuthClient(session, refresh_token=token) as client:
                return await coroutine(Player(client), req)
    return endpoint_with_player


@routes.get('/test')
@get_player
async def songid(player: Player, req: web.Request):
    playback = await player.async_current_playback()
    id = playback['item']['id']
    return web.Response(text=f'this is song {id}')

# @routes.get('/auth')

# @routes.get('/redirect')
# async def authorize(req: web.Request):
#     code = req.rel_url.query['code']
#     state = req.rel_url.query['state']
#     if code and state in states:
#         async with ClientSession(trust_env=True) as session:
#             async with AsyncSpotifyAuthClient(session, code=code) as client:
#                 #refresh_token = client.refresh_token
#                 #store_refresh_token(refresh_token, state)
#                 raise web.HTTPFound('/loginsuccess')
#     raise web.HTTPFound('/loginfailure')


app = web.Application()
app.add_routes(routes)
web.run_app(app)