from typing import Any
from aiohttp import WSMsgType, web
from rich.console import Console
from app.global_navigation import recalculate_path

from app.state import state

_connections = set()
_console = Console()


class Server:
    site = None

    async def __aenter__(self, host="127.0.0.1", port=8080):
        app = create_app()
        runner = web.AppRunner(app)
        await runner.setup()

        self.site = web.TCPSite(runner)
        await self.site.start()

        _console.print(f"Server on http://{host}:{port}")

    async def __aexit__(self, *_):
        if self.site:
            await self.site.stop()
            self.site = None


async def send_patch(patch: dict[str, object]):
    for ws in _connections:
        await ws.send_json({"type": "patch", "data": patch})


async def websocket_handler(request):

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    _console.print("WebSocket connection established")
    await ws.send_json({"type": "msg", "data": "Hi!"})
    await ws.send_json({"type": "state", "data": state.json()})

    _connections.add(ws)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            await handle_message(msg.json())

    _console.print("WebSocket closed")
    _connections.remove(ws)
    return ws


async def handle_message(msg: Any):
    request_path_calculation = False

    match msg["type"]:
        case "set_start":
            state.start = msg["data"]
            request_path_calculation = True

        case "set_end":
            state.end = msg["data"]
            request_path_calculation = True

        case "add_obstacle":
            state.obstacles.append(msg["data"])
            request_path_calculation = True

    if request_path_calculation:
        (path, computation_time) = recalculate_path()
        state.path = path
        state.computation_time = computation_time

    await send_patch(state.json())


def create_app():
    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler)])
    return app
