'''
File Name: DecryptEncrypt.py

Description:
    * Implement the encryption and decryption by importing and aggregating functions from other files: DES_IMPLEMENTATION, F_FUNCTION, Key_Schedule and Bit_manipulation.
    * The encrypt function takes the plaintext, key and the DES version as input and return a ciphertext as output. 
    * The decrypt function takes the ciphertext, key and the DES version as input and return a plaintext as output.
    * The generate_round_keys function takes a bit string as input and return a list of keys for each round (16 rounds)
    * The analysis_table function generates comparative analysis of the DES encryption process depending on different mode parameter. A table is generated to display the ciphertexts
    and analyze the avalance effect across multiple DES variants.


Author: @Nhu Nam Do Nguyen & @Chi Tai Nguyen

Student ID: c3444589 & c3444339

Date: 30 May 2025

Course: COMP3260 - Assignment 2
'''
from DES_IMPLEMENTATION import *
from F_FUNCTION import f_function
from Key_Schedule import *
from Bit_manipulation import xor, bin2hex

def encrypt(plaintext, key, version='DES0'):
    #check the length of the plaintext
    if len(plaintext) != 64:
        raise ValueError("Plaintext must be 64 bits")

    # Store ciphertext from every round
    cipherrounds = []

    #get round keys
    round_keys = generate_round_keys(key)

    #initial permutation
    permuted = initial_perm(plaintext)

    #divide L and R
    L = permuted[:32]
    R = permuted[32:]
    
    #perform 16 Feistel rounds
    for i in range(16):
        # store pre-transformation Right Half
        old_R = R

        #apply f-function to right half
        f_func_R = f_function(R, round_keys[i], version)

        #xor with left half
        R = xor(L, f_func_R)

        #swap back with original R
        L = old_R

        # record the ciphertext after each round
        cipherrounds.append(L + R)

    #combine the final result for inverse permutaiton
    combine = R+L
    ciphertext = inverse_perm(combine)
        #return ciphertext
    return (ciphertext, cipherrounds)
            

def decrypt(ciphertext, key, version='DES0'):
    if len(ciphertext) != 64:
        raise ValueError("Ciphertext must be 64-bit long")
    #reverse the list for decryption
    round_keys = generate_round_keys(key)[::-1]
    
    #initial permutation
    permuted = initial_perm(ciphertext)

    #the rest will be implmented same with the encryption function
    L = permuted[:32]
    R = permuted[32:]

    for i in range(16):
        #swapping
        old_R = R
        #apply left function to right half
        f_func_R = f_function(R, round_keys[i], version)

        #xor with left half
        R = xor(L, f_func_R)
        #swap back with original R
        L = old_R

    #combine the final result for inverse permutaiton
    combine = R+L
    plaintext = inverse_perm(combine)
        #return ciphertext
    return plaintext

def generate_round_keys(master):
    # apply PC1 to master key
    permuted = apply_pc1(master)

    # split permuted master key into 2 halves
    C, D, splits = ["0"] * 16, ["0"] * 16, split_key(permuted)
    C[0] = splits[0]
    D[0] = splits[1]

    round_keys = list()
    for i in range(16):
        # Perform left shift on each half
        # The number of bits to shift for each round is predefined in Rotation
        C[i] = shift_left(C[i], Rotation[i])
        D[i] = shift_left(D[i], Rotation[i])

        # Join and apply PC2 transformation to the halves
        joined = C[i] + D[i]
        round_keys.append(apply_pc2(joined))

        # Prepare for next round key generation
        if (i != 15):
            C[i + 1] = C[i]
            D[i + 1] = D[i]
    
    return round_keys

def analysis_table(p1, p2, k1, k2, mode='same-key'):
    # Create a table to compare the ciphertexts after each round
    cipher1, cipher2 = [], []
    allp1rounds, allp2rounds = [], []

    if mode == 'same-key':
        output = "P and P' under K\n"
    elif mode == 'different-key':
        output = "P under K and K'\n"

    # Encrypt plaintexts with the specified keys and versions
    versions = ['DES0', 'DES1', 'DES2', 'DES3']
    for version in versions:
        if mode == 'same-key':
            ciphertext_P1, p1rounds = encrypt(p1, k1, version)
            ciphertext_P2, p2rounds = encrypt(p2, k1, version)
        elif mode == 'different-key':
            ciphertext_P1, p1rounds = encrypt(p1, k1, version)
            ciphertext_P2, p2rounds = encrypt(p1, k2, version)

        # Store the ciphertexts and rounds for each version
        cipher1.append(ciphertext_P1)
        cipher2.append(ciphertext_P2)
        allp1rounds.append(p1rounds)
        allp2rounds.append(p2rounds)

    # Display ciphertexts by DES variants
    output += "Ciphertext C:\n"
    for i in range(len(versions)):
        output += "\t" + versions[i] + ":\t\t" + cipher1[i] + f" (H: {bin2hex(cipher1[i])})" + "\n"

    output += "Ciphertext C':\n"
    for i in range(len(versions)):
        output += "\t" + versions[i] + ":\t\t" + cipher2[i] + f" (H: {bin2hex(cipher2[i])})" + "\n"

    # Avalanche effect analysis
    output += "\nRound\t\t\tDES0\tDES1\tDES2\tDES3\n"

    init_diff = xor(p1, p2).count('1') if mode == 'same-key' else 0     # Number of differing bits in p1 and p2
    output += f"\t0\t\t\t{init_diff}\t\t{init_diff}\t\t{init_diff}\t\t{init_diff}\n"

    # Calculate the number of differing bits in ciphertexts after each round
    for i in range(len(p1rounds)):
        output += f"\t{i+1}\t\t\t"
        for j in range(len(allp1rounds)):
            output += str(xor(allp1rounds[j][i], allp2rounds[j][i]).count('1')) + "\t\t"
        output += "\n"
    return output
