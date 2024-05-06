from enum import Enum


class ServerEventType(Enum):
    CREATE_PLAYER_REQUEST = 0
    PLAYER_READY = 1
    START_GAME = 2
    PLAYER_MOVED = 3
    ADD_DOT = 4
