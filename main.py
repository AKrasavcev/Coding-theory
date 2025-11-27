from PIL import Image
from functions import *
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
import itertools
import os
import time


def main():
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
        if choice == '1':
            while True:
                user_input = "101010101010"
                p = 0.1
                print(f"\nUsing default input vector: {user_input} and error probability: {p}")
                
                #user_input = input("\nEnter a 12-bit binary vector (e.g., 101010101010): ")
                #p = float(input("Enter error probability (e.g., 0.1 for 10%): "))
                if len(user_input) != 12 or any(bit not in '01' for bit in user_input):
                    print("Invalid input. Please enter a 12-bit binary vector.")
                elif p < 0 or p > 1:
                    print("Invalid error probability. Please enter a value between 0 and 1.")
                    continue
                else:
                    vector = [int(bit) for bit in user_input]
                    print("Original vector: ", vector)
                    encoded = encode(vector)
                    print("Encoded vector:  ", encoded)
                    noisy = canal(encoded, p)
                    print("Noisy vector:    ", noisy)
                    error_vector = xor_vectors(encoded, noisy)
                    print("Error vector:    ", error_vector)
                    print("Number of errors:", weight(error_vector))

                    while True:
                        choice2 = input("\nDo you want to change the noisy vector? (y/n): ")
                        if choice2.lower() == 'y':
                            print("Original encoded vector was: ", encoded)
                            print("Original noisy vector was  : ", noisy)
                            new_noisy_input = input("Enter the new 23-bit noisy binary vector: ")
                            if len(new_noisy_input) != 23 or any(bit not in '01' for bit in new_noisy_input):
                                print("Invalid input. Please enter a 23-bit binary vector.")
                            else:
                                new_noisy = [int(bit) for bit in new_noisy_input]
                                new_error_vector = xor_vectors(encoded, new_noisy)
                                print("\nNew noisy vector:", new_noisy)
                                print("Error vector:    ", new_error_vector)
                                print("Number of errors:", weight(new_error_vector))

                                set_action = 0
                                while True:
                                    choice3 = input("Proceed with this noisy vector? (y/n): ")
                                    if choice3.lower() == 'y':
                                        noisy = new_noisy.copy()
                                        error_vector = new_error_vector.copy()
                                        set_action = 1
                                        break
                                    elif choice3.lower() == 'n':
                                        set_action = 2
                                        break
                                    else:
                                        print("Invalid choice. Please enter 'y' or 'n'.")
                                if set_action == 1:
                                    break
                                elif set_action == 2:
                                    continue
                        elif choice2.lower() == 'n':
                            break
                        else:
                            print("Invalid choice. Please enter 'y' or 'n'.")

                    decoded = decode(noisy)
                    print("\nDecoded vector:  ", decoded)
                    input("Press Any Key to continue...")
                    print("\n" * 2)
                    break
        elif choice == '2':
            while True:
                text = input("Enter text to encode: ")
                p = float(input("Enter error probability (e.g., 0.1 for 10%): "))

                if p < 0 or p > 1:
                    print("Invalid error probability. Please enter a value between 0 and 1.")
                    continue
                else:
                    binary_string = ''.join(format(ord(char), '08b') for char in text)
                    #print("Original binary string:", binary_string)
                    original_noisy = []
                    for i in range(0, len(binary_string), 12):
                        chunk = binary_string[i:i+12]
                        if len(chunk) < 12:
                            chunk = chunk.ljust(12, '0')
                        vector = [int(bit) for bit in chunk]
                        original_noisy.extend(canal(vector, p))

                    original_reproduced = ''
                    for i in range(0, len(original_noisy), 8):
                        byte = original_noisy[i:i+8]
                        if len(byte) < 8:
                            byte += [0] * (8 - len(byte))
                        original_reproduced += chr(int(''.join(map(str, byte)), 2))

                    encoded_bits = []
                    noisy_bits = []
                    for i in range(0, len(binary_string), 12):
                        chunk = binary_string[i:i+12]
                        if len(chunk) < 12:
                            chunk = chunk.ljust(12, '0')
                        vector = [int(bit) for bit in chunk]
                        encoded_chunk = encode(vector)
                        encoded_bits.extend(encoded_chunk)
                        noisy_bits.extend(canal(encoded_chunk, p))

                    error_vector = xor_vectors(encoded_bits, noisy_bits)
                    #print("Encoded binary string:", ''.join(map(str, encoded_bits)))
                    #print("Noisy binary string:  ", ''.join(map(str, noisy_bits)))
                    #print("Error vector:     ", ''.join(map(str, error_vector)))

                    decoded_bits = []
                    for i in range(0, len(noisy_bits), 23):
                        chunk = noisy_bits[i:i+23]
                        if len(chunk) < 23:
                            chunk += [0] * (23 - len(chunk))
                        decoded_chunk = decode(chunk)
                        decoded_bits.extend(decoded_chunk)

                    decoded_string = ''
                    for i in range(0, len(decoded_bits), 8):
                        byte = decoded_bits[i:i+8]
                        if len(byte) < 8:
                            byte += [0] * (8 - len(byte))
                        decoded_string += chr(int(''.join(map(str, byte)), 2))

                    print("\nOriginal text:                      ", text)
                    print("Original text sent through channel: ", original_reproduced.strip('\x00'))
                    print("Decoded text:                       ", decoded_string.strip('\x00'))
                    print("Length of encoded vector:           ", len(encoded_bits))
                    print("Number of errors:                   ", sum(error_vector))
                    input("Press Any Key to continue...")
                    print("\n" * 2)
                    break
        elif choice == '3':
            # Pipeline: open 24-bit BMP, split to 12-bit blocks, encode (12->23), send through canal,
            # decode (23->12) and reconstruct the image bytes, then save reconstructed image.
            while True:
                """
                file_path = "gordon.bmp"
                try:
                    img = Image.open(file_path)
                except Exception as e:
                    print("Could not open image. Please check the file path and try again. Error:", e)
                    continue

                p = float(input("Enter error probability (e.g., 0.01 for 1%): "))
                if p < 0 or p > 1:
                    print("Invalid error probability. Please enter a value between 0 and 1.")
                    continue
                """
                file_path = input("Enter the path to the 24-bit BMP image file: ")
                try:
                    img = Image.open(file_path)
                except Exception as e:
                    print("Could not open image. Please check the file path and try again. Error:", e)
                    continue

                p = 0.05
                print(f"\nUsing image file: {file_path} and error probability: {p}")

                # Ensure RGB (24-bit) mode
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                width, height = img.size
                raw_bytes = img.tobytes()  # length = width * height * 3

                t0 = time.perf_counter()
                # original payload length in bytes and bits
                orig_len_bytes = len(raw_bytes)
                orig_len_bits = orig_len_bytes * 8
                # choose worker count
                max_workers = max(1, os.cpu_count() or 1)

                # Parallelize bytes -> 12-bit ints by splitting into 3-byte-aligned chunks
                if max_workers > 1 and len(raw_bytes) >= 3 * max_workers:
                    groups = (len(raw_bytes) // 3) // max_workers
                    chunk_size = max(3, groups * 3)  # ensure multiple of 3
                    chunks = [raw_bytes[i:i+chunk_size] for i in range(0, (len(raw_bytes)//3)*3, chunk_size)]
                    remainder = raw_bytes[len(chunks)*chunk_size:]
                    with ProcessPoolExecutor(max_workers=max_workers) as ex:
                        # use the chunk worker consistently
                        results = list(ex.map(bytes_to_12bit_ints, chunks, chunksize=max(1, len(chunks)//max_workers)))
                    blocks_int = [val for sub in results for val in sub]
                    if remainder:
                        # process trailing bytes (not multiple of 3) in main process using the chunk helper
                        blocks_int.extend(bytes_to_12bit_ints(remainder))
                else:
                    # single-threaded path using the same chunk helper for consistency
                    blocks_int = bytes_to_12bit_ints(raw_bytes)
                t_bytes_to_bits = time.perf_counter() - t0

                # choose worker count
                max_workers = max(1, os.cpu_count() or 1)

                # start timer for the full image-processing pipeline (starts at bytes->bits)
                start_time = t0

                # encode integer blocks in parallel (order-preserving)
                chunksize = max(1, len(blocks_int) // (max_workers * 4))
                t_enc0 = time.perf_counter()
                with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    encoded_blocks_int = list(ex.map(encode_int, blocks_int, chunksize=chunksize))
                t_encode = time.perf_counter() - t_enc0

                # Sanity check: encoded count should match input blocks
                if len(encoded_blocks_int) != len(blocks_int):
                    print("Warning: encoded_blocks_int length mismatch; falling back to single-threaded encode")
                    encoded_blocks_int = [encode_int(u) for u in blocks_int]

                print(f"Image opened: {file_path}\nMode: {img.mode}, Size: {width}x{height}, Bytes: {orig_len_bytes}")
                print(f"Payload bits: {orig_len_bits}, blocks: {len(blocks_int)}, encoded codewords: {len(encoded_blocks_int)}")

                # apply channel per-codeword in parallel (process pool) using integer channel
                t_ch0 = time.perf_counter()
                with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    noisy_blocks_int = list(ex.map(canal_int, encoded_blocks_int, itertools.repeat(p), chunksize=chunksize))
                t_channel = time.perf_counter() - t_ch0

                # count how many encoded bits flipped in total using integer XOR popcount
                flips = sum(((a ^ b).bit_count()) for a, b in zip(encoded_blocks_int, noisy_blocks_int))
                print(f"Bits flipped in encoded stream by channel: {flips}")

                # decode noisy codewords in parallel (process pool)
                decoded_blocks_int = []
                try:
                    t_dec0 = time.perf_counter()
                    with ProcessPoolExecutor(max_workers=max_workers) as ex:
                        decoded_blocks_int = list(ex.map(decode_int, noisy_blocks_int, chunksize=chunksize))
                    t_decode = time.perf_counter() - t_dec0
                except Exception as e:
                    print("Decoding failed for one of the codewords. Error:", e)
                    input("Press Any Key to continue...")
                    print("\n" * 2)
                    break

                # sanity check: decoded count should match original block count
                if len(decoded_blocks_int) != len(blocks_int):
                    print(f"Decoded blocks {len(decoded_blocks_int)} != original blocks {len(blocks_int)}; falling back to single-threaded decode")
                    try:
                        decoded_blocks_int = [decode_int(cw) for cw in noisy_blocks_int]
                    except Exception as e:
                        print("Fallback decode failed:", e)
                        input("Press Any Key to continue...")
                        print("\n" * 2)
                        break

                # convert decoded 12-bit ints back to bytes (trimming to original length)
                # Parallelize 12-bit ints -> bytes by splitting decoded blocks into chunks
                t_bt0 = time.perf_counter()
                if max_workers > 1 and len(decoded_blocks_int) >= max_workers * 2:
                    # choose per-chunk block count so (per * 12) is a multiple of 8 bits
                    # this requires per to be even (12*per mod 8 == 0 when per is even)
                    per = max(1, len(decoded_blocks_int) // max_workers)
                    if per % 2 == 1:
                        per += 1
                    if per < 2:
                        per = 2
                    ranges = [decoded_blocks_int[i:i+per] for i in range(0, len(decoded_blocks_int), per)]
                    with ProcessPoolExecutor(max_workers=max_workers) as ex:
                        parts = list(ex.map(blocks_ints_to_bytes, ranges, chunksize=max(1, len(ranges)//max_workers)))
                    reconstructed_bytes = b''.join(parts)
                else:
                    # use chunk helper for single-threaded path as well
                    reconstructed_bytes = blocks_ints_to_bytes(decoded_blocks_int)
                t_bits_to_bytes = time.perf_counter() - t_bt0

                # write reconstructed image as BMP
                out_path = file_path.rsplit('.', 1)[0] + '_reconstructed.bmp'
                try:
                    out_img = Image.frombytes('RGB', (width, height), reconstructed_bytes)
                    out_img.save(out_path, format='BMP')
                except Exception as e:
                    print('Could not reconstruct/save image. Error:', e)
                    input("Press Any Key to continue...")
                    print("\n" * 2)
                    break

                # report bit errors between original and decoded payload by XORing bytes
                num_errors = sum(((a ^ b).bit_count()) for a, b in zip(raw_bytes, reconstructed_bytes))
                print(f"Reconstructed image saved to: {out_path}")
                print(f"Number of bit errors after decode (in payload): {num_errors} / {orig_len_bits}")

                # print per-phase timings
                print(f"Timings (seconds): bytes->bits={t_bytes_to_bits:.3f}, encode={t_encode:.3f}, channel={t_channel:.3f}, decode={t_decode:.3f}, bits->bytes={t_bits_to_bytes:.3f}")

                # stop timer and report elapsed time for the pipeline
                elapsed = time.perf_counter() - start_time
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
    main()
