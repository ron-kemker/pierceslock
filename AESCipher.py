# -*- coding: utf-8 -*-
"""
AESCipher.py
By Ronald Kemker
14 Jun 2021

Description: Runs AES-256 encryption

"""

from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.hmac import HMAC, hashes
from cryptography.hazmat.primitives.padding import PKCS7
import os, base64, time, struct, binascii
from cryptography.exceptions import InvalidSignature
from cryptography import utils

class InvalidToken(Exception):
    pass

class AESCipher(object):
    '''
    AESCipher Class
    '''
        
    def __init__(self, block_size=32):
        '''
        AESCipher Object
        
        Parameters
        ----------
        block_size : int (default=32)
           Description 
    
        Attributes
        ----------
        block_size : int (default=32)
           Description 
        _MAX_CLOCK_SKEW : int (default=60)
           Description 
           
    
        Returns
        -------
        None

        '''
        self.block_size = block_size
        self._MAX_CLOCK_SKEW = 60
            
    def generate_key(self):
        return os.urandom(self.block_size)
        
    def encrypt(self, msg, key, signing_key):
        '''
        Performs AES-256 (CBC Mode) encryption with a given key and 
        Hashed-based message authentication (HMAC).
        

        Parameters
        ----------
        msg : byte-string
            The message that needs to be encrypted.
        key : byte-string
            encryption key.
        signing_key : byte_string
            authentication key.

        Returns
        -------
        byte-string
            Output cipher text.

        '''        
            
        # Record time for message authentication
        current_time = int(time.time())
        
        # Padding is a way to take data that may or may not be a multiple of  
        # the block size for a cipher and extend it out so that it is. This is 
        # required for many block cipher modes as they require the data to be 
        # encrypted to be an exact multiple of the block size.

        # PKCS7 padding works by appending N bytes with the value of chr(N), 
        # where N is the number of bytes required to make the final block of 
        # data the same size as the block size.
        padder = PKCS7(self.block_size * 8).padder()
        padded_data = padder.update(msg) + padder.finalize()


        # initialization_vector. Random bytes. They do not need to be kept 
        # secret and they can be included in a transmitted message. Must be the 
        # same number of bytes as the block_size of the cipher. Each time 
        # something is encrypted a new initialization_vector should be 
        # generated. Do not reuse an initialization_vector with a given key, 
        # and particularly do not use a constant initialization_vector.
        iv = self.generate_key()


        # AES (Advanced Encryption Standard) is a block cipher standardized 
        # by NIST. AES is both fast, and cryptographically strong. It is a 
        aes = AES(key)
        
        # Set encryption to 256 bits (32 * 8 = 256)
        aes.block_size = self.block_size * 8
        
        # CBC (Cipher Block Chaining) is a mode of operation for block ciphers. 
        # It is considered cryptographically strong.
        cbc = CBC(iv)
        
        # AES encryptor using CBC mode
        encryptor = Cipher(aes, cbc).encryptor()
        
        
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        
        # Pack the current time, initialization vector, and ciphertext
        basic_parts = (
            b"\x80" + struct.pack(">Q", current_time) + iv + ciphertext
        )
        
        # SHA-256 is a cryptographic hash function from the SHA-2 family and 
        # is standardized by NIST. It produces a 256-bit message digest.
        crypto_hash = hashes.SHA256()

        # Hashed-based message authentication (HMAC)
        # Tool to calculate message authentication codes using cryptographic
        # hash function coupled with a secret key.
        h = HMAC(signing_key, crypto_hash)
        h.update(basic_parts) # bytes to hash and authenticate
        hmac = h.finalize() # finalize current context and return msg as bytes
        
        return base64.urlsafe_b64encode(basic_parts + hmac)

    def encrypt_file(self, file_path, key, signing_key):
        
        with open(file_path, 'rb') as f:
            msg = f.read()
            
        return self.encrypt(msg, key, signing_key)
            

    def decrypt(self, ciphertext, key, signing_key, ttl=None):
        '''
        Performs AES-256 (CBC Mode) decryption with a given key and 
        Hashed-based message authentication (HMAC).
        
        Parameters
        ----------
        ciphertext : TYPE
            DESCRIPTION.
        key : TYPE
            DESCRIPTION.
        signing_key : TYPE
            DESCRIPTION.
        ttl : TYPE, optional
            DESCRIPTION. The default is None.

        Returns
        -------
        None.
        
        Raises
        ------
        InvalidToken Exception : raises if token has expired

        '''
        
        # Split file into timestamp and data and encrpyted message
        timestamp, data = self._get_unverified_token_data(ciphertext)

        # Get current timestamp for message authentication
        current_time = int(time.time())
        
        # If defined, validate message delivery is within time-to-live
        if ttl is not None:
            if timestamp + ttl < current_time:
                raise InvalidToken
            
        # If message took longer than _MAX_CLOCK_SKEW seconds to arrive
        if current_time + self._MAX_CLOCK_SKEW < timestamp:
            raise InvalidToken

        # SHA-256 is a cryptographic hash function from the SHA-2 family and 
        # is standardized by NIST. It produces a 256-bit message digest.
        crypto_hash = hashes.SHA256()

        # Hashed-based message authentication (HMAC)
        # Tool to calculate message authentication codes using cryptographic
        # hash function coupled with a secret key.
        h = HMAC(signing_key, crypto_hash)
        h.update(data[:-32]) # Grab the signing key
        
        # Authenticate message to make sure it has not been tampered with
        try:
            h.verify(data[-32:])
        except InvalidSignature:
            raise InvalidToken                

        # Extract initialization vector
        iv = data[9:9+self.block_size]
        
        # Extract encrypted message
        ciphertext = data[9+self.block_size:-32]

        # Initialize AES object with encryption key
        aes = AES(key)
        
        # Set encryption to 256 bits (32 * 8 = 256)        
        aes.block_size = self.block_size * 8

        # CBC (Cipher Block Chaining) is a mode of operation for block ciphers. 
        # It is considered cryptographically strong.
        cbc = CBC(iv)

        decryptor = Cipher(aes, cbc).decryptor()
        plaintext_padded = decryptor.update(ciphertext)
        try:
            plaintext_padded += decryptor.finalize()
        except ValueError:
            raise InvalidToken
        unpadder = PKCS7(self.block_size * 8).unpadder()

        unpadded = unpadder.update(plaintext_padded)
        try:
            unpadded += unpadder.finalize()
        except ValueError:
            raise InvalidToken
        return unpadded


    def _get_unverified_token_data(self, token):
        utils._check_bytes("token", token)
        try:
            data = base64.urlsafe_b64decode(token)
        except (TypeError, binascii.Error):
            raise InvalidToken

        if not data or data[0] != 0x80:
            raise InvalidToken

        try:
            (timestamp,) = struct.unpack(">Q", data[1:9])
        except struct.error:
            raise InvalidToken
        return timestamp, data

if __name__ == "__main__":

    msg = b'My wife is amazing!!!'

    cipher = AESCipher()
    
    key = cipher.generate_key()
    signing_key = cipher.generate_key()
    ciphertext = cipher.encrypt(msg, key, signing_key)
    
    
    deciphertext = cipher.decrypt(ciphertext, key, signing_key)
    
    if deciphertext != msg:
        raise ValueError
    
  