from enum import Enum


class ProtocolCodes(Enum):
    CREATE_PLAYER = "CRPL"
    START_GAME = "STRT"
    PLAYER_STATE = "PLST"
    PLAYER_MOVED = "PLMV"