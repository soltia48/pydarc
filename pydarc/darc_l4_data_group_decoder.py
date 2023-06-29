import bitstring
from logging import getLogger

from pydarc.darc_l3_data import (
    DarcL3DataPacketServiceIdentificationCode,
    DarcL3DataPacket,
)
from pydarc.darc_l4_data import DarcL4DataGroup1, DarcL4DataGroup2


class DarcL4DataGroupDecoder:
    """DARC L4 Data Group Decoder"""

    __logger = getLogger(__name__)

    def __init__(self) -> None:
        """Constructor"""
        self.__data_group_buffers: dict[tuple[int, int], bitstring.Bits] = {}

    def push_data_packets(
        self, data_packets: list[DarcL3DataPacket]
    ) -> list[DarcL4DataGroup1 | DarcL4DataGroup2]:
        """Push Data Packets

        Args:
            data_packets (list[DarcL3DataPacket]): Data Packets

        Returns:
            list[DarcL4DataGroup1 | DarcL4DataGroup2]: Data Groups
        """
        data_groups: list[DarcL4DataGroup1 | DarcL4DataGroup2] = []

        for data_packet in data_packets:
            data_group_key = (data_packet.service_id, data_packet.data_group_number)
            data_group_buffer = self.__data_group_buffers.get(data_group_key)
            if data_group_buffer is None:
                if data_packet.data_packet_number != 0:
                    self.__logger.debug(
                        f"First Data Packet not found. service_id={hex(data_packet.service_id)} data_group_number={hex(data_packet.data_group_number)} data_packet_number={hex(data_packet.data_packet_number)}"
                    )
                    continue

                self.__data_group_buffers[data_group_key] = data_packet.data_block
            else:
                self.__data_group_buffers[data_group_key] += data_packet.data_block

            if data_packet.end_of_information_flag == 1:
                data_group_buffer = self.__data_group_buffers.pop(data_group_key)
                data_group: DarcL4DataGroup1 | DarcL4DataGroup2
                if (
                    data_packet.service_id
                    == DarcL3DataPacketServiceIdentificationCode.ADDITIONAL_INFORMATION
                ):
                    data_group = DarcL4DataGroup2(
                        data_packet.service_id,
                        data_packet.data_group_number,
                        data_group_buffer,
                    )
                else:
                    data_group = DarcL4DataGroup1(
                        data_packet.service_id,
                        data_packet.data_group_number,
                        data_group_buffer,
                    )

                data_groups.append(data_group)

        return data_groups
