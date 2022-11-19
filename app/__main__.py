import asyncio
import pathlib

from aiofiles import open
from rich.console import Console
from tdmclient import ClientAsync
from tdmclient.atranspiler import ATranspiler

from app.big_brain import start_thinking
from app.server import Server

_console = Console()


def main():
    _console.print("Connecting...")

    try:
        asyncio.run(connect())

    except KeyboardInterrupt:
        _console.print("[yellow]Interrupt")

    except Exception as e:
        _console.print("[red]Core program error[/red]")
        raise e


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
    async with Server():
        await load_native_code(node)
        await start_thinking()


async def load_native_code(node):
    current_path = pathlib.Path(__file__).parent.resolve()
    controller_path = current_path / "controller.py"

    async with open(controller_path, mode="r") as f:
        aseba = ATranspiler.simple_transpile(await f.read())
        await node.compile(aseba)
        await node.run()
        _console.print("Native code loaded")


if __name__ == "__main__":
    main()
