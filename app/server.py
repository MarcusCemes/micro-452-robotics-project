from asyncio import create_task
from typing import Any
from aiohttp import WSMsgType, web
from app.global_navigation import recompute_path

from app.console import *
from app.state import state


class Server:
    def __init__(self) -> None:
        self.site = None

    async def __aenter__(self, host="127.0.0.1", port=8080):
        app = create_app()
        runner = web.AppRunner(app)
        await runner.setup()

        self.site = web.TCPSite(runner)
        await self.site.start()

        debug(f"Control server running at ws://{host}:{port}/ws")

    async def __aexit__(self, *_):
        if self.site:
            await self.site.stop()
            self.site = None


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    debug("[server] Client connected")

    try:
        await ws.send_json({"type": "msg", "data": "Hi!"})
        await ws.send_json({"type": "state", "data": state.json()})

        tx = create_task(handle_tx(ws))
        await handle_rx(ws)

        tx.cancel()
        debug("[server] Client disconnected")

    except ConnectionResetError:
        pass

    return ws


async def handle_tx(ws: web.WebSocketResponse):
    while True:
        await state.wait_for_stale()
        await ws.send_json({"type": "patch", "data": state.json()})


async def handle_rx(ws: web.WebSocketResponse):
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            create_task(handle_message(msg.json(), ws))


async def handle_message(msg: Any, ws: web.WebSocketResponse):
    match msg["type"]:
        case "ping":
            id = msg["data"]
            await ws.send_json({"type": "pong", "data": id})

        case "set_start":
            state.start = msg["data"]

        case "set_end":
            state.end = msg["data"]

        case "add_obstacle":
            state.obstacles.append(msg["data"])

    state.mark_stale()
    await recompute_path()


def create_app():
    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler)])
    return app
