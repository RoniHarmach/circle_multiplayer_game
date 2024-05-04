from typing import Any
from dataclasses import dataclass
from server_event_types import ServerEventType
from typing import Optional


@dataclass
class GameEvent:
    code: ServerEventType
    message: Optional[Any] = None
    player_number: Optional[int] = None
