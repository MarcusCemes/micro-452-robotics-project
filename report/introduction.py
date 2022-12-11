from asyncio import create_task, sleep

from app.state import State

live_state = State()


async def scenario_state_patches():
    state = State()

    listeners = [state.register_listener() for _ in range(3)]
    tasks = [create_task(print_patches(i, listener, i))
             for i, listener in enumerate(listeners)]

    state.position = (1, 1)
    state.changed()
    await sleep(1)

    state.orientation = 1
    state.changed()
    await sleep(1)

    state.position = (2, 2)
    state.orientation = 2
    state.changed()
    await sleep(3)

    for task in tasks:
        task.cancel()


async def print_patches(id, listener, delay=0):
    while True:
        await listener.wait_for_patch()

        if delay:
            await sleep(delay)

        print(
            f"Task {id} received patch {listener.get_patch()} after sleeping for {delay} seconds")
