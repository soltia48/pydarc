import bitstring
from pydarc.crc_14_darc import crc_14_darc
from pydarc.crc_82_darc import crc_82_darc, generate_bitflip_syndrome_map
from pydarc.customized_logger import getLogger
from pydarc.darc_packet_data import (
    DarcBlockIdentificationCode,
    DarcDataPacket,
    DarcParityPacket,
)
from pydarc.lfsr import lfsr


class DarcL2PacketDecoder:
    """DARC L2 Packet Decoder"""

    __logger = getLogger("DarcL2PacketDecoder")

    __current_bic = 0x0000
    __data_buffer: bitstring.BitStream = bitstring.BitStream()
    __lfsr = lfsr(0x155, 0x110)
    __parity_bitflip_syndrome_map = generate_bitflip_syndrome_map(272, 8)

    def __is_packet_detected(self):
        return (
            self.__current_bic == DarcBlockIdentificationCode.BIC_1
            or self.__current_bic == DarcBlockIdentificationCode.BIC_2
            or self.__current_bic == DarcBlockIdentificationCode.BIC_3
            or self.__current_bic == DarcBlockIdentificationCode.BIC_4
        )

    def __is_data_packet_detected(self):
        return (
            self.__current_bic == DarcBlockIdentificationCode.BIC_1
            or self.__current_bic == DarcBlockIdentificationCode.BIC_2
            or self.__current_bic == DarcBlockIdentificationCode.BIC_3
        )

    def __is_parity_packet_detected(self):
        return self.__current_bic == DarcBlockIdentificationCode.BIC_4

    def __decode_packet(self):
        if self.__is_data_packet_detected():
            bic = DarcBlockIdentificationCode(self.__current_bic)
            data_packet = self.__data_buffer[0:176].bytes
            crc = self.__data_buffer[176:190].uint << 2
            parity = self.__data_buffer[190:272].uint

            if crc_14_darc(data_packet) << 2 != crc:
                syndrome = crc_82_darc(self.__data_buffer)
                self.__logger.debug(
                    f"CRC mismatch. Try correct error with parity. syndrome={hex(syndrome)}"
                )
                try:
                    error_vector = self.__parity_bitflip_syndrome_map[syndrome]
                    self.__logger.debug(
                        f"Error vector found. error_vector={error_vector.hex}"
                    )
                    self.__data_buffer ^= error_vector
                except KeyError:
                    self.__logger.warning(
                        "Error vector not found. Cannot correct error."
                    )
                    return

                data_packet = self.__data_buffer[0:176].bytes
                crc = self.__data_buffer[176:190].uint << 2

                if crc_14_darc(data_packet) << 2 != crc:
                    self.__logger.warning("CRC mismatch. Failed to correct error.")
                    return
                self.__logger.debug("Error was corrected.")

            return DarcDataPacket(bic, data_packet, crc, parity)
        else:
            bic = DarcBlockIdentificationCode(self.__current_bic)
            parity = self.__data_buffer.uint
            return DarcParityPacket(bic, parity)

    def push_bit(self, bit: int):
        if self.__is_packet_detected():
            bit ^= next(self.__lfsr)
            self.__data_buffer += "0b0" if bit == 0 else "0b1"

            if len(self.__data_buffer) == 272:
                packet = self.__decode_packet()

                self.__current_bic = 0x0000
                self.__data_buffer.clear()
                self.__lfsr = lfsr(0x155, 0x110)

                return packet

        else:
            self.__current_bic = ((self.__current_bic << 1) | bit) & 0xFFFF
