def lfsr(seed: int, polynomial: int):
    state = seed
    while True:
        lsb = state & 1
        state >>= 1
        if lsb != 0:
            state ^= polynomial
            yield 1
        else:
            yield 0
