import bitstring


def __reflect_bits(value, bits):
    result = 0
    for i in range(bits):
        result = (result << 1) | ((value >> i) & 1)
    return result


def __generate_crc_82_darc_table():
    table = [0] * 256
    for i in range(256):
        value = i << 74
        for _ in range(8):
            value = (
                (value << 1) ^ 0x0308C0111011401440411
                if (value & 0x200000000000000000000) != 0
                else (value << 1)
            )
        table[i] = value & 0x3FFFFFFFFFFFFFFFFFFFF
    return table


__crc_82_darc_table = __generate_crc_82_darc_table()


def __crc_82_darc_table_driven(message: bytes | bitstring.Bits):
    crc = 0x000000000000000000000
    for value in message:
        crc = __crc_82_darc_table[((crc >> 74) ^ value) & 0xFF] ^ (crc << 8)
    return crc & 0x3FFFFFFFFFFFFFFFFFFFF


def __crc_82_darc_bit_by_bit(message: bytes | bitstring.Bits, bits: int):
    crc = 0x000000000000000000000
    for value in message:
        for i in range(8):
            if bits <= 0:
                break

            bit = (crc & 0x200000000000000000000) ^ (
                0x200000000000000000000 if value & (0x80 >> i) != 0 else 0
            )
            crc <<= 1
            if bit != 0:
                crc ^= 0x0308C0111011401440411

            bits -= 1
        crc &= 0x3FFFFFFFFFFFFFFFFFFFF
    return crc & 0x3FFFFFFFFFFFFFFFFFFFF


def crc_82_darc(message: bytes | bitstring.Bits, bits: int | None = None):
    if bits is None:
        bits = 8 * len(message)

    if bits % 8 == 0:
        return __crc_82_darc_table_driven(message)
    else:
        return __crc_82_darc_bit_by_bit(message, bits)


def generate_bitflip_syndrome_map(length: int, error_width: int):
    bitflip_syndrome_map: dict[int, bitstring.Bits] = dict()
    for i in range(1, error_width + 1):
        error_base = 1 << (i - 1) | 1
        counter_max = 2 ** (i - 2) if 2 < i else 1
        for j in range(counter_max):
            error_with_counter = error_base | j << 1
            for k in range(length - i):
                error = error_with_counter << k
                error_vector = bitstring.Bits(uint=error, length=length)
                bitflip_syndrome_map[crc_82_darc(error_vector, length)] = error_vector
    return bitflip_syndrome_map
