"""
main.py
---------
Interactive demo and CLI for the Golay C(23,12) encode->channel->decode
pipeline.

This module provides a simple menu-driven program that exercises three
scenarios:
    1) encode/decode of a single 12-bit vector (interactive)
    2) encode/decode of an arbitrary text string (chunked 12-bit blocks)
    3) full image pipeline: read 24-bit BMP -> split into 12-bit blocks ->
         encode (12->23) -> channel (BSC) -> decode -> reconstruct image

The module uses the helper routines from `functions.py` for encoding,
channel simulation and packing/unpacking.

Run: `python main.py` and follow the menu prompts.
"""

from PIL import Image
from functions import *
import os
import time
import multiprocessing


def main():
    """
    Run the interactive menu loop.

    Behavior:
      - Presents a menu with 4 choices and executes the selected scenario.
      - Choice 1: interactive encode/decode of one 12-bit vector.
      - Choice 2: encode/decode ASCII text by grouping into 12-bit blocks.
      - Choice 3: end-to-end image pipeline for a 24-bit BMP using the
                  integer-based encode/canal/decode helpers.

    Returns:
        None
    """

    while True:
        print("Golay (C23) Code Implementation")
        print("------------------------------")
        print("Possible scenarios to test implementation:")
        print("1. Enter 12-bit vector")
        print("2. Enter text")
        print("3. Chose (write path) image file to encode/decode")
        print("4. Exit")
        print("------------------------------")
        choice = input("Enter your choice (1-4): ")
        choice = choice.strip()
        p = 0
        
        # -------------------------------------
        # Choice 1: single 12-bit vector (interactive)
        # -------------------------------------
        # Flow:
        #  - prompt user for a 12-bit binary string and an error probability p
        #  - pack bits to an int via `bits_list_to_int`
        #  - encode with `encode_int` -> 23-bit int
        #  - apply channel `canal_int23` -> noisy 23-bit int
        #  - allow user to override the noisy codeword manually
        #  - decode with `decode_int` and display recovered 12-bit payload
        if choice == '1':
            while True:
                user_input = input("\nEnter a 12-bit binary vector (e.g., 101010101010): ")
                if len(user_input) != 12 or any(bit not in '01' for bit in user_input):
                    print("Invalid input. Please enter a 12-bit binary vector.")
                    continue

                p = float(input("Enter error probability (e.g., 0.01 for 1%): "))
                if p < 0 or p > 1:
                    print("Invalid error probability. Please enter a value between 0 and 1.")
                    continue

                user_vector = [int(bit) for bit in user_input]
                u12 = bits_list_to_int(user_vector)
                print("Original vector: ", user_vector)

                encoded_u23 = encode_int(u12)
                print("Encoded vector:  ", int_to_bits_list(encoded_u23, 23))

                noisy_u23 = canal_int23(encoded_u23, p)
                print("Noisy vector:    ", int_to_bits_list(noisy_u23, 23))
                error_u23 = encoded_u23 ^ noisy_u23
                error_vector = int_to_bits_list(error_u23, 23)
                print("Error vector :   ", error_vector)
                print("Number of errors:", error_u23.bit_count())

                decoded_bits = []   
                while True:
                    choice2 = input("\nDo you want to change the noisy vector? (y/n): ")
                    if choice2.lower() == 'y':
                        new_noisy_input = input("Enter the new 23-bit noisy binary vector: ")
                        if len(new_noisy_input) != 23 or any(bit not in '01' for bit in new_noisy_input):
                            print("Invalid input. Please enter a 23-bit binary vector.")
                            continue
                        new_noisy_vector = [int(bit) for bit in new_noisy_input]
                        new_noisy_u23 = bits_list_to_int(new_noisy_vector)
                        noisy_u23 = new_noisy_u23
                        error_u23 = encoded_u23 ^ noisy_u23
                        print("Replaced noisy vector:", new_noisy_vector)
                        print("New number of errors: ", error_u23.bit_count())
                        break
                    elif choice2.lower() == 'n':
                        break
                    else:
                        print("Invalid choice. Please enter 'y' or 'n'.")

                try:
                    decoded_u12 = decode_int(noisy_u23)
                    decoded_bits = int_to_bits_list(decoded_u12, 12)
                except Exception as e:
                    print("Decoding failed:", e)

                print("Original vector: ", user_vector)
                print("Decoded vector:  ", decoded_bits)
                print("Error vector :   ", error_vector)
                print("Number of errors:", error_u23.bit_count())
                input("Press Any Key to continue...")
                print("\n" * 2)
                break

        # -------------------------------------
        # Choice 2: encode/decode text via 12-bit blocks
        # -------------------------------------
        # Flow:
        #  - convert input text to a binary string (8 bits per char)
        #  - simulate a raw (uncoded) channel on the original bits for
        #    comparison purposes (uses list-based `canal`)
        #  - split binary string into 12-bit blocks, pad last block with zeros
        #  - for each 12-bit block: pack -> encode_int -> canal_int23 -> decode_int
        #  - reassemble decoded bits into a text string and report statistics
        elif choice == '2':
            while True:
                text = input("Enter text to encode: ")
                p = float(input("Enter error probability (e.g., 0.01 for 1%): "))
                if p < 0 or p > 1:
                    print("Invalid error probability. Please enter a value between 0 and 1.")
                    continue

                binary_string = ''.join(format(ord(char), '08b') for char in text)

                # Simulate sending original text through channel without encoding
                original_noisy = []
                for i in range(0, len(binary_string), 12):
                    chunk = binary_string[i:i+12]
                    if len(chunk) < 12:
                        chunk = chunk.ljust(12, '0')
                    bits = [int(bit) for bit in chunk]
                    original_noisy.extend(canal(bits, p))

                original_reproduced = ''
                for i in range(0, len(original_noisy), 8):
                    byte = original_noisy[i:i+8]
                    if len(byte) < 8:
                        byte += [0] * (8 - len(byte))
                    original_reproduced += chr(int(''.join(map(str, byte)), 2))

                encoded_blocks = []
                noisy_blocks = []
                encoded_bits = []
                noisy_bits = []
                decoded_bits = []

                # Encode the binary string into 23-bit codewords
                for i in range(0, len(binary_string), 12):
                    chunk = binary_string[i:i+12]
                    if len(chunk) < 12:
                        chunk = chunk.ljust(12, '0')
                    bits = [int(bit) for bit in chunk]
                    u12 = bits_list_to_int(bits)
                    u23 = encode_int(u12)
                    encoded_blocks.append(u23)

                # Simulate sending encoded text through channel with errors
                noisy_blocks = [canal_int23(u23, p) for u23 in encoded_blocks]

                # Decode the received noisy codewords
                decoded_blocks = [decode_int(u23) for u23 in noisy_blocks]

                encoded_bits.extend([bit for u23 in encoded_blocks for bit in int_to_bits_list(u23, 23)])
                noisy_bits.extend([bit for u23 in noisy_blocks for bit in int_to_bits_list(u23, 23)])
                decoded_bits.extend([bit for u12 in decoded_blocks for bit in int_to_bits_list(u12, 12)])

                # Convert decoded bits back to string
                decoded_string = ''
                for i in range(0, len(decoded_bits), 8):
                    byte = decoded_bits[i:i+8]
                    if len(byte) < 8:
                        byte += [0] * (8 - len(byte))
                    decoded_string += chr(int(''.join(map(str, byte)), 2))

                error_vector = [a ^ b for a, b in zip(encoded_bits, noisy_bits)]

                print("\nOriginal text:                      ", text)
                print("Original text sent through channel: ", original_reproduced)
                print("Decoded text:                       ", decoded_string)
                print("Number of encoded vectors:          ", len(encoded_blocks))
                print("Number of errors:                   ", sum(error_vector))
                input("Press Any Key to continue...")
                print("\n" * 2)
                break

        # -------------------------------------
        # Choice 3: image pipeline (BMP 24-bit)
        # -------------------------------------
        # Flow:
        #  - open image and extract raw RGB bytes
        #  - pack bytes -> 12-bit blocks using `bytes_to_blocks`
        #  - encode blocks in parallel using `encode_blocks`
        #  - send both the raw 12-bit blocks (not encoded) and the encoded
        #    23-bit codewords through their respective channels (for side-by-side
        #    comparison of error rates)
        #  - decode encoded stream and convert both received streams back to
        #    bytes using `blocks_to_bytes` and save reconstructed images
        elif choice == '3':
            while True:
                file_path = input("Enter the path to the 24-bit BMP image file: ")
                try:
                    img = Image.open(file_path)
                except Exception as e:
                    print("Could not open image. Please check the file path and try again. Error:", e)
                    continue

                p = float(input("Enter error probability (e.g., 0.01 for 1%): "))
                if p < 0 or p > 1:
                    print("Invalid error probability. Please enter a value between 0 and 1.")
                    continue

                print(f"\nUsing image file: {file_path} and error probability: {p}")

                if img.mode != 'RGB':
                    img = img.convert('RGB')

                width, height = img.size
                raw_bytes = img.tobytes()
                
                orig_len_bytes = len(raw_bytes)
                orig_len_bits = orig_len_bytes * 8

                t0 = time.perf_counter()
                
                max_workers = max(1, os.cpu_count() or 1)

                # Converts bytes -> 12-bit ints by working in parallel with 3-byte-aligned chunks; each 3 bytes = 24 bits = 2 blocks of 12 bits
                blocks_int = bytes_to_blocks(raw_bytes, max_workers)
                t_bytes_to_bits = time.perf_counter() - t0

                chunksize = max(1, len(blocks_int) // (max_workers * 4))

                # Encode integer blocks in parallel (order-preserving)
                t_enc0 = time.perf_counter()
                encoded_blocks_int = encode_blocks(blocks_int, max_workers, chunksize)
                t_encode = time.perf_counter() - t_enc0

                # Sanity check: encoded count should match input blocks
                if len(encoded_blocks_int) != len(blocks_int):
                    print("Warning: encoded_blocks_int length mismatch; falling back to single-threaded encode")
                    encoded_blocks_int = [encode_int(u) for u in blocks_int]

                print(f"Image opened: {file_path}\nMode: {img.mode}, Size: {width}x{height}, Bytes: {orig_len_bytes}")
                print(f"Payload bits: {orig_len_bits}, blocks: {len(blocks_int)}, encoded codewords: {len(encoded_blocks_int)}")

                # Send NOT encoded blocks through channel in parallel
                t_ch0 = time.perf_counter()
                noisy_blocks = canal_blocks12(blocks_int, p, max_workers, chunksize)
                t_channel0 = time.perf_counter() - t_ch0

                # Send each codeword through channel in parallel
                t_ch1 = time.perf_counter()
                noisy_blocks_int = canal_blocks23(encoded_blocks_int, p, max_workers, chunksize)
                t_channel1 = time.perf_counter() - t_ch1

                # Count how many NOT encoded bits flipped in total
                flips_not_encoded = sum(((a ^ b).bit_count()) for a, b in zip(blocks_int, noisy_blocks))
                print(f"Bits flipped in NOT encoded stream by channel:  {flips_not_encoded} | {flips_not_encoded / orig_len_bits:.4%}")

                # Count how many encoded bits flipped in total
                flips = sum(((a ^ b).bit_count()) for a, b in zip(encoded_blocks_int, noisy_blocks_int))
                print(f"Bits flipped in encoded stream by channel:      {flips} | {flips / (len(encoded_blocks_int) * 23):.4%}")

                # Decode noisy codewords in parallel
                decoded_blocks_int = []
                try:
                    t_dec0 = time.perf_counter()
                    decoded_blocks_int = decode_blocks(noisy_blocks_int, max_workers, chunksize)
                    t_decode = time.perf_counter() - t_dec0
                except Exception as e:
                    print("Decoding failed for one of the codewords. Error:", e)
                    input("Press Any Key to continue...")
                    print("\n" * 2)
                    break

                # Convert NOT encoded 12-bit ints back to bytes in parallel taking even amount of chunks; each 2 blocks of 12 bits = 3 bytes
                t_bt0 = time.perf_counter()
                reconstructed_bytes = blocks_to_bytes(noisy_blocks, max_workers)
                t_bits_to_bytes0 = time.perf_counter() - t_bt0

                # Convert decoded 12-bit ints back to bytes in parallel taking even amount of chunks; each 2 blocks of 12 bits = 3 bytes
                t_bt1 = time.perf_counter()
                reconstructed_encoded_bytes = blocks_to_bytes(decoded_blocks_int, max_workers)
                t_bits_to_bytes1 = time.perf_counter() - t_bt1

                # Save reconstructed not encoded image
                out_path0 = file_path.rsplit('.', 1)[0] + '_reconstructed.bmp'
                if not save_to_file(out_path0, width, height, reconstructed_bytes):
                    break

                # Save reconstructed encoded image
                out_path1 = file_path.rsplit('.', 1)[0] + '_reconstructed_encoded.bmp'
                if not save_to_file(out_path1, width, height, reconstructed_encoded_bytes):
                    break

                # Count errors between original and not encoded payload sent through channel
                num_errors0 = sum(((a ^ b).bit_count()) for a, b in zip(raw_bytes, reconstructed_bytes))

                # Count errors between original and decoded payload sent through channel
                num_errors1 = sum(((a ^ b).bit_count()) for a, b in zip(raw_bytes, reconstructed_encoded_bytes))
                elapsed = time.perf_counter() - t0

                print(f"Reconstructed not encoded image saved to:       {out_path0}")
                print(f"Number of bit errors after reconstruction:      {num_errors0} / {orig_len_bits} | {num_errors0 / orig_len_bits:.4%}")
                print(f"Reconstructed encoded image saved to:           {out_path1}")
                print(f"Number of bit errors after decode (in payload): {num_errors1} / {orig_len_bits} | {num_errors1 / orig_len_bits:.4%}")

                # Print per-phase timings
                print(f"Timings (seconds): bytes->bits={t_bytes_to_bits:.3f}, encode={t_encode:.3f}, channel0={t_channel0:.3f}, channel1={t_channel1:.3f}, decode={t_decode:.3f}, bits->bytes0={t_bits_to_bytes0:.3f}, bits->bytes1={t_bits_to_bytes1:.3f}")
                print(f"Total processing time: {elapsed:.3f} seconds")

                input("Press Any Key to continue...")
                print("\n" * 2)
                break
        elif choice == '4':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == '__main__':
    multiprocessing.freeze_support()
    main()
