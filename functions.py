from concurrent.futures import ProcessPoolExecutor
from threading import Lock
from functools import lru_cache
from PIL import Image
import itertools
import random
import os


def B() -> list[list[int]]:
    """
    Return matrix B used by the Golay IMLD algorithm.

    Returns:
        list[list[int]]: 12x12 binary matrix represented as list of rows (each row is a list of 0/1).
    """
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
    """
    Return generator matrix G for Golay C(23,12).

    Returns:
        list[list[int]]: 12x23 binary generator matrix (rows are lists of 0/1).
    """
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
    """
    Return parity-check matrix H for Golay decoding (24x12 used by IMLD logic).

    Returns:
        list[list[int]]: 24x12 binary matrix (rows are lists of 0/1).
    """
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


def _row_to_int(row: list[int]) -> int:
    """
    Convert a binary row (list of 0/1) into an integer mask.

    Args:
        row (list[int]): list of bits where index 0 -> LSB.

    Returns:
        int: integer whose bits correspond to the input row.
    """
    m = 0
    for i, bit in enumerate(row):
        if bit & 1:
            m |= (1 << i)
    return m


@lru_cache(maxsize=1)
def G_masks() -> list[int]:
    """
    Cached conversion of generator matrix rows into integer masks.

    Returns:
        list[int]: list of 12 integer masks corresponding to rows of G().
    """
    return [_row_to_int(row) for row in G()]


@lru_cache(maxsize=1)
def H_masks() -> list[int]:
    """
    Cached conversion of H() rows to integer masks.

    Returns:
        list[int]: list of 24 integer masks corresponding to rows of H().
    """
    return [_row_to_int(row) for row in H()]


@lru_cache(maxsize=1)
def B_masks() -> list[int]:
    """
    Cached conversion of B() rows to integer masks.

    Returns:
        list[int]: list of 12 integer masks corresponding to rows of B().
    """
    return [_row_to_int(row) for row in B()]


def bits_list_to_int(bits: list[int]) -> int:
    """
    Pack a list of bits into an integer.

    Args:
        bits (list[int]): list of bits where index 0 is the least-significant bit (LSB).

    Returns:
        int: integer value representing the packed bits.
    """
    w = 0
    for i, b in enumerate(bits):
        if b & 1:
            w |= (1 << i)
    return w

def int_to_bits_list(w: int, length: int) -> list[int]:
    """
    Unpack an integer into a list of bits.

    Args:
        w (int): integer to unpack.
        length (int): number of bits to produce.

    Returns:
        list[int]: list of bits [bit0, bit1, ..., bit{length-1}] where bit0 is LSB.
    """
    return [ (w >> i) & 1 for i in range(length) ]


def encode_int(w12: int) -> int:
    """
    Encode a 12-bit payload integer into a 23-bit Golay codeword integer.

    Args:
        w12 (int): 12-bit payload (0..4095).

    Returns:
        int: 23-bit codeword packed into an integer.
    """
    masks = G_masks()
    w23 = 0
    for j in range(12):
        if (w12 >> j) & 1:
            w23 ^= masks[j]
    return w23

def _add_w24_int(w23: int) -> int:
    """
    Append the 24th parity bit to a 23-bit codeword integer.

    The rule follows existing list-based parity: if parity of w23 bits is 1 -> append 0, else append 1.

    Args:
        w23 (int): 23-bit codeword integer.

    Returns:
        int: 24-bit integer with appended parity bit at position 23.
    """
    parity = w23.bit_count() & 1
    append_bit = 0 if parity == 1 else 1
    return w23 | (append_bit << 23)


def _syndrome_w24_int(w24: int) -> int:
    """
    Compute the 12-bit syndrome for a 24-bit word using H row masks.

    Args:
        w24 (int): 24-bit word (integer).

    Returns:
        int: 12-bit syndrome packed in an int.
    """
    masks = H_masks()
    s = 0
    for j in range(24):
        if (w24 >> j) & 1:
            s ^= masks[j]
    return s


