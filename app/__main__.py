from asyncio import create_task, run, sleep

import numpy as np
from rich.padding import Padding
from rich.panel import Panel
from tdmclient import ClientAsync

from app.big_brain import BigBrain
from app.config import DEBUG, PROCESS_MSG_INTERVAL, RAISE_DEPRECATION_WARNINGS
from app.context import Context
from app.parallel import Pool
from app.server import Server
from app.state import State
from app.utils.console import *
from app.vision import close_capture_source


def main():
    print_banner()

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
        close_capture_source()
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


async def init():
    status = console.status(
        "Connecting to Thymio driver", spinner_style="cyan")

    status.start()

    try:
        with Pool() as pool:
            with ClientAsync() as client:
                status.update("Waiting for Thymio node")
                debug(client.nodes)
                with await client.lock() as node:

                    info("Principal node connected")
                    debug(f"Node lock on {node}")

                    # Signal the Thymio to broadcast variable changes
                    await node.watch(variables=True)

                    status.stop()
                    # wantSecondThymio = input("Do you want a second thymio to be connected? (y/n): ")
                    wantSecondThymio = False
                    status.start()

                    if wantSecondThymio == "y":

                        status.update("Waiting for second Thymio node")

                        with await client.nodes[1].lock() as secondary_node:

                            status.stop()
                            status = None

                            info("Secondary node connected")
                            debug(f"Secondary Node lock on {secondary_node}")

                            # Start processing Thymio messages
                            create_task(process_messages(client))

                            ctx = Context(node, secondary_node, pool, State())

                            async with Server(ctx):
                                brain = BigBrain(ctx)
                                await brain.start_thinking()
                    else:
                        debug("single node mode selected")
                        status.stop()
                        status = None

                        # Start processing Thymio messages
                        create_task(process_messages(client))

                        ctx = Context(node, None, pool, State())

                        async with Server(ctx):
                            brain = BigBrain(ctx)
                            await brain.start_thinking()    
                

    except ConnectionRefusedError:
        warning("Thymio driver connection refused")

    except ConnectionResetError:
        warning("Thymio driver connection closed")

    finally:
        if status:
            status.stop()


async def process_messages(client: ClientAsync):
    try:
        while True:
            client.process_waiting_messages()
            await sleep(PROCESS_MSG_INTERVAL)

    except Exception:
        pass

if __name__ == "__main__":
    main()
