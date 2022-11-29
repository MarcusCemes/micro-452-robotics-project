from asyncio import create_task
from traceback import print_exception
from typing import Any

from aiohttp import WSMsgType
from aiohttp.web import (Application, AppRunner, Request, TCPSite,
                         WebSocketResponse, get)

from app.context import Context
from app.state import State, normalise_obstacle
from app.utils.console import *


class Server:
    def __init__(self, ctx: Context) -> None:
        self.site = None
        self.ctx = ctx

    async def __aenter__(self, host="127.0.0.1", port=8080):
        app = create_app(self.ctx)
        runner = AppRunner(app)
        await runner.setup()

        self.site = TCPSite(runner)
        await self.site.start()

        debug(f"Control server running at ws://{host}:{port}/ws")

    async def __aexit__(self, *_):
        if self.site:
            await self.site.stop()
            self.site = None


async def websocket_handler(request: Request):
    ctx: Context = request.app["ctx"]

    ws = WebSocketResponse()
    await ws.prepare(request)

    debug("[server] Client connected")

    try:
        await ws.send_json({"type": "msg", "data": "Hi!"})
        await ws.send_json({"type": "state", "data": ctx.state.__dict__})

        tx = create_task(handle_tx(ws, ctx.state))
        await handle_rx(ws, ctx)

        tx.cancel()
        debug("[server] Client disconnected")

    except ConnectionResetError:
        pass

    except Exception as e:
        error("[server] Error sending initial state!")
        print_exception(e)
        print(ctx.state)

        print("type of relative_distances", type(
            ctx.state.relative_distances[0]))

        if ctx.state.prox_sensors:
            print("type of prox_sensors", type(ctx.state.prox_sensors[0]))

    return ws


async def handle_tx(ws: WebSocketResponse, state: State):
    try:
        while True:
            await state.wait_changed()
            await ws.send_json({"type": "patch", "data": state.__dict__})

    except ConnectionResetError:
        pass

    except Exception as e:
        error("[server] Error sending patch!")
        print_exception(e)
        print(state)


async def handle_rx(ws: WebSocketResponse, ctx: Context):
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            create_task(handle_message(msg.json(), ws, ctx))


async def handle_message(msg: Any, ws: WebSocketResponse, ctx: Context):
    match msg["type"]:
        case "ping":
            id = msg["data"]
            await ws.send_json({"type": "pong", "data": id})

        case "set_start":
            ctx.state.start = msg["data"]
            ctx.scene_update.trigger()

        case "set_end":
            ctx.scene_update.trigger()
            ctx.state.end = msg["data"]

        case "add_obstacle":
            ctx.state.extra_obstacles.append(normalise_obstacle(msg["data"]))
            ctx.scene_update.trigger()

        case "clear_obstacles":
            ctx.state.extra_obstacles = []
            ctx.scene_update.trigger()

    ctx.state.changed()
    ctx.scene_update.trigger()


def create_app(ctx: Context):
    app = Application()
    app["ctx"] = ctx

    app.add_routes([get('/ws', websocket_handler)])
    return app
