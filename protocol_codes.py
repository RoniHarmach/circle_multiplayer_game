from enum import Enum


class ProtocolCodes(Enum):
    CREATE_PLAYER_REQUEST = "CRPR"
    CREATE_PLAYER = "CRPL"
    PLAYER_READY = "PLRD"
    START_GAME = "STRT"
    PLAYER_MOVED = "PLMV"
    GAME_STATE_CHANGE = "GMSC"
    GAME_INIT = "GMIT"
    LOAD_ENTRY_SCREEN = "LDSC"