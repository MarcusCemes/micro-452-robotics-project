from aiohttp import WSMsgType, web
from rich.console import Console

_connections = set()
_console = Console()
_site = None
_state: dict[str, object] = {}


async def update_state(patch: dict[str, object]):
    global _state
    _state = _state | patch

    for ws in _connections:
        await ws.send_json({"type": "patch", "data": patch})


async def websocket_handler(request):
    global _state

    ws = web.WebSocketResponse()
    await ws.prepare(request)

    _console.print("WebSocket connection established")
    await ws.send_json({"type": "msg", "data": "Hi!"})
    await ws.send_json({"type": "state", "data": _state})

    _connections.add(ws)

    async for msg in ws:
        if msg.type == WSMsgType.TEXT:
            print(msg.json())
            pass

    _console.print("WebSocket closed")
    _connections.remove(ws)
    return ws


def create_app():
    app = web.Application()
    app.add_routes([web.get('/ws', websocket_handler)])
    return app


async def start_server(host="127.0.0.1", port=8080):
    global _site

    app = create_app()
    runner = web.AppRunner(app)
    await runner.setup()

    _site = web.TCPSite(runner)
    await _site.start()

    _console.print(f"Server on http://{host}:{port}")


async def stop_server():
    global _site

    if not _site is None:
        await _site.stop()
        _site = None
