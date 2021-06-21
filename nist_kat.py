# -*- coding: utf-8 -*-
"""
nist_kat.py
By Ronald Kemker
19 Jun 2021

Description: This validates the algorithm against the Known Answer Tests (KAT)
             established by NIST.

"""


from AESCipher import AESCipher as AES
import unittest, binascii

class NIST_Testing(unittest.TestCase):

    
    def test_CBCGFSbox256e(self):

        filename = 'KAT_AES/CBCGFSbox256e.txt'
    
        with open(filename, 'r') as f:
            txt_file = f.readlines()
        
        for i in range(3,len(txt_file), 6):
            key = txt_file[i].split(' = ')[-1][:-1]
            iv =  txt_file[i+1].split(' = ')[-1][:-1]
            plaintext = txt_file[i+2].split(' = ')[-1][:-1]
            ciphertext = txt_file[i+3].split(' = ')[-1][:-1]
    
            key = binascii.unhexlify(key)
            iv = binascii.unhexlify(iv)
            plaintext = binascii.unhexlify(plaintext)
            ciphertext = binascii.unhexlify(ciphertext)
    
            aes = AES()
            encrypt_out, _ = aes.encrypt(plaintext, key, iv)
            
            self.assertEqual(encrypt_out[:16], ciphertext)

            decrypt_out = aes.decrypt(encrypt_out, key, iv)
            self.assertEqual(decrypt_out, plaintext)
            

    
    def test_CBCKeySbox256e(self):

        filename = 'KAT_AES/CBCKeySbox256e.txt'
    
        with open(filename, 'r') as f:
            txt_file = f.readlines()
        
        for i in range(3,len(txt_file), 6):
            key = txt_file[i].split(' = ')[-1][:-1]
            iv =  txt_file[i+1].split(' = ')[-1][:-1]
            plaintext = txt_file[i+2].split(' = ')[-1][:-1]
            ciphertext = txt_file[i+3].split(' = ')[-1][:-1]
    
            key = binascii.unhexlify(key)
            iv = binascii.unhexlify(iv)
            plaintext = binascii.unhexlify(plaintext)
            ciphertext = binascii.unhexlify(ciphertext)
    
            aes = AES()
            encrypt_out, _ = aes.encrypt(plaintext, key, iv)
            
            self.assertEqual(encrypt_out[:16], ciphertext)
            
            decrypt_out = aes.decrypt(encrypt_out, key, iv)
            self.assertEqual(decrypt_out, plaintext)            
    def test_CBCVarTxt256e(self):

        filename = 'KAT_AES/CBCVarTxt256e.txt'
    
        with open(filename, 'r') as f:
            txt_file = f.readlines()
        
        for i in range(3,len(txt_file), 6):
            key = txt_file[i].split(' = ')[-1][:-1]
            iv =  txt_file[i+1].split(' = ')[-1][:-1]
            plaintext = txt_file[i+2].split(' = ')[-1][:-1]
            ciphertext = txt_file[i+3].split(' = ')[-1][:-1]
    
            key = binascii.unhexlify(key)
            iv = binascii.unhexlify(iv)
            plaintext = binascii.unhexlify(plaintext)
            ciphertext = binascii.unhexlify(ciphertext)
    
            aes = AES()
            encrypt_out, _ = aes.encrypt(plaintext, key, iv)
            
            self.assertEqual(encrypt_out[:16], ciphertext)

            decrypt_out = aes.decrypt(encrypt_out, key, iv)
            self.assertEqual(decrypt_out, plaintext)

    def test_CBCVarKey256e(self):

        filename = 'KAT_AES/CBCVarKey256e.txt'
    
        with open(filename, 'r') as f:
            txt_file = f.readlines()
        
        for i in range(3,len(txt_file), 6):
            key = txt_file[i].split(' = ')[-1][:-1]
            iv =  txt_file[i+1].split(' = ')[-1][:-1]
            plaintext = txt_file[i+2].split(' = ')[-1][:-1]
            ciphertext = txt_file[i+3].split(' = ')[-1][:-1]
    
            key = binascii.unhexlify(key)
            iv = binascii.unhexlify(iv)
            plaintext = binascii.unhexlify(plaintext)
            ciphertext = binascii.unhexlify(ciphertext)
    
            aes = AES()
            encrypt_out, _ = aes.encrypt(plaintext, key, iv)
            
            self.assertEqual(encrypt_out[:16], ciphertext)

            decrypt_out = aes.decrypt(encrypt_out, key, iv)
            self.assertEqual(decrypt_out, plaintext)

            
if __name__ == '__main__':
    unittest.main()

