
from asyncio import Event


async def start_thinking():
    await Event().wait()
