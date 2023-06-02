import argparse
from pydarc.darc_packet_data import (
    DarcDataPacket,
    DarcParityPacket,
)
from pydarc.darc_l2_packet_decoder import DarcL2PacketDecoder
import sys


def main(argv=None):
    parser = argparse.ArgumentParser(description="DARC bitstream Decoder")
    parser.add_argument("input_path", help="Input DARC bitstream path (- to stdin)")
    args = parser.parse_args()

    l2_packet_decoder = DarcL2PacketDecoder()

    if args.input_path == "-":
        while True:
            bit = ord(sys.stdin.read(1))
            packet = l2_packet_decoder.push_bit(bit)
            if isinstance(packet, DarcDataPacket):
                print(
                    f"DarcDataPacket bic={packet.bic.name} data_packet={packet.data_packet.hex()} crc={hex(packet.crc)} parity={hex(packet.parity)}"
                )
            elif isinstance(packet, DarcParityPacket):
                print(
                    f"DarcParityPacket bic={packet.bic.name} parity={hex(packet.parity)}"
                )
    else:
        print("File input is not yet supported.")


if __name__ == "__main__":
    main()
