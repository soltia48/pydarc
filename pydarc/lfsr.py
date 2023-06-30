def lfsr(seed: int, polynomial: int) -> int:
    """Galois Linear-Feedback Shift Register

    Args:
        seed (int): Seed
        polynomial (int): Polynomial

    Yields:
        int: Bit (0 or 1)
    """
    state = seed
    while True:
        lsb = state & 1
        state >>= 1
        if lsb != 0:
            state ^= polynomial
            yield 1
        else:
            yield 0
