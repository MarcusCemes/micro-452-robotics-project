from asyncio import sleep

from app.global_navigation import calculate_path
from app.server import update_state


async def start_thinking():
    await update_state({"start": (3, 3), "end": (13, 13), "pos": (3, 8), "path": []})

    while True:
        path = await calculate_path()
        await update_state({"path": path})
        await sleep(5)
