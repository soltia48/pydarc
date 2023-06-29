import bitstring

from pydarc.bit_operations import reverse_bits
from pydarc.crc_16_darc import crc_16_darc
from pydarc.darc_l3_data import DarcL3DataPacketServiceIdentificationCode


class DarcL4DataGroup:
    """Darc L4 Data Group"""

    def __init__(
        self,
        service_id: DarcL3DataPacketServiceIdentificationCode,
        data_group_number: int,
        payload: bitstring.Bits,
    ) -> None:
        """Constructor

        Args:
            service_id (DarcL3DataPacketServiceIdentificationCode): Service ID
            data_group_number (int): Data Group number
            payload (bitstring.Bits): Payload
        """
        # Metadata
        self.service_id = service_id
        self.data_group_number = data_group_number

        self.payload = payload

    def bit_reversed_payload(self) -> bitstring.Bits:
        """Get bit reversed payload

        Returns:
            bitstring.Bits: Bit reversed payload
        """
        return bitstring.Bits(reverse_bits(self.payload.bytes))


class DarcL4DataGroup1(DarcL4DataGroup):
    """DARC L4 Data Group Composition 1"""

    def start_of_headding(self) -> int:
        """Get Start of headding

        Returns:
            int: Start of headding
        """
        bit_reversed_payload = self.bit_reversed_payload()
        return bit_reversed_payload[0:8].uint

    def data_group_link(self) -> int:
        """Get Data Group link

        Returns:
            int: Data Group link
        """
        bit_reversed_payload = self.bit_reversed_payload()
        return bit_reversed_payload[8:9].uint

    def data_group_data(self) -> bitstring.Bits:
        """Get Data Group data

        Returns:
            bitstring.Bits: Data Group data
        """
        bit_reversed_payload = self.bit_reversed_payload()
        data_group_size: int = bit_reversed_payload[9:24].uint
        return bit_reversed_payload[24 : 24 + 8 * data_group_size]

    def end_of_data_group(self) -> int:
        """Get End of Data Group

        Returns:
            int: End of Data Group
        """
        bit_reversed_payload = self.bit_reversed_payload()
        return bit_reversed_payload[-24:-16].uint

    def crc(self) -> int:
        """Get recorded CRC value

        Returns:
            int: Recorded CRC value
        """
        return self.payload[-16:].uint

    def is_crc_valid(self) -> bool:
        """Is CRC valid

        Returns:
            bool: True if CRC is valid, else False
        """
        return crc_16_darc(self.payload[:-16].bytes) == self.crc()


class DarcL4DataGroup2(DarcL4DataGroup):
    def has_crc(self) -> bool:
        """Has CRC value

        Returns:
            bool: True if has CRC value, else None
        """
        return 160 < len(self.payload)

    def segments_data(self) -> bitstring.Bits:
        """Get Segments data

        Returns:
            bitstring.Bits: Segments data
        """
        bit_reversed_payload = self.bit_reversed_payload()
        has_crc = self.has_crc()
        return bit_reversed_payload[:-16] if has_crc else bit_reversed_payload

    def crc(self) -> int | None:
        """Get CRC value

        Returns:
            int | None: int if has CRC value, else None
        """
        has_crc = self.has_crc()
        return self.payload[-16:].uint if has_crc else None

    def is_crc_valid(self) -> bool:
        """Is CRC valid

        Returns:
            bool: True if CRC is valid or has not CRC, else False
        """
        crc = self.crc()
        if crc is None:
            return True

        return crc_16_darc(self.payload[:-16].bytes) == crc
