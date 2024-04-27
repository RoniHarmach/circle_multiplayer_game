from dataclasses import dataclass
from protocol_codes import ProtocolCodes


@dataclass
class UserEventMessage:
    code: ProtocolCodes
    data: bytes
