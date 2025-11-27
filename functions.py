from concurrent.futures import ProcessPoolExecutor
from threading import Lock
from functools import lru_cache
from PIL import Image
import itertools
import random
import os


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


def canal_int12(cw: int, p: float) -> int:
    global _module_rng, _module_rng_lock
    if '_module_rng' not in globals():
        _module_rng = random.Random(int.from_bytes(os.urandom(8), 'little'))
        _module_rng_lock = Lock()

    out = cw
    with _module_rng_lock:
        for j in range(12):
            if _module_rng.random() <= p:
                out ^= (1 << j)
    return out


def canal_int23(cw: int, p: float) -> int:
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


def bytes_to_blocks(raw_bytes: bytes, max_workers: int) -> list[int]:
    """ 
    Converts bytes -> 12-bit ints by working with 3-byte-aligned chunks;
    Each 3 bytes = 24 bits = 2 blocks of 12 bits 
    """
    if max_workers > 1 and len(raw_bytes) >= 3 * max_workers:
        groups = (len(raw_bytes) // 3) // max_workers
        chunk_size = max(3, groups * 3)
        chunks = [raw_bytes[i:i+chunk_size] for i in range(0, (len(raw_bytes)//3)*3, chunk_size)]
        remainder = raw_bytes[len(chunks)*chunk_size:]
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            results = list(ex.map(bytes_to_12bit_ints, chunks, chunksize=max(1, len(chunks)//max_workers)))
        blocks_int = [val for sub in results for val in sub]
        if remainder:
            blocks_int.extend(bytes_to_12bit_ints(remainder))
    else:
        blocks_int = bytes_to_12bit_ints(raw_bytes)
    return blocks_int


def encode_blocks(blocks: list[int], max_workers: int, chunksize: int) -> list[int]:
    """ Encodes 12-bit ints -> 23-bit int codewords """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        encoded_blocks = list(ex.map(encode_int, blocks, chunksize=chunksize))
    return encoded_blocks


def canal_blocks12(blocks: list[int], p: float, max_workers: int, chunksize: int) -> list[int]:
    """ Simulates transmission errors on 12-bit codewords """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    noisy_blocks = list(ex.map(canal_int12, blocks, itertools.repeat(p), chunksize=chunksize))
    return noisy_blocks


def canal_blocks23(blocks: list[int], p: float, max_workers: int, chunksize: int) -> list[int]:
    """ Simulates transmission errors on 23-bit codewords """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    noisy_blocks = list(ex.map(canal_int23, blocks, itertools.repeat(p), chunksize=chunksize))
    return noisy_blocks


def decode_blocks(blocks: list[int], max_workers: int, chunksize: int) -> list[int]:
    """ Decodes received 23-bit int codewords -> 12-bit ints """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        decoded_blocks = list(ex.map(decode_int, blocks, chunksize=chunksize))
    return decoded_blocks


def blocks_to_bytes(blocks: list[int], max_workers: int) -> bytes:
    """ 
    Converts 12-bit ints -> bytes by working with 2-block-aligned chunks; 
    Each 2 blocks = 24 bits = 3 bytes 
    """
    if max_workers > 1 and len(blocks) >= 2 * max_workers:
        groups = (len(blocks) // 2) // max_workers
        chunk_size = max(2, groups * 2)
        chunks = [blocks[i:i+chunk_size] for i in range(0, (len(blocks)//2)*2, chunk_size)]
        remainder = blocks[len(chunks)*chunk_size:]
        with ProcessPoolExecutor(max_workers=max_workers) as ex:
            results = list(ex.map(blocks_ints_to_bytes, chunks, chunksize=max(1, len(chunks)//max_workers)))
        out_bytes = b''.join(results)
        if remainder:
            out_bytes += blocks_ints_to_bytes(remainder)
    else:
        out_bytes = blocks_ints_to_bytes(blocks)
    return out_bytes


def save_to_file(out_path: str, width: int, height: int, data: bytes) -> int:
    """ Saves raw RGB bytes as a BMP image file """
    try:
        out_img = Image.frombytes('RGB', (width, height), data)
        out_img.save(out_path, format='BMP')
        return 1
    except Exception as e:
        print('Could not reconstruct/save image. Error:', e)
        input("Press Any Key to continue...")
        print("\n" * 2)
        return 0


test_vector = [1,0,1,0,1,0,1,0,1,0,1,0]
test_vector2 = [1,1,0,1,0,1,0,1,0,1,0,1]