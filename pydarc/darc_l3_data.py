import bitstring
from enum import IntEnum


class DarcL3DataPacketServiceIdentificationCode(IntEnum):
    UNDEFINED_0 = 0x0
    TRANSMISSION_1_MODE = 0x1
    TRANSMISSION_2_MODE = 0x2
    TRANSMISSION_3_MODE = 0x3
    TRANSMISSION_4_MODE = 0x4
    TRANSMISSION_5_MODE = 0x5
    TRANSMISSION_6_MODE = 0x6
    TRANSMISSION_7_MODE = 0x7
    TRANSMISSION_8_MODE = 0x8
    TRANSMISSION_9_MODE = 0x9
    UNDEFINED_A = 0xA
    UNDEFINED_B = 0xB
    UNDEFINED_C = 0xC
    ADDITIONAL_INFORMATION = 0xD
    AUXILIARY_SIGNAL = 0xE
    OPERATIONAL_SIGNAL = 0xF


class DarcL3DataPacket:
    """DARC L3 Data Packet"""

    @staticmethod
    def from_buffer(buffer: bytes):
        """Construct from buffer

        Args:
            buffer (bytes): Buffer

        Raises:
            ValueError: Invalid buffer length

        Returns:
            DarcL3DataPacket: DarcL3DataPacket instance
        """
        buffer: bitstring.Bits = bitstring.Bits(buffer)
        if len(buffer) != 176:
            raise ValueError("Invalid buffer length.")

        service_id = DarcL3DataPacketServiceIdentificationCode(buffer[0:4][::-1].uint)
        decode_id_flag: int = buffer[4:5].uint
        end_of_information_flag: int = buffer[5:6].uint
        update_flag: int = buffer[6:8][::-1].uint

        data_group_number: int
        data_packet_number: int
        data_block: bitstring.Bits
        if (
            service_id
            == DarcL3DataPacketServiceIdentificationCode.ADDITIONAL_INFORMATION
        ):
            # Composition 2
            data_group_number: int = buffer[8:12][::-1].uint
            data_packet_number: int = buffer[12:16][::-1].uint
            data_block = buffer[16:176]

        else:
            # Composition 1
            data_group_number: int = buffer[8:22][::-1].uint
            data_packet_number: int = buffer[22:32][::-1].uint
            data_block = buffer[32:176]

        return DarcL3DataPacket(
            service_id,
            decode_id_flag,
            end_of_information_flag,
            update_flag,
            data_group_number,
            data_packet_number,
            data_block,
        )

    def __init__(
        self,
        service_id: int,
        decode_id_flag: int,
        end_of_information_flag: int,
        update_flag: int,
        data_group_number: int,
        data_packet_number: int,
        data_block: bitstring.Bits,
    ):
        """Constructor

        Args:
            service_id (int): Service ID
            decode_id_flag (int): Decode ID flag
            end_of_information_flag (int): End of information flag
            update_flag (int): Update flag
            data_group_number (int): Data Group number
            data_packet_number (int): Data Packet number
            data_block (bitstring.Bits): Data Block
        """
        self.service_id = service_id
        self.decode_id_flag = decode_id_flag
        self.end_of_information_flag = end_of_information_flag
        self.update_flag = update_flag
        self.data_group_number = data_group_number
        self.data_packet_number = data_packet_number
        self.data_block = data_block
