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


v = test_vector
encoded = encode(v)
print("Original vector: ", v)
print("Encoded vector:  ", encoded)
noisy = canal(encoded, 0.1)
print("Noisy vector:    ", noisy)
decoded = decode(noisy)
print("Decoded vector:  ", decoded)

#print(multiply(test_vector, G()))
#print(sum_vectors(test_vector, test_vector2))
#print(add_w24(test_vector))
#print(form_u(test_vector, ZEROES()))