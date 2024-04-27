import socket
from dataclasses import dataclass
from player_data import PlayerData


@dataclass
class PlayerState:
    player_data: PlayerData
    client_socket: socket
