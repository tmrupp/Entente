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


myKey = generate_key()
newKey = generate_key()
encryptedKey = encrypt(myKey.public_key.format(True), newKey.secret)
newPublicKey = newKey.public_key

@snark
def analogousKey (myPublicKey, privateInt, privateLength, encryptedNewKey, newPublicKey):
    newSecretKey = privateInt.to_bytes(2, 'big')
    statement0 = encryptedNewKey == encrypt(myPublicKey.format(True), newSecretKey)
    data = os.urandom(16)
    statement1 = data == (decrypt(newSecretKey, encrypt(newPublicKey.format(True), data)))
    return statement0 and statement1


privateInt = PrivVal(int.from_bytes(myKey.secret, "big"))
privateLength = PrivVal(len(myKey.secret))
print (analogousKey(myKey.public_key, privateInt, privateLength, encryptedKey, newKey.public_key))

