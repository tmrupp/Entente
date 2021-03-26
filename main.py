import rsa
import hashlib
import time
import os
from Crypto.Cipher import AES

# names: entente, consensum, ostraka, conchord

# call wallets pots?
#   (op, sender, time, ...)
# COMMANDS
# actions/proposals/calls/resolutions (has a cost)
# responses/votes (free, validates and gives voter reward) Everything else burns?
# add voters 
#   (..., new original voters, encrypted anonymized list of public-private pairs)
#   (must re-anonymize all voters) via an new encrypted public-private pair, possible ways:
#       1. blockchain itself reissues a list of encrypted pairs (this could be cracked?)
#       2. anonymization acts as a response (how to submit new list of valid voters?) 
# remove voters (remove by original key)
#   remove single address requires unanimity besides removee
#   remove group (presumably stale, lost, or compromised wallets/pots) requies no response from removees
# message? (just a call with no effect?)
# send (sends some token from a wallet to another wallet (pot??)) (acts like a call, i.e. has a cost)
#   (..., reciever, amount)
# dispute (dispute a vote, only happens when anonymous pub-priv keys are stolen by vote adder or by side channel)
#   respond - prove that you have the original pub-priv key pair for a response
#   add - prove that your pub key in the anon list doesn't correspond to a valid key pair
# found? (creates a new forum/boule)

# SETTINGS
# quorum (how many valid voters must vote)
# timeout (how long can you vote on a thing)
# consensus (what percentage of votes must be affirmative to pass)
# cost? how expensive is it to propose/call

# initial assumptions:
# in order for a call to resolve all voters must respond
# for a call to pass there must be unanimity 
# response votes are anon

# TODO: make the map op -> func to take a block not a block.msg

# takes a message and returns an encrypted key and message encrypted by that key
def AESEncryptWithRSAKey (msg, pub):
    key = os.urandom(16) # generate a random key... hopefully is secure
    cipher = AES.new(key, AES.MODE_EAX)
    ciphertext, tag = cipher.encrypt_and_digest(msg)
    encryptedKey = rsa.encrypt(key, pub)
    return (encryptedKey, (ciphertext, cipher.nonce, tag))

# decrypts a message based on a private key
def AESDecryptWithRSAKey (msg, priv):
    (encryptedKey, (ciphertext, nonce, tag)) = msg
    key = rsa.decrypt(encryptedKey, priv)
    cipher = AES.new(key, AES.MODE_EAX, nonce=nonce)
    plaintext = cipher.decrypt(ciphertext)
    try:
        cipher.verify(tag)
    except ValueError:
        print("Key incorrect or message corrupted")
    return plaintext

# encrypts a new anon rsa key pair
def encryptAnonPair (newpub, newpriv, pub):
    encryptedPriv = AESEncryptWithRSAKey(newpriv.save_pkcs1(), pub)
    encryptedPub = AESEncryptWithRSAKey(newpub.save_pkcs1(), pub)
    return (encryptedPub, encryptedPriv)

# decrypts an anon rsa key pair
def decryptAnonPair (pair, priv):
    (encryptedPub, encryptedPriv) = pair
    newpub = rsa.PublicKey.load_pkcs1(AESDecryptWithRSAKey(encryptedPub, priv))
    newpriv = rsa.PrivateKey.load_pkcs1(AESDecryptWithRSAKey(encryptedPriv, priv))
    return (newpub, newpriv)

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    
def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

def hashThenSignMessage (msg, privateKey):
    h = rsa.compute_hash(msg, 'SHA-256')
    return rsa.sign_hash(h, privateKey, 'SHA-256')

def verifySignature (msg, signature, publicKey):
    return rsa.verify(msg, signature, publicKey)

def verifyTxSignature (transaction):
    (msg, signature) = transaction
    op, pub, *rest = msg
    try:
        verifySignature(str(msg).encode('utf8'), signature, pub)
    except:
        return False
    return True

def verifyTxTime (transaction, chain):
    (msg, signature) = transaction
    op, sender, time, *rest = msg
    if (len(chain) != 0 and chain.getTopTime() > time):
        return False
    return True

