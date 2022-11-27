from asyncio import create_task, run, sleep
from rich.padding import Padding
from rich.panel import Panel
from tdmclient import ClientAsync

from app.big_brain import BigBrain
from app.console import *
from app.context import Context
from app.parallel import Pool
from app.server import Server
from app.state import State


def main():
    print_banner()

    try:
        run(connect())

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
        with Pool() as pool:
            with ClientAsync() as client:
                status.update("Waiting for Thymio node")

                with await client.lock() as node:
                    status.stop()

                    info("Connected")
                    debug(f"Node lock on {node}")

                    # Signal the Thymio to broadcast variable changes
                    await node.watch(variables=True)

                    # Start processing Thymio messages
                    create_task(process_messages(client))

                    ctx = Context(node, pool, State())

                    async with Server(ctx):
                        await BigBrain(ctx).start_thinking()

    except ConnectionRefusedError:
        warning("Thymio driver connection refused")

    except ConnectionResetError:
        warning("Thymio driver connection closed")

    finally:
        status.stop()


async def process_messages(client: ClientAsync):
    try:
        while True:
            client.process_waiting_messages()
            await sleep(0.05)

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
