from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Cipher import AES

class Pot ():
    def __init__ (self):
        self.key = ECC.generate(curve='p256')
        self.signer = DSS.new(self.key,'fips-186-3')

    def __str__(self) -> str:
        return str(self.key)

    def sign (self, msg):
        h = SHA256.new(msg)
        return self.signer.sign(h)

    def get_public_key (self):
        return self.key.public_key()

    def verify_signature (pub: ECC.EccKey, msg, signature):
        h = SHA256.new(msg)
        verifier = DSS.new(pub, 'fips-186-3')
        try:
            verifier.verify(h, signature)
            return True
        except ValueError:
            return False

def test ():
    myPot = Pot()
    yourPot = Pot()
    print(myPot)

    message = b'hey how\'s it going'

    mySignature = myPot.sign(message)
    print(mySignature)

    verified = Pot.verify_signature(myPot.get_public_key(), message, mySignature)
    print(verified)

# test()