class PublicWallet:
    def __init__ (self, publicKey):
        self.pubkey = publicKey
        self.value = 0

class Wallet:
    def __init__ (self):
        (pub, self.privkey) = rsa.newkeys(512)
        self.pwallet = PublicWallet(pub)

    def signedMsg (self, msg):
        return (msg, hashThenSignMessage(str(msg).encode('utf8'), self.privkey))

    def sendTx (self, receiever, amount):
        msg = ("send", self.pwallet.pubkey, time.gmtime(), receiever, amount)
        # print(msg)
        return self.signedMsg(msg)

    def addTx (self, newVoters, boule):
        allVoters = newVoters

        if (boule is not None):
            allVoters = boule.originalVoters.extend(newVoters)

        newAnonymousVoters = []
        anonymousConversions = {}
        for v in allVoters:
            (newpub, newpriv) = rsa.newkeys(512)
            newAnonymousVoters.append(newpub)
            encryptedKeys = encryptAnonPair(newpub, newpriv, v)
            anonymousConversions[v] = encryptedKeys
        
        msg = ("add", self.pwallet.pubkey, time.gmtime(), newVoters, newAnonymousVoters, anonymousConversions)
        return self.signedMsg(msg)

    # Y:yes N:no A:abstain
    def respondTx (self, index, response):
        msg = ("respond", self.getPublicKey(), time.gmtime(), response, index)
        return self.signedMsg(msg)

    # def getUnrespondedCalls (self, boule):

    def getAnonKeys (self, boule):
        # go through boule and find most recently passed add op
        return 0


    def makeBlock (self, msg):
        return Block(msg)

    def getPublicKey (self):
        return self.pwallet.pubkey

class Block:
    def __init__ (self, msg="let's fucking go"):
        self.prevHash = bytes()
        self.msg = msg # signature in msg
        self.index = 0

    def getHash (self):
        info = (self.prevHash, str(self.msg).encode('utf8'), self.index)
        return rsa.compute_hash(str(info).encode('utf8'), 'SHA-256')

    def __str__ (self):
        return str((self.index, self.msg, self.prevHash))

class BlockChain:
    def __init__ (self):
        self.chain = []

    def __len__ (self):
        return len(self.chain)
    
    def addBlock (self, newBlock):
        if (len(self.chain) > 0):
            newBlock.prevHash = self.getTopBlock().getHash()
        else:
            newBlock.prevHash = bytes([0x0])
        newBlock.index = len(self)
        # if (verifyTx(newBlock.msg)):
        self.chain.append(newBlock)

    def getTopTime (self):
        return self.getTopBlock().msg[0][2]

    def getTopBlock (self):
        return self.chain[len(self)-1]

    def __str__ (self):
        s = ""
        for block in self.chain:
            s += str(block) + "\n"
        return s

# blocks have form:
# (index, Tx, prevHash)
#   Tx:
#       (msg, signature)
#           msg:
#               (op, sender, time, ...)

