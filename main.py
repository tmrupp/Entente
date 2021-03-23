import rsa
import hashlib
import time

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

def verifyMessageHash (msg, msgHash, publicKey):
    return getSHA256Hash(msg) == rsa.decrypt(msgHash, publicKey)

class publicWallet:
    def __init__ (self, publicKey):
        self.pubkey = publicKey
        self.value = 0

class wallet:
    def __init__ (self):
        (self.pub, priv) = rsa.newkeys(512)
        self.privkey = priv
        self.pwallet = publicWallet(self.pub)

    def sendTx (self, receieveKey, sendAmount):
        msg = str(self.pwallet.pubkey) + " T " + str(receieveKey) + " : " + str(sendAmount) + " @ " + str(time.gmtime())
        print(msg)
        return rsa.sign(msg.encode('utf8'), self.privkey, 'SHA-512')

    def verifyTx (self, Transaction):
        print(Transaction)


myWallet = wallet()
Tx = myWallet.sendTx(public, 10)
print (Tx)


