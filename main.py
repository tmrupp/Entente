import rsa
import hashlib
import time

# names: entente, consensum, ostraka, conchord

(public, private) = rsa.newkeys(512)

print ("pubkey=", public)
print ("privkey=", private)

message = 'hello Bob!'.encode('utf8')
bobh = rsa.compute_hash(message, 'SHA-256')
bobsignature = rsa.sign_hash(bobh, private, 'SHA-256')
print(rsa.verify(message, bobsignature, public))

print("my signature=", bobsignature)

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

def verifySignature (msg, signature, publicKey):
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
        msg = ("send", self.pwallet.pubkey, time.gmtime(), receiever, amount)
        # print(msg)
        return (msg, hashThenSignMessage(str(msg).encode('utf8'), self.privkey))

    def verifyTx (self, transaction):
        (msg, signature) = transaction
        op, pub, *rest = msg
        try:
            verifySignature(str(msg).encode('utf8'), signature, pub)
        except:
            return False
        return True

class Block:
    def __init__ (self, prevBlock, msg, signature, index):
        self.prevHash = prevBlock.getHash()
        self.msg = msg
        self.signature = signature
        self.index = index

    def getHash ():
        info = (self.prevHash, str(self.msg).encode('utf8'), self.signature, self.index)
        return rsa.compute_hash(str(info).encode('utf8'), 'SHA-256')

# class BlockChain:
        


myWallet = wallet()
Tx = myWallet.sendTx(public, 10)
print (Tx)

print (myWallet.verifyTx(Tx))


