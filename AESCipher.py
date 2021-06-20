# -*- coding: utf-8 -*-
"""
AESCipher.py
By Ronald Kemker
18 Jun 2021

Description: Runs AES-256 encryption

"""

import os, base64, time, struct, binascii
from cryptography.hazmat.primitives.ciphers.algorithms import AES
from cryptography.hazmat.primitives.ciphers.modes import CBC
from cryptography.hazmat.primitives.ciphers import Cipher
from cryptography.hazmat.primitives.hmac import HMAC, hashes
from cryptography.hazmat.primitives.padding import PKCS7
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
           The number of bits in each block 
        _MAX_CLOCK_SKEW : int (default=60)
           The max time the message can be validated in (not implemented)
           
    
        Returns
        -------
        None

        '''
        self.block_size = block_size
        self._MAX_CLOCK_SKEW = 60
            
    def generate_key(self):
        '''
        Generates a random 256-bit key (for encryption, signing, and 
        initialization)     
        
        Returns
        -------
        key : byte string
            The randomly generated key

        '''
        return os.urandom(self.block_size)
        
    def encrypt(self, msg, key, signing_key, iv = None):
        '''
        Performs AES-256 (CBC Mode) encryption with a given key.
        

        Parameters
        ----------
        msg : byte-string
            The message that needs to be encrypted.
        key : byte-string
            encryption key.
        signing_key : byte_string
            authentication key.
        iv : byte_string, optional
            initialization vector (default=None)

        Returns
        -------
        byte-string
            Output cipher text.

        '''        
            
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
        if not iv:
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
        
        return ciphertext, iv
        
    def encode_authentication(self, ciphertext, iv):
        '''
        Perform SHA-256 Hash-based Message Authentication on the ciphertext

        Parameters
        ----------
        ciphertext : bytes string
            DESCRIPTION.
        iv : bytes string
            DESCRIPTION.

        Returns
        -------
        bytes-string
            Ciphertext with authentication code

        '''
        # Record time for message authentication
        current_time = int(time.time())    
    
        # Pack the current time, initialization vector, and ciphertext
        basic_parts = (
            b"\x80" + struct.pack(">Q", current_time) + iv + ciphertext
        )
        
        # SHA-256 is a cryptographic hash function from the SHA-2 family and 
        # is standardized by NIST. It produces a 256-bit message digest.
        crypto_hash = hashes.SHA256()

        # Hashed-based message authentication (HMAC)
        # Tool to calculate message authentication codes using 
        # cryptographic hash function coupled with a secret key.
        h = HMAC(signing_key, crypto_hash)
        h.update(basic_parts) # bytes to hash and authenticate
        hmac = h.finalize() # finalize current context, return msg as bytes        
        return base64.urlsafe_b64encode(basic_parts + hmac)

    def encrypt_file(self, file_path, key, signing_key):
        
        with open(file_path, 'rb') as f:
            msg = f.read()
            
        ciphertext, iv = self.encrypt(msg, key, signing_key)
        encoded = self.encode_authentication(ciphertext, iv)
        return encoded
            
    def decrypt(self, ciphertext, key, iv, ttl=None):
        '''
        Performs AES-256 (CBC Mode) decryption with a given key and 
        Hashed-based message authentication (HMAC).
        
        Parameters
        ----------
        ciphertext : byte string
            The encrypted message
        key : byte-string
            encryption key.
        iv : byte string
            initialization vector 
        ttl : int, optional
            The "time-to-live" for a given message.  
            TODO: This needs to be intergrated somehow with the current app

            
        Returns
        -------
        deciphertext : byte string
            The decrypted and unpadded message
        
        Raises
        ------
        InvalidToken Exception : 
            raises if any part of the decrpytion process is interrupted, 
            including: 
                - Error with decryption
                - Error with unpadding

        '''
        
        # Initialize AES object with encryption key
        aes = AES(key)
        
        # Set encryption to 256 bits (32 * 8 = 256)        
        aes.block_size = self.block_size * 8

        # CBC (Cipher Block Chaining) is a mode of operation for block ciphers. 
        # It is considered cryptographically strong.
        cbc = CBC(iv)

        # AES decryption using CBC mode
        decryptor = Cipher(aes, cbc).decryptor()
        plaintext_padded = decryptor.update(ciphertext)
        try:
            plaintext_padded += decryptor.finalize()
        except ValueError:
            raise InvalidToken
        
        # Unpadding the plain text
        unpadder = PKCS7(self.block_size * 8).unpadder()

        unpadded = unpadder.update(plaintext_padded)
        try:
            unpadded += unpadder.finalize()
        except ValueError:
            raise InvalidToken
        return unpadded

    def authenticate(self, ciphertext, signing_key, ttl=None):
        '''
        Authenticate transmitted message
        
        Parameters
        ----------
        ciphertext : byte string
            The encrypted message
        signing_key : byte string
            authentication key.
        ttl : int, optional
            The "time-to-live" for a given message.  
            TODO: This needs to be intergrated somehow with the current app
            
        Returns
        -------
        ciphertext : byte string
            The encrypted message
        iv : byte string
            initialization vector        
        
        Raises
        ------
        InvalidToken Exception : 
            raises if any part of the decrpytion process is interrupted, 
            including: 
                - ttl has expired
                - Message is not authentic

        '''
        
        # Split file into timestamp and data and encrpyted message
        timestamp, data = self._get_unverified_token_data(ciphertext)

        # Get current timestamp for message authentication
        current_time = int(time.time())
        
        # If defined, validate message delivery is within time-to-live
        if ttl is not None:
            if timestamp + ttl < current_time:
                raise InvalidToken

        # TODO: Consider re-adding this if it makes sense            
        # # If message took longer than _MAX_CLOCK_SKEW seconds to arrive
        # if current_time + self._MAX_CLOCK_SKEW < timestamp:
        #     raise InvalidToken

        # SHA-256 is a cryptographic hash function from the SHA-2 family  
        # and is standardized by NIST. It produces a 256-bit message 
        # digest.
        crypto_hash = hashes.SHA256()

        # Hashed-based message authentication (HMAC)
        # Tool to calculate message authentication codes using 
        # cryptographic hash function coupled with a secret key.
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
        
        return ciphertext, iv
        
    def _get_unverified_token_data(self, token):
        '''
        This breaks up the ciphertext into timestamp and "other" data for
        validating against ttl

        Parameters
        ----------
        token : byte-string
            This it the raw ciphertext data

        Raises
        ------
        InvalidToken
            If not properly formatted

        Returns
        -------
        timestamp : byte-string
            Time that the message was encrypted.
        data : byte-string
            The initialization_vector, ciphertext, and signature key (in order) 

        '''
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

    '''
    Toy Example
    '''    
    msg = b'My wife is amazing!!!'

    cipher = AESCipher()
    
    key = cipher.generate_key()
    # key = 'c47b0294dbbbee0fec4757f22ffeee3587ca4730c3d33b691df38bab076bc558'
    # key = bytes.fromhex(key)
    signing_key = cipher.generate_key()
    ciphertext, iv = cipher.encrypt(msg, key, signing_key)
    msg_tx = cipher.encode_authentication(ciphertext, iv)
    
    ciphertext, iv = cipher.authenticate(msg_tx, signing_key)
    deciphertext = cipher.decrypt(ciphertext, key, iv)
    
    if deciphertext != msg:
        raise ValueError
    
  