from BlockChain import *
from Pot import Pot
import time

# starter, no anon
# fixed cost of 1, eventually logistic curve

def verifyTxSignature (transaction):
    (msg, signature) = transaction
    op, pub, *rest = msg
    try:
        Pot.verify_signature(Pot.import_public_key(pub), str(msg).encode('utf8'), signature)
    except:
        return False
    return True

def verifyTxTime (transaction, chain):
    (msg, signature) = transaction
    op, sender, time, *rest = msg
    if (len(chain) != 0 and chain.getTopTime() > time):
        return False
    return True

class Boule:
    def __init__ (self, initialTx):
        self.restart()
        self.cost = 1
        # nicknames?
        self.chain = BlockChain()
        self.addAndProcessTx(initialTx)

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
        else:
            print("transation =", str(transaction), "was rejected")

    def restart (self):
        self.pots = {} # amount of money people have, dictionary of public keys -> value
        self.responders = [] # valid responders, list of public keys

    def sendToPot (self, receiver, amount):
        if receiver in self.pots.keys():
            self.pots[receiver] += amount
        else:
            self.pots[receiver] = amount

    def verifySend (self, msg):
        (op, sender, time, receiver, amount) = msg
        if (sender not in self.pots.keys()):
            return False

        if (self.pots[sender] < amount + self.cost):
            return False

        return True

    def send (self, block):
        msg = block.tx[0]
        (op, sender, time, receiever, amount) = msg
        self.pots[sender] -= amount + self.cost
        self.sendToPot(receiever, amount)

    # would be veryified by consensus, time, and 
    def verifyAddVoters (self, msg):
        op, sender, *rest = msg
        if (len(self.pots) == 0 or (sender in self.pots and self.pots[sender] >= self.cost)):
            return True
        
        return False
        
    # passes if passes!
    def addVoters (self, block):
        if (self.callIsPassed(block.index)):
            msg = block.tx[0]
            (op, sender, time, newVoters) = msg
            print ("adding voters! " + str(newVoters))
            for v in newVoters:
                self.sendToPot(v, 1.0)
                self.responders.append(v)

    # make sure you haven't already responded to this
    # make sure you're a valid responder (anon or no)
    # cannot respond to a response
    def verifyRespond (self, msg):
        (op, sender, time, response, index) = msg
        for i in range(index, len(self.chain.chain)):
            block = self.chain.chain[i]
            (msg, signature) = block.tx
            checkIndex = block.index
            checkOp, checkSender, *rest = msg
            if (checkOp == "respond"):
                if (sender == checkSender and index == checkIndex):
                    print ("already responded at index=" + str(i))
                    return False

        if (index >= len(self.chain.chain)):
            print("index =", index, "out of range, blockchain size=", len(self.chain.chain))
            return False

        block = self.chain.chain[index]
        (msg, signature) = block.tx
        checkOp, *rest = msg

        if (checkOp == "respond"):
            print ("responding to a response")
            return False
        
        if (sender not in self.getVotersAt(self.chain.getTopBlock().index)):
            print ("sender=" + sender + " not in voter rolls=" + str(self.getVotersAt(self.chain.getTopBlock().index)))
            return False

        return True

    def respond (self, block):
        # do nothing, besides depositing reward
        # magic happens in "post"
        msg = block.tx[0]
        op, sender, *rest = msg
        self.sendToPot(sender, 1.0)
        (op, sender, time, response, index) = msg
        # try to process the call
        self.processBlock(self.chain.chain[index])
        
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
    def appendTx (self, transaction):
        if (self.validateTx(transaction)):
            self.chain.addBlock(Block(transaction))
            return True
        else:
            return False

    def appendAndProcessTx (self, transaction):
        if (self.appendTx(transaction)):
            self.processBlock(self.chain.getTopBlock())

    def processBlock (self, block):
        op, pub, *rest = block.tx[0]
        self.operations[op](self, block)

    def processBlockChain (self):
        self.restart()
        for block in self.chain.chain:
            self.processBlock(block)

    def showAmounts (self):
        for w in self.pots.items():
            print (w)

    # gets the most recently passed re-anonimization
    # don't check past this to see if passed later...
    def getVotersAt (self, index):
        voters = []

        print("checking for voters at index=", index)

        for i in range(index-1, -1):
            block = self.chain.chain[i]
            msg = block.tx[0]
            op, *rest = msg

            print ("this guy has op="+op)

            if (op == "add" and self.callIsPassed(i, index)):
                (op, sender, time, newVoters) = msg
                print("found an add op! newVoter=", newVoters)
                voters.extend(newVoters)

        return voters

    def callIsPassed (self, index, indexLimit=-1):
        if (index <= 0):
            return True

        if (indexLimit == -1):
            indexLimit = len(self.chain.chain)

        voters = self.getVotersAt(index)

        # go through the chain and look at all responses to this call
        for i in range(index, indexLimit):
            block = self.chain.chain[i]
            msg = block.tx[0]
            op, *rest = msg
            # is a response
            if (op == "respond"):
                op, voter, time, response, checkIndex = msg
                # is a response to this call
                if (checkIndex == index):
                    # responder voted yes
                    if (response != "N"):
                        voters.remove(voter)
                    else:
                        # not unanimously agreed upon!
                        return False
        
        if (len(voters) == 0):
            return True

        # not everyone has responded yet
        return False

    def __str__ (self):
        s = "Boule, responders:\n"
        for v in self.responders:
            s = s + str(v) + "\n"

        s = s + "pots:\n"
        for k, v in self.pots.items():
            s = s + str(k) + ": " + str(v) + "\n"
        return s


def test ():
    pots = []

    for i in range(6):
        pots.append(Pot())

    print("hi, pots=")

    boule = Boule(pots[0].addTx([pots[0].get_public_key()]))
    
    print (str(boule))

    Tx = pots[0].addTx([pots[1].get_public_key()])
    boule.addAndProcessTx(Tx)

    print (str(boule))

    Tx = pots[0].respondTx(1, "Y")
    boule.addAndProcessTx(Tx)

    print (str(boule))

test()