def _syndrome_w12(s12: int) -> int:
    """
    Compute syndrome of a 12-bit vector against matrix B.

    Args:
        s12 (int): 12-bit integer syndrome.

    Returns:
        int: 12-bit integer result of syndrome against B.
    """
    masks = B_masks()
    s2 = 0
    for j in range(12):
        if (s12 >> j) & 1:
            s2 ^= masks[j]
    return s2


def IMLD_int(w24: int) -> int:
    """
    Integer implementation of the IMLD decoding routine for Golay code.

    This function attempts to correct up to 3 errors in a 24-bit word using
    precomputed masks and the B matrix search strategy.

    Args:
        w24 (int): 24-bit integer.

    Returns:
        int: corrected 24-bit integer.

    Raises:
        ValueError: if more than 3 errors are detected and correction fails.
    """
    s = _syndrome_w24_int(w24)

    if s.bit_count() <= 3:
        return w24 ^ s

    for i, bmask in enumerate(B_masks()):
        sb = s ^ bmask
        if sb.bit_count() <= 2:
            e_mask = (1 << (12 + i))
            combined = (sb & ((1<<12)-1)) | e_mask
            return w24 ^ combined

    s2 = _syndrome_w12(s)
    if s2.bit_count() <= 3:
        return w24 ^ (s2 << 12)

    for i, bmask in enumerate(B_masks()):
        sb = s2 ^ bmask
        if sb.bit_count() <= 2:
            e_mask = (1 << i)
            combined = (e_mask) | ((sb & ((1<<12)-1)) << 12)
            return w24 ^ combined

    raise ValueError("More than 3 errors detected; cannot decode.")


def decode_int(w23: int) -> int:
    """
    Decode a 23-bit Golay codeword integer to recover the 12-bit payload.

    Args:
        w23 (int): 23-bit codeword integer.

    Returns:
        int: recovered 12-bit payload (LSB-based packing).
    """
    w24 = _add_w24_int(w23)
    corrected = IMLD_int(w24)
    return corrected & ((1 << 12) - 1)


def canal_int12(w: int, p: float) -> int:
    """
    Apply a binary symmetric channel (BSC) to a 12-bit integer word.

    Each bit is flipped independently with probability `p`.

    Args:
        w (int): integer representing up to 12 bits (payload or block).
        p (float): flip probability in [0,1].

    Returns:
        int: integer with bits flipped according to the BSC.
    """
    global _module_rng, _module_rng_lock
    if '_module_rng' not in globals():
        _module_rng = random.Random(int.from_bytes(os.urandom(8), 'little'))
        _module_rng_lock = Lock()

    out = w
    with _module_rng_lock:
        for j in range(12):
            if _module_rng.random() <= p:
                out ^= (1 << j)
    return out


def canal_int23(w: int, p: float) -> int:
    """
    Apply a binary symmetric channel (BSC) to a 23-bit codeword integer.

    Args:
        w (int): 23-bit codeword integer.
        p (float): flip probability in [0,1].

    Returns:
        int: noisy 23-bit integer after random bit flips.
    """
    global _module_rng, _module_rng_lock
    if '_module_rng' not in globals():
        _module_rng = random.Random(int.from_bytes(os.urandom(8), 'little'))
        _module_rng_lock = Lock()

    out = w
    with _module_rng_lock:
        for j in range(23):
            if _module_rng.random() <= p:
                out ^= (1 << j)
    return out


def canal(v: list[int], p: float) -> list[int]:
    """
    Apply a binary symmetric channel (BSC) to a list of bits.

    Args:
        v (list[int]): list of bits (0/1).
        p (float): flip probability for each bit.

    Returns:
        list[int]: noisy copy of input list with some bits flipped.
    """
    noisy = v.copy()
    for i in range(len(noisy)):
        if random.random() <= p:
            noisy[i] ^= 1
    return noisy


