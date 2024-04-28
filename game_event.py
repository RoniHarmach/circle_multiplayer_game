from typing import Any
from dataclasses import dataclass
from protocol_codes import ProtocolCodes
from typing import Optional


@dataclass
class GameEvent:
    code: ProtocolCodes
    message: Optional[Any] = None
    player_number: Optional[int] = None
