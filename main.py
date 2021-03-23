import rsa
import hashlib
import time

# names: entente, consensum, ostraka, conchord

(public, private) = rsa.newkeys(512)

print ("pubkey=", public)
print ("privkey=", private)

message = 'hello Bob!'.encode('utf8')
crypto = rsa.encrypt(message, public)
message = rsa.decrypt(crypto, private)
print(message.decode('utf8'))

def getSHA256Hash (msg):
    m = hashlib.sha256()
    m.update(msg.encode('utf8'))
    return m.digest()

def encryptMessageHash (msg, privateKey):
    return rsa.encrypt(getSHA256Hash(msg), privateKey)

def hashThenSignMessage (msg, privateKey):
    h = rsa.compute_hash(msg, 'SHA-256')
    return rsa.sign_hash(h, privateKey, 'SHA-256')

def verifySign (msg, signature, publicKey):
    return rsa.verify(msg, signature, publicKey)

class publicWallet:
    def __init__ (self, publicKey):
        self.pubkey = publicKey
        self.value = 0

class wallet:
    def __init__ (self):
        (pub, self.privkey) = rsa.newkeys(512)
        self.pwallet = publicWallet(pub)

    def sendTx (self, receiever, amount):
        msg = ("send", self.pwallet.pubkey, receiever, amount, time.gmtime())
        # print(msg)
        return (msg, hashThenSignMessage(str(msg).encode('utf8'), self.privkey))

    def verifyTx (self, transaction):
        (msg, signature) = transaction
        op, pub, *rest = msg
        return verifySign(str(msg).encode('utf8'), signature, pub)

# class Block:
    
        


myWallet = wallet()
Tx = myWallet.sendTx(public, 10)
print (Tx)

print (myWallet.verifyTx(Tx))


