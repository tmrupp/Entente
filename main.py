import rsa
import hashlib
import time

# names: entente, consensum, ostraka, conchord

# call wallets pots?
#   (op, sender, time, ...)
# COMMANDS
# actions/proposals/calls/resolutions (has a cost)
# responses/votes (free, validates and gives voter reward)
# add voters 
#   (..., new original voters, encrypted anonymized list of public-private pairs)
#   (must re-anonymize all voters) via an new encrypted public-private pair, possible ways:
#       1. blockchain itself reissues a list of encrypted pairs (this could be cracked?)
#       2. anonymization acts as a response (how to submit new list of valid voters?) 
# remove voters (this requires some shit, maybe a roll call)
# message? (just a call with no effect?)
# send (sends some token from a wallet to another wallet (pot??)) (acts like a call, i.e. has a cost)
#   (..., reciever, amount)
# dispute (dispute a vote, only happens when anonymous pub-priv keys are stolen by vote adder or by side channel)


# SETTINGS
# quorum (how many valid voters must vote)
# timeout (how long can you vote on a thing)
# consensus (what percentage of votes must be affirmative to pass)
# cost? how expensive is it to propose/call

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
    op, sender, time, *rest = msg
    if (chain.getMostRecentTime() > time):
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


            # print("len=", len(int_to_bytes(newpub.n)))
            # rsa.encrypt(int_to_bytes(newpub.e), v)
            # rsa.encrypt(int_to_bytes(newpub.n), v)\

            # AES Encrypt a key

            # encryptedKeys = (rsa.encrypt(str(newpub).encode('utf8'), v), rsa.encrypt(str(newpriv).encode('utf8'), v))
            # anonymousConversions[v.pubkey] = encryptedKeys
        
        msg = ("add", self.pwallet.pubkey, time.gmtime(), newAnonymousVoters, anonymousConversions)
        return self.signedMsg(msg)

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
    def __init__ (self, block):
        self.chain = [block]

    def __len__ (self):
        return len(self.chain)
    
    def addBlock (self, newBlock):
        newBlock.prevHash = self.chain[len(self)-1].getHash()
        newBlock.index = len(self)
        # if (verifyTx(newBlock.msg)):
        self.chain.append(newBlock)

    def getMostRecentTime (self):
        return self.chain[len(self)-1].msg[2]

    def __str__ (self):
        s = ""
        for block in self.chain:
            s += str(block) + "\n"
        return s

class Boule:
    def __init__ (self, initialTx):
        self.originalVoters = []
        self.anonymousVoters = []
        self.wallets = {}
        self.chain = BlockChain(Block(initialTx))
        self.cost = 1

    def verifySend (self, msg):
        (op, sender, time, receiever, amount) = msg
        if (self.wallets[sender].value < amount):
            return False
        return True

    def send (self, msg):
        (op, sender, time, receiever, amount) = msg
        self.wallets[sender] -= amount
        self.wallets[receiever] += amount

    def verifyAddVoters (self, msg):
        return 0
        

    def addVoters (self, msg):
        return 0

    verifyOperations = {
        "send": verifySend,
        "add": verifyAddVoters
    }

    operations = {
        "send": send,
        "add": addVoters
    }

    def validateTx (self, transaction):
        # verify signature
        if (not verifyTxSignature(transaction)):
            return False

        if (not verifyTxTime(transaction, chain)):
            return False
        
        (msg, signature) = transaction
        op, pub, *rest = msg
        return self.verifyOperations[op](self, msg)

    # recieve a transaction, add to blockchain
    def addTx (self, transaction):
        if (self.validateTx(transaction)):
            chain.addBlock(Block(transaction))

    def processBlock (self, block):
        op, pub, *rest = block.msg
        self.operations[op](self, block.msg)

    def processBlockChain (self):
        return 0

    def showAmounts ():
        for w in wallets:
            print (w)




        


    def processBlock (self, block):
        return 0


wallets = [Wallet(), Wallet(), Wallet()]
myWallet = Wallet()

Tx = myWallet.addTx([myWallet.getPublicKey()], None)
boule = Boule(Tx)

print (Tx)

# bc = BlockChain()

# bc.addBlock(myWallet.makeBlock(myWallet.sendTx(wallets[0].getPublicKey(), 10)))
# bc.addBlock(myWallet.makeBlock(myWallet.sendTx(wallets[1].getPublicKey(), 100)))
# bc.addBlock(myWallet.makeBlock(myWallet.sendTx(wallets[0].getPublicKey(), 50)))

# print("bc=", bc)
