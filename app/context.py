from dataclasses import dataclass

from tdmclient import ClientAsyncCacheNode

from app.utils.pool import Pool
from app.state import State
from app.utils.types import Signal


@dataclass
class Context:
    """
    Shared application context, providing access to resources used
    by different modules.
    """

    node: ClientAsyncCacheNode
    node_top: ClientAsyncCacheNode | None
    pool: Pool
    state: State
    scene_update: Signal = Signal()
    pose_update: Signal = Signal()
    debug_update: bool = False
