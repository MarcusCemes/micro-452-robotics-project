from dataclasses import dataclass,  field

from tdmclient import ClientAsyncCacheNode

from app.parallel import Pool
from app.state import State
from app.utils.types import Signal


@dataclass
class Context:
    node: ClientAsyncCacheNode
    pool: Pool
    state: State
    scene_update: Signal = Signal()
    pose_update: Signal = Signal()
