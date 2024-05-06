from dataclasses import dataclass
from typing import Tuple


@dataclass
class DotData:
    id: int
    coord: Tuple[int, int]
    color: str
    radius: int
    points: int
    increase: int
