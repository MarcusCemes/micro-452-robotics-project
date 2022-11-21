from asyncio import gather
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

    await ws.send_json({"type": "msg", "data": "Hi!"})
    await ws.send_json({"type": "state", "data": state.json()})

    await gather(handle_tx(ws), handle_rx(ws))

    debug("[server] Client connected")

    return ws


async def handle_tx(ws: web.WebSocketResponse):
    while True:
        await state.wait_for_stale()
        await ws.send_json({"type": "patch", "data": state.json()})


async def handle_rx(ws: web.WebSocketResponse):
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            await handle_message(msg.json())


async def handle_message(msg: Any):

    match msg["type"]:
        case "set_start":
            state.start = msg["data"]
            await recompute_path()

        case "set_end":
            state.end = msg["data"]
            await recompute_path()

        case "add_obstacle":
            state.obstacles.append(msg["data"])
            await recompute_path()


def create_app():
    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler)])
    return app
