import asyncio
from sys import exit

from aiofiles import open
from rich.console import Console
from tdmclient import ClientAsync
from tdmclient.atranspiler import ATranspiler

from app.big_brain import start_thinking
from app.server import start_server, stop_server

_console = Console()


def main():
    _console.print("Connecting...")

    try:
        asyncio.run(connect())

    except KeyboardInterrupt:
        _console.print("[yellow]Interrupt")

    except Exception as e:
        _console.print("[red]Core program error:[/red]")
        _console.print(e)
        exit(1)


async def connect():
    try:
        with ClientAsync() as client:
            _console.print("Waiting for Thymio robot...")

            with await client.lock() as node:
                _console.print(f"[green]Connected[/green] to {node}")
                await run_program(node)

    except ConnectionRefusedError:
        _console.print("[yellow]Could not connect to Thymio driver[/yellow]")


async def run_program(node):
    await start_server()

    try:
        await load_native_code(node)
        await start_thinking()

    finally:
        await stop_server()


async def load_native_code(node):
    async with open("app/controller.py", mode="r") as f:
        aseba = ATranspiler.simple_transpile(await f.read())
        await node.compile(aseba)
        await node.run()
        _console.print("Native code loaded")


if __name__ == "__main__":
    main()
