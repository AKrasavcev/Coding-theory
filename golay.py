import random

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
    return multiply(v, G())

def IMLD(w : list[int]) -> list[int]:
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


"""
v = test_vector
encoded = encode(v)
print("Original vector: ", v)
print("Encoded vector:  ", encoded)
noisy = canal(encoded, 0.1)
print("Noisy vector:    ", noisy)
decoded = decode(noisy)
print("Decoded vector:  ", decoded)
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
        print("not implemented yet")
    elif choice == '3':
        print("not implemented yet")
    elif choice == '4':
        print("Exiting program.")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")

#print(multiply(test_vector, G()))
#print(sum_vectors(test_vector, test_vector2))
#print(add_w24(test_vector))
#print(form_u(test_vector, ZEROES()))