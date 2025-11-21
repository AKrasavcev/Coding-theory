from PIL import Image
from functions import encode, decode, canal, xor_vectors, weight

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

            orig_bits = bytes_to_bits(raw_bytes)
            orig_len_bytes = len(raw_bytes)

            # chunk into 12-bit blocks and pad the last block with zeros if needed
            n_blocks = (len(orig_bits) + 11) // 12
            pad_bits = n_blocks * 12 - len(orig_bits)
            padded_bits = orig_bits + [0] * pad_bits

            # encode each 12-bit block into 23-bit codeword
            encoded_bits = []
            for i in range(0, len(padded_bits), 12):
                block = padded_bits[i:i+12]
                encoded_bits.extend(encode(block))

            print(f"Image opened: {file_path}\nMode: {img.mode}, Size: {width}x{height}, Bytes: {orig_len_bytes}")
            print(f"Payload bits: {len(orig_bits)}, blocks: {n_blocks}, encoded bits: {len(encoded_bits)}")

            # send encoded stream through channel
            noisy_encoded = canal(encoded_bits, p)

            # count how many encoded bits flipped by the channel
            flips = sum(1 for a, b in zip(encoded_bits, noisy_encoded) if a != b)
            print(f"Bits flipped in encoded stream by channel: {flips}")

            # decode noisy encoded stream back into 12-bit blocks
            decoded_bits = []
            try:
                for i in range(0, len(noisy_encoded), 23):
                    cw = noisy_encoded[i:i+23]
                    if len(cw) < 23:
                        cw += [0] * (23 - len(cw))
                    decoded_block = decode(cw)  # returns 12 bits
                    decoded_bits.extend(decoded_block)
            except Exception as e:
                print("Decoding failed for one of the codewords. Error:", e)
                # abort this run and let user retry with smaller p
                input("Press Any Key to continue...")
                print("\n" * 2)
                break

            # trim decoded bits to original length and convert back to bytes
            decoded_bits = decoded_bits[:len(orig_bits)]
            reconstructed_bytes = bits_to_bytes(decoded_bits)[:orig_len_bytes]

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

            input("Press Any Key to continue...")
            print("\n" * 2)
            break
    elif choice == '4':
        print("Exiting program.")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")

#print(multiply(test_vector, G()))
#print(sum_vectors(test_vector, test_vector2))
#print(add_w24(test_vector))
#print(form_u(test_vector, ZEROES()))