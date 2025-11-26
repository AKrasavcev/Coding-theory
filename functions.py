import random
import os
from functools import lru_cache

def B() -> list[list[int]]:
    return [
        [1,1,0,1,1,1,0,0,0,1,0,1],
        [1,0,1,1,1,0,0,0,1,0,1,1],
        [0,1,1,1,0,0,0,1,0,1,1,1],
        [1,1,1,0,0,0,1,0,1,1,0,1],
        [1,1,0,0,0,1,0,1,1,0,1,1],
        [1,0,0,0,1,0,1,1,0,1,1,1],
        [0,0,0,1,0,1,1,0,1,1,1,1],
        [0,0,1,0,1,1,0,1,1,1,0,1],
        [0,1,0,1,1,0,1,1,1,0,0,1],
        [1,0,1,1,0,1,1,1,0,0,0,1],
        [0,1,1,0,1,1,1,0,0,0,1,1],
        [1,1,1,1,1,1,1,1,1,1,1,0]
    ]

def G() -> list[list[int]]:
    return [
    [1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,1,1,0,0,0,1,0],
    [0,1,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,0,0,1,0,1],
    [0,0,1,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,0,1,1],
    [0,0,0,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,1,0,1,1,0],
    [0,0,0,0,1,0,0,0,0,0,0,0,1,1,0,0,0,1,0,1,1,0,1],
    [0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,1,0,1,1,0,1,1],
    [0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,1,0,1,1,1],
    [0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,1,1,0,1,1,1,0],
    [0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1,1,0,1,1,1,0,0],
    [0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,1,0,1,1,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,1,1,1,0,0,0,1],
    [0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1,1,1,1]
]

def H() -> list[list[int]]:
    return [
    [1,0,0,0,0,0,0,0,0,0,0,0],
    [0,1,0,0,0,0,0,0,0,0,0,0],
    [0,0,1,0,0,0,0,0,0,0,0,0],
    [0,0,0,1,0,0,0,0,0,0,0,0],
    [0,0,0,0,1,0,0,0,0,0,0,0],
    [0,0,0,0,0,1,0,0,0,0,0,0],
    [0,0,0,0,0,0,1,0,0,0,0,0],
    [0,0,0,0,0,0,0,1,0,0,0,0],
    [0,0,0,0,0,0,0,0,1,0,0,0],
    [0,0,0,0,0,0,0,0,0,1,0,0],
    [0,0,0,0,0,0,0,0,0,0,1,0],
    [0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,0,1,1,1,0,0,0,1,0,1],
    [1,0,1,1,1,0,0,0,1,0,1,1],
    [0,1,1,1,0,0,0,1,0,1,1,1],
    [1,1,1,0,0,0,1,0,1,1,0,1],
    [1,1,0,0,0,1,0,1,1,0,1,1],
    [1,0,0,0,1,0,1,1,0,1,1,1],
    [0,0,0,1,0,1,1,0,1,1,1,1],
    [0,0,1,0,1,1,0,1,1,1,0,1],
    [0,1,0,1,1,0,1,1,1,0,0,1],
    [1,0,1,1,0,1,1,1,0,0,0,1],
    [0,1,1,0,1,1,1,0,0,0,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,0]
]

def ZEROES() -> list[int]:
    return [0] * 12


# --- Integer-based helpers and fast routines ---
def _row_to_int(row: list[int]) -> int:
    # map list index i -> bit position i (LSB = index 0)
    m = 0
    for i, bit in enumerate(row):
        if bit & 1:
            m |= (1 << i)
    return m


@lru_cache(maxsize=1)
def G_masks() -> list[int]:
    return [_row_to_int(row) for row in G()]


@lru_cache(maxsize=1)
def H_row_masks() -> list[int]:
    # H() returns 24 rows of length 12 -> each row contributes a 12-bit mask
    return [_row_to_int(row) for row in H()]


@lru_cache(maxsize=1)
def B_masks() -> list[int]:
    return [_row_to_int(row) for row in B()]


def bits_list_to_int(bits: list[int]) -> int:
    v = 0
    for i, b in enumerate(bits):
        if b & 1:
            v |= (1 << i)
    return v


def int_to_bits_list(x: int, length: int) -> list[int]:
    return [ (x >> i) & 1 for i in range(length) ]


def encode_int(u12: int) -> int:
    """Encode a 12-bit integer into a 23-bit integer using precomputed masks."""
    masks = G_masks()
    cw = 0
    for j in range(12):
        if (u12 >> j) & 1:
            cw ^= masks[j]
    return cw


def encode_many_int(us: list[int]) -> list[int]:
    return [encode_int(u) for u in us]


def _add_w24_int(cw23: int) -> int:
    # preserve existing list-based parity rule: if sum(bits) % 2 == 1 -> append 0 else append 1
    parity = cw23.bit_count() & 1
    append_bit = 0 if parity == 1 else 1
    return cw23 | (append_bit << 23)


def _syndrome_w24_int(w24: int) -> int:
    # compute 12-bit syndrome: s = sum_j w[j] * H_row_masks[j]
    masks = H_row_masks()
    s = 0
    for j in range(24):
        if (w24 >> j) & 1:
            s ^= masks[j]
    return s


