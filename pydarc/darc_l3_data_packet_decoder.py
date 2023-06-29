from logging import getLogger

from pydarc.darc_l2_data import (
    DarcL2Block,
    DarcL2InformationBlock,
    DarcL2Frame,
)
from pydarc.darc_l3_data import DarcL3DataPacket


class DarcL3DataPacketDecoder:
    """DARC L3 Data Packet Decoder"""

    def push_frame(self, frame: DarcL2Frame) -> list[DarcL3DataPacket]:
        """Push a Frame

        Args:
            frame (DarcL2Frame): Frame

        Returns:
            list[DarcL3DataPacket]: Data Packets
        """
        l2_information_blocks: filter[DarcL2InformationBlock] = filter(
            lambda x: isinstance(x, DarcL2InformationBlock),
            frame.blocks,
        )
        return list(
            map(
                lambda x: DarcL3DataPacket.from_buffer(x.data_packet()),
                l2_information_blocks,
            )
        )