def bytes_to_12bit_ints(b: bytes) -> list[int]:
    """
    Pack a bytes stream into a list of 12-bit integers.

    Bits are read most-significant bit (MSB)-first from each byte and collected into 12-bit blocks.
    If the total number of bits is not divisible by 12, the last block is padded
    with zeros on the least-significant side to reach 12 bits.

    Args:
        b (bytes): input byte sequence.

    Returns:
        list[int]: list of 12-bit integers representing packed blocks.
    """
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
    """
    Unpack a list of 12-bit integers into a bytes sequence.

    Bits are emitted MSB-first from each 12-bit block. If the final byte is
    partial it is padded with zeros in the LSB positions.

    Args:
        blocks (list[int]): list of 12-bit integers.

    Returns:
        bytes: resulting byte sequence (may include trailing zero-padding in last byte).
    """
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
    Convert a byte stream to a list of 12-bit integers using optional parallelism.

    This function chunks the input on 3-byte boundaries (24 bits) so each chunk
    contains an even number of 12-bit blocks, which is helpful for parallel packing.

    Args:
        raw_bytes (bytes): input byte stream.
        max_workers (int): number of worker processes to use; if 1, runs single-threaded.

    Returns:
        list[int]: list of 12-bit integers.
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
    """
    Encode a list of 12-bit integers into 23-bit codewords using optional parallelism.

    Args:
        blocks (list[int]): list of 12-bit payload integers.
        max_workers (int): maximum worker processes for parallel map.
        chunksize (int): chunksize to pass to ProcessPoolExecutor.map.

    Returns:
        list[int]: encoded 23-bit codewords as integers.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        encoded_blocks = list(ex.map(encode_int, blocks, chunksize=chunksize))
    return encoded_blocks


def canal_blocks12(blocks: list[int], p: float, max_workers: int, chunksize: int) -> list[int]:
    """
    Apply BSC to a list of 12-bit blocks in parallel.

    Args:
        blocks (list[int]): list of 12-bit integers.
        p (float): flip probability for each bit.
        max_workers (int): number of worker processes.
        chunksize (int): chunksize for parallel mapping.

    Returns:
        list[int]: noisy 12-bit integers after channel application.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        noisy_blocks = list(ex.map(canal_int12, blocks, itertools.repeat(p), chunksize=chunksize))
    return noisy_blocks


def canal_blocks23(blocks: list[int], p: float, max_workers: int, chunksize: int) -> list[int]:
    """
    Apply BSC to a list of 23-bit codewords in parallel.

    Args:
        blocks (list[int]): list of 23-bit codeword integers.
        p (float): flip probability for each bit.
        max_workers (int): number of worker processes.
        chunksize (int): chunksize for parallel mapping.

    Returns:
        list[int]: noisy 23-bit integers after channel application.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        noisy_blocks = list(ex.map(canal_int23, blocks, itertools.repeat(p), chunksize=chunksize))
    return noisy_blocks


def decode_blocks(blocks: list[int], max_workers: int, chunksize: int) -> list[int]:
    """
    Decode a list of 23-bit codewords back to 12-bit payloads in parallel.

    Args:
        blocks (list[int]): list of 23-bit codeword integers.
        max_workers (int): number of worker processes.
        chunksize (int): chunksize for parallel mapping.

    Returns:
        list[int]: list of recovered 12-bit integers.
    """
    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        decoded_blocks = list(ex.map(decode_int, blocks, chunksize=chunksize))
    return decoded_blocks


def blocks_to_bytes(blocks: list[int], max_workers: int) -> bytes:
    """
    Convert a list of 12-bit integers into bytes, using optional parallelism.

    The function chunks on 2-block boundaries so each chunk represents a whole
    number of bytes (2 blocks = 24 bits = 3 bytes).

    Args:
        blocks (list[int]): list of 12-bit integers.
        max_workers (int): number of worker processes.

    Returns:
        bytes: resulting byte sequence (last byte may be zero-padded).
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
    """
    Save raw RGB bytes as a BMP image file.

    Args:
        out_path (str): filesystem path for the output BMP file.
        width (int): image width in pixels.
        height (int): image height in pixels.
        data (bytes): raw RGB byte sequence (length should be width*height*3).

    Returns:
        int: 1 on success, 0 on failure.
    """
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