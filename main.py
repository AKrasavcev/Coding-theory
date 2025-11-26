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

                # helpers to convert between bytes and bits (MSB-first per byte)
                def bytes_to_bits(b: bytes) -> list[int]:
                    bits = [((byte >> i) & 1) for byte in b for i in range(7, -1, -1)]
                    return bits

                def bits_to_bytes(bits: list[int]) -> bytes:
                    # pad to full bytes
                    n = ((len(bits) + 7) // 8) * 8
                    bits = bits + [0] * (n - len(bits))
                    out = bytearray()
                    for i in range(0, len(bits), 8):
                        byte = 0
                        for bit in bits[i:i+8]:
                            byte = (byte << 1) | (bit & 1)
                        out.append(byte)
                    return bytes(out)

                t0 = time.perf_counter()
                orig_bits = bytes_to_bits(raw_bytes)
                t_bytes_to_bits = time.perf_counter() - t0
                orig_len_bytes = len(raw_bytes)

                # chunk into 12-bit blocks and pad the last block with zeros if needed
                n_blocks = (len(orig_bits) + 11) // 12
                pad_bits = n_blocks * 12 - len(orig_bits)
                padded_bits = orig_bits + [0] * pad_bits

                # build 12-bit blocks list
                blocks = [padded_bits[i:i+12] for i in range(0, len(padded_bits), 12)]

                # choose worker count
                max_workers = max(1, os.cpu_count() or 1)

                # start timer for the full image-processing pipeline (starts at bytes->bits)
                start_time = t0

                # encode blocks in parallel (order-preserving) using processes to avoid GIL
                # Use an adaptive chunksize so each worker processes a batch of blocks
                chunksize = max(1, len(blocks) // (max_workers * 4))
                t_enc0 = time.perf_counter()
                with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    encoded_blocks = list(ex.map(encode, blocks, chunksize=chunksize))
                t_encode = time.perf_counter() - t_enc0

                # flatten encoded bits
                encoded_bits = [bit for cw in encoded_blocks for bit in cw]

                print(f"Image opened: {file_path}\nMode: {img.mode}, Size: {width}x{height}, Bytes: {orig_len_bytes}")
                print(f"Payload bits: {len(orig_bits)}, blocks: {n_blocks}, encoded bits: {len(encoded_bits)}")

                # apply channel per-codeword in parallel (process pool)
                t_ch0 = time.perf_counter()
                with ProcessPoolExecutor(max_workers=max_workers) as ex:
                    noisy_blocks = list(ex.map(canal, encoded_blocks, itertools.repeat(p), chunksize=chunksize))
                t_channel = time.perf_counter() - t_ch0

                # flatten noisy encoded stream
                noisy_encoded = [bit for cw in noisy_blocks for bit in cw]

                # count how many encoded bits flipped by the channel
                # Use threads to parallelize the reduction without copying the lists.
                def _count_chunk(a, b, start, end):
                    c = 0
                    for i in range(start, end):
                        if a[i] != b[i]:
                            c += 1
                    return c

                total_len = min(len(encoded_bits), len(noisy_encoded))
                if total_len == 0:
                    flips = 0
                else:
                    # small adaptive chunk size; increase divisor to create larger chunks
                    chunk_size = max(1, total_len // (max_workers * 2))
                    ranges = [(i, min(total_len, i + chunk_size)) for i in range(0, total_len, chunk_size)]
                    with ThreadPoolExecutor(max_workers=max_workers) as tex:
                        futures = [tex.submit(_count_chunk, encoded_bits, noisy_encoded, s, e) for s, e in ranges]
                        flips = sum(f.result() for f in futures)

                print(f"Bits flipped in encoded stream by channel: {flips}")

                # decode noisy codewords in parallel (process pool)
                decoded_blocks = []
                try:
                    t_dec0 = time.perf_counter()
                    with ProcessPoolExecutor(max_workers=max_workers) as ex:
                        decoded_blocks = list(ex.map(decode, noisy_blocks, chunksize=chunksize))
                    t_decode = time.perf_counter() - t_dec0
                except Exception as e:
                    print("Decoding failed for one of the codewords. Error:", e)
                    # abort this run and let user retry with smaller p
                    input("Press Any Key to continue...")
                    print("\n" * 2)
                    break

                # flatten decoded bits
                decoded_bits = [bit for db in decoded_blocks for bit in db]

                # trim decoded bits to original length and convert back to bytes
                decoded_bits = decoded_bits[:len(orig_bits)]
                t_bt0 = time.perf_counter()
                reconstructed_bytes = bits_to_bytes(decoded_bits)[:orig_len_bytes]
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

                # report bit errors between original and decoded payload
                error_vector = [a ^ b for a, b in zip(orig_bits, decoded_bits)]
                num_errors = sum(error_vector)
                print(f"Reconstructed image saved to: {out_path}")
                print(f"Number of bit errors after decode (in payload): {num_errors} / {len(orig_bits)}")

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
        elif choice == '5':
            print("Running tests...")
            print("test vector:", test_vector)
            encoded = encode_int(bits_list_to_int(test_vector))
            print("Encoded vector:", int_to_bits_list(encoded, 23))
            noisy = canal_int(encoded, 0.1)
            print("Noisy vector:  ", int_to_bits_list(noisy, 23))
            decoded = decode_int(noisy)
            print("Decoded vector:", int_to_bits_list(decoded, 12))
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

if __name__ == '__main__':
    main()

#print(multiply(test_vector, G()))
#print(sum_vectors(test_vector, test_vector2))
#print(add_w24(test_vector))
#print(form_u(test_vector, ZEROES()))