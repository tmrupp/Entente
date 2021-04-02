from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

key = DSA.generate(2048)

print(key.public_key().export_key())
print(key)

p, q, g = key.domain

print("p=", p)