def _syndrome_12_with_B(s12: int) -> int:
    # compute syndrome of 12-bit vector against B matrix (12x12)
    masks = B_masks()
    out = 0
    for j in range(12):
        if (s12 >> j) & 1:
            out ^= masks[j]
    return out


def IMLD_int(w24: int) -> int:
    # Implements the integer variant of IMLD using masks
    s = _syndrome_w24_int(w24)

    if s.bit_count() <= 3:
        # combine_vectors(s, ZEROES()) -> s in low 12 bits
        return w24 ^ s

    # try s + B[i]
    for i, bmask in enumerate(B_masks()):
        sb = s ^ bmask
        if sb.bit_count() <= 2:
            # e has bit i set in positions 12..23 (second half)
            e_mask = (1 << (12 + i))
            combined = (sb & ((1<<12)-1)) | e_mask
            return w24 ^ combined

    # s2 = syndrome(s, B())
    s2 = _syndrome_12_with_B(s)
    if s2.bit_count() <= 3:
        # combine_vectors(ZEROES(), s2) -> s2 in positions 12..23
        return w24 ^ (s2 << 12)

    for i, bmask in enumerate(B_masks()):
        sb = s2 ^ bmask
        if sb.bit_count() <= 2:
            e_mask = (1 << i)
            combined = (e_mask) | ((sb & ((1<<12)-1)) << 12)
            return w24 ^ combined

    raise ValueError("More than 3 errors detected; cannot decode.")


def decode_int(cw23: int) -> int:
    """Decode a 23-bit codeword integer to a 12-bit integer payload."""
    w24 = _add_w24_int(cw23)
    corrected = IMLD_int(w24)
    # remove last bit (the appended parity) and return first 12 bits
    return corrected & ((1 << 12) - 1)


def decode_many_int(cws: list[int]) -> list[int]:
    return [decode_int(cw) for cw in cws]


def canal_int(cw: int, p: float) -> int:
    """Apply BSC channel to a 23-bit codeword integer, flipping each bit with probability p."""
    # create a local RNG seeded from OS randomness to avoid correlated streams in worker processes
    rnd = random.Random(int.from_bytes(os.urandom(8), 'little'))
    out = cw
    for j in range(23):
        if rnd.random() <= p:
            out ^= (1 << j)
    return out


def canal_many_int(cws: list[int], p: float) -> list[int]:
    return [canal_int(cw, p) for cw in cws]


test_vector = [1,0,1,0,1,0,1,0,1,0,1,0]
test_vector2 = [1,1,0,1,0,1,0,1,0,1,0,1]

def add_w24(v: list[int]) -> list[int]:
    if sum(v) % 2:
        v.append(0)
    else:
        v.append(1)
    return v

def remove_w24(v: list[int]) -> list[int]:
    return v[:-1]

def multiply(v : list[int], A : list[list[int]]) -> list[int]:
    sum = [0] * len(A[0])
    for i in range(len(A[0])):
        for j in range(len(v)):
            sum[i] ^= v[j] & A[j][i]
    return sum

def syndrome(v : list[int], A : list[list[int]]) -> list[int]:
    return multiply(v, A)

def xor_vectors(a : list[int], b: list[int]) -> list[int]:
    return [(x ^ y) for x, y in zip(a, b)]

def sum_vectors(a : list[int], b : list[int]) -> list[int]:
    return [(x + y) % 2 for x, y in zip(a, b)]

def combine_vectors(a : list[int], b: list[int]) -> list[int]:
    return a + b

def weight(v : list[int]) -> int:
    return sum(v)

def encode(v : list[int]) -> list[int]:
    if len(v) != 12:
        raise ValueError("Input vector must be of length 12.")
    return multiply(v, G())

def IMLD(w : list[int]) -> list[int]:
    if len(w) != 24:
        raise ValueError("Input vector must be of length 24.")
    
    s = syndrome(w, H())
    
    if weight(s) <= 3:
        return sum_vectors(combine_vectors(s, ZEROES()), w)
    
    for i in range(len(B())):
        sb = sum_vectors(s, B()[i])
        if weight(sb) <= 2:
            e = ZEROES()
            e[i] = 1
            return sum_vectors(combine_vectors(sb, e), w)
        
    s2 = syndrome(s, B())
    if weight(s2) <= 3:
        return sum_vectors(combine_vectors(ZEROES(), s2), w)
    
    for i in range(len(B())):
        sb = sum_vectors(s2, B()[i])
        if weight(sb) <= 2:
            e = ZEROES()
            e[i] = 1
            return sum_vectors(combine_vectors(e, sb), w)
        
    raise ValueError("More than 3 errors detected; cannot decode.")

def decode(w : list[int]) -> list[int]:
    w = add_w24(w)
    corrected = IMLD(w)
    corrected = remove_w24(corrected)
    return corrected[:12]

def canal(v: list[int], p: float) -> list[int]:
    noisy = v.copy()
    for i in range(len(noisy)):
        if random.random() <= p:
            noisy[i] ^= 1
    return noisy
