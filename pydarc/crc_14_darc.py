import bitstring


def __reflect_bits(value, bits):
    result = 0
    for i in range(bits):
        result = (result << 1) | ((value >> i) & 1)
    return result


def __generate_crc_14_darc_table():
    table = [0] * 256
    for i in range(256):
        value = i << 6
        for _ in range(8):
            value = (value << 1) ^ 0x0805 if (value & 0x2000) != 0 else (value << 1)
        table[i] = value & 0x3FFF
    return table


__crc_14_darc_table = __generate_crc_14_darc_table()


def __crc_14_darc_table_driven(message: bytes | bitstring.Bits):
    crc = 0x0000
    for value in message:
        crc = __crc_14_darc_table[((crc >> 6) ^ value) & 0xFF] ^ (crc << 8)
    return crc & 0x3FFF


def __crc_14_darc_bit_by_bit(message: bytes | bitstring.Bits, bits: int):
    crc = 0x0000
    for value in message:
        for i in range(8):
            if bits <= 0:
                break

            bit = (crc & 0x2000) ^ (0x2000 if value & (0x80 >> i) != 0 else 0)
            crc <<= 1
            if bit != 0:
                crc ^= 0x0805

            bits -= 1
        crc &= 0x3FFF
    return crc & 0x3FFF


def crc_14_darc(message: bytes | bitstring.Bits, bits: int | None = None):
    if bits is None:
        bits = 8 * len(message)

    if bits % 8 == 0:
        return __crc_14_darc_table_driven(message)
    else:
        return __crc_14_darc_bit_by_bit(message, bits)
