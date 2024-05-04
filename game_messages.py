from dataclasses import dataclass

from typing import List, Dict, Optional, Tuple
from dot_data import DotData
from player_data import PlayerData


@dataclass
class GameInitMessage:
    player_data: PlayerData
    other_players: Dict[int, PlayerData]
    dots: Dict[int, DotData]


@dataclass
class GameStateChangeMessage:
    players: List[PlayerData]
    removed_dots: Optional[List[int]] = None

@dataclass
class PlayerMovementMessage:
    player_number: int
    coords: Tuple[int, int]

