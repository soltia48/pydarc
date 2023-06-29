import bitstring
from enum import IntEnum

from pydarc.crc_14_darc import crc_14_darc
from pydarc.crc_82_darc import correct_error_dscc_272_190


class DarcL2BlockIdentificationCode(IntEnum):
    UNDEFINED = 0x0000
    BIC_1 = 0x135E
    BIC_2 = 0x74A6
    BIC_3 = 0xA791
    BIC_4 = 0xC875


class DarcL2Block:
    """DARC L2 Block"""

    def __init__(
        self, block_id: DarcL2BlockIdentificationCode, payload: bitstring.Bits
    ):
        """Constructor

        Args:
            block_id (DarcL2BlockIdentificationCode): Block ID
            payload (bytes): Payload
        """
        self.block_id = block_id

        if len(payload) != 272:
            raise ValueError("Invalid buffer length.")

        # Correct error
        error_corrected_payload = correct_error_dscc_272_190(payload)
        if error_corrected_payload is not None:
            payload = error_corrected_payload

        self.payload = payload[0:190]


class DarcL2InformationBlock(DarcL2Block):
    """DARC L2 Information Block"""

    def data_packet(self) -> bytes:
        """Get Data Packet

        Returns:
            bytes: Data Packet
        """
        return self.payload[0:176].bytes

    def crc(self) -> int:
        """Get recorded CRC value

        Returns:
            int: Recorded CRC value
        """
        return self.payload[176:190].uint

    def is_crc_valid(self) -> bool:
        """Is CRC valid

        Returns:
            bool: True if CRC is valid, else False
        """
        return crc_14_darc(self.data_packet()) == self.crc()


class DarcL2ParityBlock(DarcL2Block):
    """DARC L2 Parity Block"""

    def vertical_parity(self) -> bytes:
        """Get vertical parity

        Returns:
            bytes: Vertical parity
        """
        return self.payload.bytes


class DarcL2Frame:
    """DARC L2 Frame"""

    @staticmethod
    def __correct_error_dscc_272_190(buffer: bitstring.Bits) -> bitstring.Bits:
        """Correct error with Difference Set Cyclic Codes (272,190)

        Args:
            buffer (bitstring.Bits): Buffer

        Returns:
            bitstring.Bits: Error corrected buffer. However, return original If cannot correct error
        """
        error_corrected_buffer = correct_error_dscc_272_190(buffer)
        if error_corrected_buffer is not None:
            buffer = error_corrected_buffer
        return buffer

    @staticmethod
    def from_block_buffer(
        block_buffer: list[DarcL2InformationBlock | DarcL2ParityBlock],
    ):
        """Construct from Block buffer

        Args:
            block_buffer (list[DarcL2InformationBlock  |  DarcL2ParityBlock]): Block buffer

        Raises:
            ValueError: Invalid block_buffer length

        Returns:
            DarcL2Frame: DarcL2Frame instance
        """
        if len(block_buffer) != 272:
            raise ValueError("Invalid block_buffer length.")

        # Copy information blocks
        blocks = list(
            filter(lambda x: isinstance(x, DarcL2InformationBlock), block_buffer)
        )
        # Copy parity blocks
        blocks.extend(filter(lambda x: isinstance(x, DarcL2ParityBlock), block_buffer))

        # Create payload 2D buffer
        payload_2d_buffer = list(map(lambda x: bitstring.Bits(x.payload), blocks))
        # Rotate left
        left_rotated_payload_2d_buffer: list[bitstring.Bits] = map(
            lambda x: bitstring.Bits(x), list(zip(*payload_2d_buffer))[::-1]
        )
        # Correct error with vertical parity
        left_rotated_payload_2d_buffer = map(
            DarcL2Frame.__correct_error_dscc_272_190, left_rotated_payload_2d_buffer
        )
        # Rotate right
        payload_2d_buffer = list(
            map(
                lambda x: bitstring.Bits(x),
                zip(*list(left_rotated_payload_2d_buffer)[::-1]),
            )
        )

        for block, payload_buffer in zip(blocks, payload_2d_buffer):
            block.payload = payload_buffer

        return DarcL2Frame(blocks)

    def __init__(self, blocks: list[DarcL2InformationBlock | DarcL2ParityBlock]):
        """Constructor

        Args:
            blocks (list[DarcL2InformationBlock | DarcL2ParityBlock]): Blocks
        """
        self.blocks = blocks
