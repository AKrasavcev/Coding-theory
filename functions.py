import random
import os
from threading import Lock
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


def _row_to_int(row: list[int]) -> int:
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
    masks = G_masks()
    cw = 0
    for j in range(12):
        if (u12 >> j) & 1:
            cw ^= masks[j]
    return cw


def _add_w24_int(cw23: int) -> int:
    parity = cw23.bit_count() & 1
    append_bit = 0 if parity == 1 else 1
    return cw23 | (append_bit << 23)


def _syndrome_w24_int(w24: int) -> int:
    masks = H_row_masks()
    s = 0
    for j in range(24):
        if (w24 >> j) & 1:
            s ^= masks[j]
    return s


def _syndrome_12_with_B(s12: int) -> int:
    masks = B_masks()
    out = 0
    for j in range(12):
        if (s12 >> j) & 1:
            out ^= masks[j]
    return out


def IMLD_int(w24: int) -> int:
    s = _syndrome_w24_int(w24)

    if s.bit_count() <= 3:
        return w24 ^ s

    for i, bmask in enumerate(B_masks()):
        sb = s ^ bmask
        if sb.bit_count() <= 2:
            e_mask = (1 << (12 + i))
            combined = (sb & ((1<<12)-1)) | e_mask
            return w24 ^ combined

    s2 = _syndrome_12_with_B(s)
    if s2.bit_count() <= 3:
        return w24 ^ (s2 << 12)

    for i, bmask in enumerate(B_masks()):
        sb = s2 ^ bmask
        if sb.bit_count() <= 2:
            e_mask = (1 << i)
            combined = (e_mask) | ((sb & ((1<<12)-1)) << 12)
            return w24 ^ combined

    raise ValueError("More than 3 errors detected; cannot decode.")


def decode_int(cw23: int) -> int:
    w24 = _add_w24_int(cw23)
    corrected = IMLD_int(w24)
    return corrected & ((1 << 12) - 1)


def decode_many_int(cws: list[int]) -> list[int]:
    return [decode_int(cw) for cw in cws]


def canal_int(cw: int, p: float) -> int:
    global _module_rng, _module_rng_lock
    if '_module_rng' not in globals():
        _module_rng = random.Random(int.from_bytes(os.urandom(8), 'little'))
        _module_rng_lock = Lock()

    out = cw
    with _module_rng_lock:
        for j in range(23):
            if _module_rng.random() <= p:
                out ^= (1 << j)
    return out


def canal_many_int(cws: list[int], p: float) -> list[int]:
    return [canal_int(cw, p) for cw in cws]

def canal(v: list[int], p: float) -> list[int]:
    noisy = v.copy()
    for i in range(len(noisy)):
        if random.random() <= p:
            noisy[i] ^= 1
    return noisy


def bytes_to_12bit_ints(b: bytes) -> list[int]:
    blocks = []
    acc = 0
    acc_len = 0
    for byte in b:
        for i in range(7, -1, -1):
            acc = (acc << 1) | ((byte >> i) & 1)
            acc_len += 1
            if acc_len == 12:
                blocks.append(acc)
                acc = 0
                acc_len = 0
    if acc_len > 0:
        acc = acc << (12 - acc_len)
        blocks.append(acc)
    return blocks

def blocks_ints_to_bytes(blocks: list[int]) -> bytes:
    out = bytearray()
    acc = 0
    acc_len = 0
    for val in blocks:
        for i in range(11, -1, -1):
            bit = (val >> i) & 1
            acc = (acc << 1) | bit
            acc_len += 1
            if acc_len == 8:
                out.append(acc)
                acc = 0
                acc_len = 0
    if acc_len > 0:
        out.append(acc << (8 - acc_len))
    return bytes(out)


test_vector = [1,0,1,0,1,0,1,0,1,0,1,0]
test_vector2 = [1,1,0,1,0,1,0,1,0,1,0,1]