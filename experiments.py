"""experiments.py
Generate a 1MB dummy file, run uncoded and coded pipelines with several
channel error probabilities p, and report bit-error counts and timings.

Run: python experiments.py
"""
import os
import time
import csv
import multiprocessing
from functions import (
    bytes_to_blocks,
    encode_blocks,
    canal_blocks12,
    canal_blocks23,
    decode_blocks,
    blocks_to_bytes,
)


def bit_errors_bytes(a: bytes, b: bytes) -> int:
    """Return number of differing bits between two byte sequences.

    Pads the shorter sequence with zeros.
    """
    if len(a) < len(b):
        a = a + b'\x00' * (len(b) - len(a))
    elif len(b) < len(a):
        b = b + b'\x00' * (len(a) - len(b))

    total = 0
    for x, y in zip(a, b):
        total += (x ^ y).bit_count()
    return total


def run_experiment(dummy_path: str, p_values: list[float], max_workers: int = 1, num_runs: int = 10) -> list[dict]:
    # ensure dummy file exists
    if not os.path.exists(dummy_path):
        print(f"Creating dummy file {dummy_path} (1_048_576 bytes)")
        with open(dummy_path, 'wb') as f:
            f.write(os.urandom(1_048_576))  # 1 MB

    raw_bytes = open(dummy_path, 'rb').read()
    orig_len_bytes = len(raw_bytes)
    orig_len_bits = orig_len_bytes * 8

    print(f"Workers: {max_workers}, dummy size: {orig_len_bytes} bytes")

    # Convert once to blocks (reuse for all p)
    t0 = time.perf_counter()
    blocks = bytes_to_blocks(raw_bytes, max_workers)
    t_bytes_to_blocks = time.perf_counter() - t0

    print(f"Packed into {len(blocks)} 12-bit blocks (bytes->blocks: {t_bytes_to_blocks:.3f}s)")

    chunksize = max(1, len(blocks) // (max_workers * 2))

    # Encode once
    t0 = time.perf_counter()
    encoded = encode_blocks(blocks, max_workers, chunksize)
    t_encode = time.perf_counter() - t0
    print(f"Encoded {len(encoded)} blocks (encode: {t_encode:.3f}s)")

    # For each p, run both uncoded and coded channel + decode pipeline
    results = []
    for p in p_values:
        print('\n' + '=' * 60)
        print(f"Running experiment p={p} (runs={num_runs})")

        for run_idx in range(num_runs):
            # uncoded path: send raw 12-bit blocks through canal_int12
            t0 = time.perf_counter()
            noisy_uncoded = canal_blocks12(blocks, p, max_workers, chunksize)
            t_uncoded_channel = time.perf_counter() - t0

            t0 = time.perf_counter()
            recon_uncoded = blocks_to_bytes(noisy_uncoded, max_workers)
            t_uncoded_unpack = time.perf_counter() - t0

            # coded path: send encoded 23-bit codewords through canal_int23, then decode
            t0 = time.perf_counter()
            noisy_coded = canal_blocks23(encoded, p, max_workers, chunksize)
            t_coded_channel = time.perf_counter() - t0

            t0 = time.perf_counter()
            decoded_blocks = decode_blocks(noisy_coded, max_workers, chunksize)
            t_decode = time.perf_counter() - t0

            t0 = time.perf_counter()
            recon_coded = blocks_to_bytes(decoded_blocks, max_workers)
            t_coded_unpack = time.perf_counter() - t0

            # Trim reconstructed bytes to original length (pack/unpack may pad)
            recon_uncoded = recon_uncoded[:orig_len_bytes]
            recon_coded = recon_coded[:orig_len_bytes]

            # Compute bit errors
            errs_uncoded = bit_errors_bytes(raw_bytes, recon_uncoded)
            errs_coded = bit_errors_bytes(raw_bytes, recon_coded)

            equal_uncoded = errs_uncoded == 0
            equal_coded = errs_coded == 0

            print(f"Run {run_idx+1}/{num_runs} — Uncoded: channel={t_uncoded_channel:.3f}s, unpack={t_uncoded_unpack:.3f}s, errors={errs_uncoded}/{orig_len_bits} | {errs_uncoded/orig_len_bits:.6f}, equal={equal_uncoded}")
            print(f"Run {run_idx+1}/{num_runs} — Coded:   channel={t_coded_channel:.3f}s, decode={t_decode:.3f}s, unpack={t_coded_unpack:.3f}s, errors={errs_coded}/{orig_len_bits} | {errs_coded/orig_len_bits:.6f}, equal={equal_coded}")

            results.append({
                'run': run_idx + 1,
                'p': p,
                'errs_uncoded': errs_uncoded,
                'errs_coded': errs_coded,
                'errs_uncoded_ratio': errs_uncoded / orig_len_bits,
                'errs_coded_ratio': errs_coded / orig_len_bits,
                'equal_uncoded': equal_uncoded,
                'equal_coded': equal_coded,
                'orig_len_bits': orig_len_bits,
                'timings': {
                    'bytes_to_blocks': t_bytes_to_blocks,
                    'encode': t_encode,
                    'uncoded_channel': t_uncoded_channel,
                    'uncoded_unpack': t_uncoded_unpack,
                    'coded_channel': t_coded_channel,
                    'decode': t_decode,
                    'coded_unpack': t_coded_unpack,
                }
            })

    print('\nAll experiments completed.')
    return results


if __name__ == '__main__':
    multiprocessing.freeze_support()
    dummy = 'dummy_1MB.bin'
    p_values = [0.0, 0.0001, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.15, 0.2, 0.3, 0.4, 0.5]
    #max_workers = max(1, os.cpu_count() or 1)
    max_workers = 8  # adjust as needed
    num_runs = 10
    results = run_experiment(dummy, p_values, max_workers=max_workers, num_runs=num_runs)

    # Save results to CSV
    csv_path = 'experiments_results.csv'
    with open(csv_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = [
            'p', 'errs_uncoded', 'errs_coded', 'errs_uncoded_ratio', 'errs_coded_ratio', 'equal_uncoded', 'equal_coded', 'orig_len_bits',
            'bytes_to_blocks', 'encode', 'uncoded_channel', 'uncoded_unpack',
            'coded_channel', 'decode', 'coded_unpack'
        ]
        writer.writerow(header)
        for r in results:
            t = r['timings']
            writer.writerow([
                r['p'], r['errs_uncoded'], r['errs_coded'], r['errs_uncoded_ratio'], r['errs_coded_ratio'], r['equal_uncoded'], r['equal_coded'], r.get('orig_len_bits'),
                t['bytes_to_blocks'], t['encode'], t['uncoded_channel'], t['uncoded_unpack'],
                t['coded_channel'], t['decode'], t['coded_unpack']
            ])

    print(f"Results written to {csv_path}")

    # Compute per-p averages across runs and save to a separate CSV
    avg_path = 'experiments_results_avg.csv'
    grouped = {}
    for r in results:
        p = r['p']
        grouped.setdefault(p, []).append(r)

    with open(avg_path, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        header = [
            'p', 'runs', 'mean_errs_uncoded', 'mean_errs_coded', 'mean_errs_uncoded_ratio', 'mean_errs_coded_ratio',
            'frac_equal_uncoded', 'frac_equal_coded', 'orig_len_bits',
            'mean_bytes_to_blocks', 'mean_encode', 'mean_uncoded_channel', 'mean_uncoded_unpack',
            'mean_coded_channel', 'mean_decode', 'mean_coded_unpack'
        ]
        writer.writerow(header)
        for p, rows in sorted(grouped.items()):
            n = len(rows)
            sum_errs_uncoded = sum(r['errs_uncoded'] for r in rows)
            sum_errs_coded = sum(r['errs_coded'] for r in rows)
            sum_errs_uncoded_ratio = sum(r['errs_uncoded_ratio'] for r in rows)
            sum_errs_coded_ratio = sum(r['errs_coded_ratio'] for r in rows)
            sum_equal_uncoded = sum(1 if r['equal_uncoded'] else 0 for r in rows)
            sum_equal_coded = sum(1 if r['equal_coded'] else 0 for r in rows)
            orig_bits = rows[0].get('orig_len_bits')

            # timings: these are per-run values inside r['timings']
            mean_bytes_to_blocks = sum(r['timings']['bytes_to_blocks'] for r in rows) / n
            mean_encode = sum(r['timings']['encode'] for r in rows) / n
            mean_uncoded_channel = sum(r['timings']['uncoded_channel'] for r in rows) / n
            mean_uncoded_unpack = sum(r['timings']['uncoded_unpack'] for r in rows) / n
            mean_coded_channel = sum(r['timings']['coded_channel'] for r in rows) / n
            mean_decode = sum(r['timings']['decode'] for r in rows) / n
            mean_coded_unpack = sum(r['timings']['coded_unpack'] for r in rows) / n

            writer.writerow([
                p, n,
                sum_errs_uncoded / n,
                sum_errs_coded / n,
                sum_errs_uncoded_ratio / n,
                sum_errs_coded_ratio / n,
                sum_equal_uncoded / n,
                sum_equal_coded / n,
                orig_bits,
                mean_bytes_to_blocks, mean_encode, mean_uncoded_channel, mean_uncoded_unpack,
                mean_coded_channel, mean_decode, mean_coded_unpack
            ])

    print(f"Averaged results written to {avg_path}")
