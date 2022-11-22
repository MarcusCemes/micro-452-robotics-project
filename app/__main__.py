import asyncio

from aiofiles import open
from rich.padding import Padding
from rich.panel import Panel
from tdmclient import ClientAsync

from app.big_brain import start_thinking
from app.console import *
from app.parallel import Pool
from app.server import Server


def main():
    print_banner()

    try:
        asyncio.run(connect())

    except KeyboardInterrupt:
        warning("Interrupted by user")

    except Exception:
        critical("Program crashed")
        console.print_exception()

    finally:
        print("")


def print_banner():
    console.print(
        Padding(
            Panel(
                "[bold white]Big Brain - Thymio Controller\n"
                + "[grey42]MICRO-452 - Mobile Robotics\n"
                + "École Polytechnique Fédérale de Lausanne"
            ),
            (1, 2),
        ), justify="left")


async def connect():
    status = console.status(
        "Connecting to Thymio driver", spinner_style="cyan")
    status.start()

    try:
        with Pool() as client:
            with ClientAsync() as client:
                status.update("Waiting for Thymio node")

                with await client.lock() as node:
                    status.stop()

                    info("Connected")
                    debug(f"Node lock on {node}")

                    async with Server():
                        await start_thinking(node)

    except ConnectionRefusedError:
        warning("Thymio driver connection refused")

    except ConnectionResetError:
        warning("Thymio driver connection closed")

    finally:
        status.stop()


if __name__ == "__main__":
    main()
