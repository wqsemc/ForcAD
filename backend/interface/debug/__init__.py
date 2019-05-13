import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, BASE_DIR)

import asyncio

from sanic import Sanic
from sanic.response import html, json
import storage
from aioredis.pubsub import Receiver

import socketio

sio = socketio.AsyncServer(async_mode='sanic')
app = Sanic()
sio.attach(app)


@app.listener('before_server_start')
async def before_server_start(_sanic, loop):
    mpsc = Receiver(loop=loop)
    redis = await storage.get_async_redis_pool(loop)
    await redis.subscribe(
        mpsc.channel('scoreboard'),
        mpsc.channel('stolen_flags'),
    )
    sio.start_background_task(background_task, mpsc)


async def background_task(mpsc):
    async for channel, msg in mpsc.iter():
        try:
            message = msg.decode()
        except AttributeError:
            pass
        else:
            print(message, channel, channel.name)
            if channel.name == b'stolen_flags':
                print('Emitting flag stolen event')
                await sio.emit('flag_stolen', {'data': message}, namespace='/test')
            elif channel.name == b'scoreboard':
                print('Emitting scoreboard event')
                await sio.emit('update_scoreboard', {'data': message}, namespace='/test')


@sio.on('connect', namespace='/test')
async def test_connect(_sid, _environ):
    loop = asyncio.get_event_loop()
    game_state = await storage.game.get_game_state_async(loop)

    teams = await storage.teams.get_teams_async(loop)
    teams = [team.to_json() for team in teams]
    tasks = await storage.tasks.get_tasks_async(loop)
    tasks = [task.to_json_for_participants() for task in tasks]
    if not game_state:
        state = ''
    else:
        state = game_state.to_json()

    await sio.emit(
        'init_scoreboard',
        {
            'data': {
                'state': state,
                'teams': teams,
                'tasks': tasks,
            }
        },
        namespace='/test'
    )


@app.route('/api/teams/')
async def get_teams(_request):
    teams = await storage.teams.get_teams_async(asyncio.get_event_loop())
    teams = [team.to_json() for team in teams]
    return json(teams)


@app.route('/api/tasks/')
async def get_tasks(_request):
    tasks = await storage.tasks.get_tasks_async(asyncio.get_event_loop())
    tasks = [task.to_json() for task in tasks]
    return json(tasks)


@app.route('/')
async def index(_request):
    with open('templates/app.html') as f:
        return html(f.read())


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)