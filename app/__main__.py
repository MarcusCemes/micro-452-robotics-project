from asyncio import create_task, run, sleep
from sys import version_info

import numpy as np
from rich.padding import Padding
from rich.panel import Panel
from tdmclient import ClientAsync

from app.big_brain import BigBrain
from app.config import DEBUG, PROCESS_MSG_INTERVAL, RAISE_DEPRECATION_WARNINGS
from app.context import Context
from app.server import Server
from app.state import State
from app.utils.console import *
from app.utils.pool import Pool
from app.utils.types import Channel, Vec2

VERSION_MAJOR = 3
VERSION_MINOR = 10


def main():
    print_banner()
    check_version()

    if RAISE_DEPRECATION_WARNINGS:
        np.warnings.filterwarnings(  # type: ignore
            "error", category=np.VisibleDeprecationWarning)

    try:
        run(init(), debug=DEBUG)

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


def check_version():
    (major, minor, _, _, _) = version_info
    if major < VERSION_MAJOR or minor < VERSION_MINOR:
        console.print("\n".join(
            [
                "[bold red]Python version not supported![/]",
                f"This project uses features from Python {VERSION_MAJOR}.{VERSION_MINOR}",
                f"You have version {major}.{minor}\n"
            ]
        ))

        exit(1)


async def init():
    status = console.status(
        "Connecting to Thymio driver", spinner_style="cyan")

    status.start()

    try:
        with Pool() as pool:
            with ClientAsync() as client:
                status.update("Waiting for Thymio node")

                create_task(process_messages(client))

                with await client.lock() as node:
                    status.stop()

                    ctx = Context(node, None, pool, State())

                    info("Primary node connected")
                    debug(f"Node lock on {node}")

                    # Signal the Thymio to broadcast variable changes
                    await node.watch(variables=True)

                    info("Would you like to connect a second Thymio? [Y/n]")
                    connectSecond = input("> ")

                    if connectSecond.lower() != "n":
                        status.update("Waiting for second Thymio node")
                        status.start()

                        with await client.nodes[1].lock() as secondary_node:
                            ctx.node_top = secondary_node

                            status.stop()
                            status = None

                            info("Secondary node connected")
                            debug(f"Node lock on {secondary_node}")

                            await start(ctx)
                    else:
                        status = None
                        await start(ctx)

    except ConnectionRefusedError:
        warning("Thymio driver connection refused")

    except ConnectionResetError:
        warning("Thymio driver connection closed")

    finally:
        if status:
            status.stop()


async def start(ctx: Context):
    channel_position = Channel[Vec2]()

    async with Server(ctx, channel_position):
        brain = BigBrain(ctx)
        await brain.start_thinking(channel_position)


async def process_messages(client: ClientAsync):
    """Process waiting messages from the Thymio driver."""

    try:
        while True:
            client.process_waiting_messages()
            await sleep(PROCESS_MSG_INTERVAL)

    except Exception:
        pass

if __name__ == "__main__":
    main()
