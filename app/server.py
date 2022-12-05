from asyncio import create_task
from traceback import print_exc
from typing import Any

from aiohttp import WSMsgType
from aiohttp.web import (Application, AppRunner, Request, TCPSite,
                         WebSocketResponse, get)

from app.context import Context
from app.filtering import Filtering
from app.state import ChangeListener, normalise_obstacle
from app.utils.console import *

filteringModule: Filtering | None = None


def setFilteringModule(filtering: Filtering):
    global filteringModule
    filteringModule = filtering


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

    debug("\\[server] Client connected")

    try:
        listener = ctx.state.register_listener()

        await ws.send_json({"type": "msg", "data": "Hi!"})
        await ws.send_json({"type": "state", "data": ctx.state.json()})

        tx = create_task(handle_tx(ws, listener))
        await handle_rx(ws, ctx)

        tx.cancel()
        debug("\\[server] Client disconnected")

    except ConnectionResetError:
        pass

    except Exception:
        error("\\[server] Error sending initial state!")
        print_exc()
        print(ctx.state)

        print("type of relative_distances", type(
            ctx.state.relative_distances[0]))

        if ctx.state.prox_sensors:
            print("type of prox_sensors", type(ctx.state.prox_sensors[0]))

    return ws


async def handle_tx(ws: WebSocketResponse, listener: ChangeListener):
    try:
        while True:
            await listener.wait_for_patch()
            await ws.send_json({"type": "patch", "data": listener.get_patch()})

    except ConnectionResetError:
        pass

    except Exception:
        error("\\[server] Error sending patch!")
        print_exc()


async def handle_rx(ws: WebSocketResponse, ctx: Context):
    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            create_task(handle_message(msg.json(), ws, ctx))


async def handle_message(msg: Any, ws: WebSocketResponse, ctx: Context):
    match msg["type"]:
        case "ping":
            id = msg["data"]
            await ws.send_json({"type": "pong", "data": id})

        case "set_position":
            if filteringModule:
                for _ in range(0, 10):
                    filteringModule.update((*msg["data"], 0))

        case "set_end":
            ctx.state.end = msg["data"]

        case "add_obstacle":
            ctx.state.extra_obstacles.append(normalise_obstacle(msg["data"]))

            # Reassign to trigger change event
            ctx.state.extra_obstacles = ctx.state.extra_obstacles

        case "clear_obstacles":
            ctx.state.extra_obstacles = []

        case "optimise":
            ctx.state.optimise = msg["data"]

        case "stop":
            ctx.node.send_set_variables({
                "motor.left.target": [0],
                "motor.right.target": [0],
            })

            exit()

    ctx.state.changed()
    ctx.scene_update.trigger()
    debug("Scene updated")


def create_app(ctx: Context):
    app = Application()
    app["ctx"] = ctx

    app.add_routes([get('/ws', websocket_handler)])
    return app
