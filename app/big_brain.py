
from asyncio import Event
from tdmclient.thymio import Node


async def start_thinking(_: Node):
    await Event().wait()
