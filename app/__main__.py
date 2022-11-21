import asyncio
import pathlib

from aiofiles import open
from tdmclient import ClientAsync
from tdmclient.atranspiler import ATranspiler

from app.big_brain import start_thinking
from app.console import *
from app.parallel import Pool
from app.server import Server


def main():
    try:
        asyncio.run(connect())

    except KeyboardInterrupt:
        warning("Interrupted by user")

    except Exception:
        critical("Program crashed")
        console.print_exception()


async def connect():
    status = console.status("Connecting to Thymio driver")
    status.start()

    try:
        with Pool() as client:
            with ClientAsync() as client:
                status.update("Waiting for Thymio node")

                with await client.lock() as node:
                    status.stop()

                    info("Connected")
                    debug(f"Node lock on {node}")

                    await run_program(node)

    except ConnectionRefusedError:
        warning("Thymio driver connection refused")

    except ConnectionResetError:
        warning("Thymio driver connection closed")


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

        debug("Native ASEBA code loaded")


if __name__ == "__main__":
    main()
