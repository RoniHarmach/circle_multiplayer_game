import socket
from dataclasses import dataclass
from typing import Optional

from player_data import PlayerData


@dataclass
class PlayerState:
    client_socket: socket
    player_data: Optional[PlayerData] = None
    player_ready: bool = False
