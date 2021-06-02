from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
from Crypto.Cipher import AES
import time

class Pot ():
    def __init__ (self):
        self.key = ECC.generate(curve='p256')
        self.signer = DSS.new(self.key,'fips-186-3')

    def __str__(self) -> str:
        return str(self.key)

    def sign (self, msg):
        h = SHA256.new(msg)
        return self.signer.sign(h)

    def signedMsg (self, msg):
        return (msg, self.sign(str(msg).encode('utf8')))

    def get_public_key (self):
        return self.key.public_key().export_key(format='PEM')

    def import_public_key (exported_key):
        return ECC.import_key(exported_key)

    def verify_signature (pub: ECC.EccKey, msg, signature):
        h = SHA256.new(msg)
        verifier = DSS.new(pub, 'fips-186-3')
        try:
            verifier.verify(h, signature)
            return True
        except ValueError:
            return False

    def sendTx (self, receiever, amount):
        msg = ("send", self.get_public_key(), time.gmtime(), receiever, amount)
        # print(msg)
        return self.signedMsg(msg)

    def grantTx (self, newVoters):
        msg = ("grant", self.get_public_key(), time.gmtime(), newVoters)
        return self.signedMsg(msg)

    # Y:yes N:no A:abstain
    def respondTx (self, index, response):
        msg = ("respond", self.get_public_key(), time.gmtime(), response, index)
        return self.signedMsg(msg)

    #modify op, self writing
    #revoke op, remove voters

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