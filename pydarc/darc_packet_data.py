from enum import IntEnum
from typing import NamedTuple, Union


class DarcBlockIdentificationCode(IntEnum):
    UNDEFINED = 0x0000
    BIC_1 = 0x135E
    BIC_2 = 0x74A6
    BIC_3 = 0xA791
    BIC_4 = 0xC875


class DarcDataPacket(NamedTuple):
    bic: DarcBlockIdentificationCode
    data_packet: bytes
    crc: int
    parity: int


class DarcParityPacket(NamedTuple):
    bic: DarcBlockIdentificationCode
    parity: int


DarcPacket = Union[DarcDataPacket, DarcParityPacket]
