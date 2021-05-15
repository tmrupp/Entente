# from __future__ import print_function

import sys
import os

from pysnark.runtime import snark, PrivVal
import random
from nacl.signing import SigningKey
from pysnark.array import Array
from Crypto.Cipher import AES

from ecies.utils import generate_eth_key, generate_key
from ecies import encrypt, decrypt

p = random.randint(0,256)
s = PrivVal(random.randint(0,256))

# secp_k = generate_key()
# sk_bytes = secp_k.secret  # bytes
# pk_bytes = secp_k.public_key.format(True)  # bytes
# decrypt(sk_bytes, encrypt(pk_bytes, data))

# takes a message and returns an encrypted key and message encrypted by that key
def AESEncryptWithETHKey (msg, pub):
    key = os.urandom(16) # generate a random key... hopefully is secure
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(msg)
    encryptedKey = encrypt(pub, key)
    return (encryptedKey, (ciphertext, cipher.nonce, tag))

# decrypts a message based on a private key
def AESDecryptWithETHKey (msg, priv):
    (encryptedKey, (ciphertext, nonce, tag)) = msg
    key = decrypt(priv, encryptedKey)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
    except ValueError:
        print("Key incorrect or message corrupted")
    return plaintext

myKey = generate_key()
secret_message = b'hey how are ya'
encrypted_message = AESEncryptWithETHKey(secret_message, myKey.public_key.format(True))
decrypted_message = AESDecryptWithETHKey(encrypted_message, myKey.secret)
print (decrypted_message)

newKey = generate_key()
secretBytes = [PrivVal(x) for x in newKey.secret]
publicBytes = [PrivVal(x) for x in myKey.public_key.format(True)]
allBytes = secretBytes + publicBytes
allBytes = Array([secretBytes, publicBytes])



@snark
def analogousKey (p, pc, c, kb):
    return p > pc

print ("compare of secret", s, "< public", p, analogousKey(p, s, 0, myKey))