class Boule:
    def __init__ (self, initialTx):
        self.restart()
        self.cost = 1
        # nicknames?
        self.addAndProcessTx(initialTx)

    def restart (self):
        self.wallets = {} 
        self.chain = BlockChain()
        self.originalVoters = []
        self.anonymousVoters = []

    def sendToWallet (self, receiver, amount):
        if receiver in self.wallets.keys():
            self.wallets[receiver] += amount
        else:
            self.wallets[receiver] = amount

    def verifySend (self, msg):
        (op, sender, time, receiver, amount) = msg

        if (sender not in self.wallets.keys()):
            return False

        if (self.wallets[sender] < amount):
            return False

        return True

    def send (self, block):
        msg = block.msg[0]
        (op, sender, time, receiever, amount) = msg
        self.wallets[sender] -= amount
        self.sendToWallet(receiever, amount)

    # would be veryified by consensus, time, and 
    def verifyAddVoters (self, msg):
        op, sender, *rest = msg
        return True
        
    # for now this always passes
    def addVoters (self, block):
        if (self.callIsPassed(block.index)):
            msg = block.msg[0]
            (op, sender, time, newVoters, newAnonymousVoters, anonymousConversions) = msg
            self.originalVoters.append(newVoters)
            self.anonymousVoters = newAnonymousVoters
            for v in newVoters:
                self.sendToWallet(v, 1.0)

    # make sure you haven't already responded to this
    # make sure you're a valid responder (anon or no)
    def verifyRespond (self, msg):
        (op, sender, time, response, index) = msg
        for i in range(index, len(self.chain.chain)):
            block = self.chain.chain[i]
            (msg, signature) = block.msg
            checkIndex = block.index
            checkOp, checkSender, *rest = msg
            if (checkOp == "respond"):
                if (sender == checkSender and index == checkIndex):
                    return False
        
        if (sender not in self.getLastPassedAnonList(self.chain.getTopBlock().index)):
            return False

        return True

    def respond (self, block):
        # do nothing, besides depositing reward
        # magic happens in "post"
        msg = block.msg[0]
        op, sender, *rest = msg
        self.sendToWallet(sender, 1.0)

        
    verifyOperations = {
        "send": verifySend,
        "add": verifyAddVoters,
        "respond": verifyRespond
    }

    operations = {
        "send": send,
        "add": addVoters,
        "respond": respond
    }

    def validateTx (self, transaction):
        # verify signature
        if (not verifyTxSignature(transaction)):
            return False

        if (not verifyTxTime(transaction, self.chain)):
            return False
        
        (msg, signature) = transaction
        op, pub, *rest = msg
        return self.verifyOperations[op](self, msg)

    # recieve a transaction, add to blockchain
    def addTx (self, transaction):
        if (self.validateTx(transaction)):
            self.chain.addBlock(Block(transaction))
            return True
        else:
            return False

    def addAndProcessTx (self, transaction):
        if (self.addTx(transaction)):
            self.processBlock(self.chain.getTopBlock())

    def processBlock (self, block):
        op, pub, *rest = block.msg[0]
        # print ("in process block msg=", block.msg)
        self.operations[op](self, block)

    def processBlockChain (self):
        self.restart()
        for block in self.chain.chain:
            self.processBlock(block)

    def showAmounts (self):
        for w in self.wallets.items():
            print (w)

    # gets the most recently passed re-anonimization
    # don't check past this to see if passed later...
    def getLastPassedAnonList (self, index):
        for i in range(index-1, 0):
            block = self.chain.chain[i]
            msg = block.msg[0]
            op, *rest = msg
            if (op == "add" and self.callIsPassed(i, index)):
                (op, sender, time, newVoters, newAnonymousVoters, anonymousConversions) = msg
                return newAnonymousVoters
        return []

    def callIsPassed (self, index, indexLimit=-1):
        if (index <= 0):
            return True

        if (indexLimit == -1):
            indexLimit = len(self.chain.chain)

        anonVoters = self.getLastPassedAnonList(index)

        # go through the chain and look at all responses to this call
        for i in range(index, indexLimit):
            
            # empty means passed by default, but look through all voters
            # account for disputes later...
            if (not anonVoters):
                return True

            block = self.chain.chain[i]
            msg = block.msg[0]
            op, *rest = msg
            # is a response
            if (op == "respond"):
                op, voter, time, response, checkIndex = msg
                # is a response to this call
                if (checkIndex == index):
                    # responder voted yes
                    if (response != "N"):
                        anonVoters.remove(voter)
                    else:
                        # not unanimously agreed upon!
                        return False
        
        # not everyone has responded yet
        return False

wallets = [Wallet(), Wallet(), Wallet()]
myWallet = Wallet()

Tx = myWallet.addTx([myWallet.getPublicKey(), wallets[0].getPublicKey()], None)
boule = Boule(Tx)

boule.addAndProcessTx(myWallet.sendTx(wallets[0].getPublicKey(), 0.3))
boule.addAndProcessTx(wallets[0].sendTx(wallets[1].getPublicKey(), 0.1))
boule.addAndProcessTx(myWallet.respondTx(0, 'Y'))

boule.showAmounts()
print("***boule***\n\n", boule.chain)


# print (Tx)
