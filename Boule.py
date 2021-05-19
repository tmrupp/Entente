from BlockChain import *
from Pot import Pot
import time

# starter, no anon
# fixed cost of 1, eventually logistic curve

class Boule:
    def __init__ (self, initialTx):
        self.restart()
        self.cost = 1
        # nicknames?
        self.chain = BlockChain()
        self.addAndProcessTx(initialTx)

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

        if (self.pots[sender] < amount):
            return False

        return True

    def send (self, block):
        msg = block.tx[0]
        (op, sender, time, receiever, amount) = msg
        self.pots[sender] -= amount
        self.sendToPot(receiever, amount)

    # would be veryified by consensus, time, and 
    def verifyAddVoters (self, msg):
        op, sender, *rest = msg
        return True
        
    # passes if passes!
    def addVoters (self, block):
        if (self.callIsPassed(block.index)):
            msg = block.tx[0]
            (op, sender, time, newVoters, newAnonymousVoters, anonymousConversions) = msg
            self.originalVoters.extend(newVoters)
            self.anonymousVoters = newAnonymousVoters
            self.anonymousConversions = anonymousConversions
            for v in newVoters:
                self.sendToWallet(v, 1.0)

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
                    return False

        block = self.chain.chain[index]
        (msg, signature) = block.tx
        checkOp, *rest = msg
        if (checkOp == "respond"):
            return False
        
        if (sender not in self.getLastPassedAnonListAt(self.chain.getTopBlock().index)):
            return False

        return True

    def respond (self, block):
        # do nothing, besides depositing reward
        # magic happens in "post"
        msg = block.tx[0]
        op, sender, *rest = msg
        self.sendToWallet(sender, 1.0)
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

    def getLastPassedAnonList (self):
        return 0

    # gets the most recently passed re-anonimization
    # don't check past this to see if passed later...
    def getLastPassedAnonListAt (self, index):
        for i in range(index-1, 0):
            block = self.chain.chain[i]
            msg = block.tx[0]
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

        anonVoters = self.getLastPassedAnonListAt(index)

        # go through the chain and look at all responses to this call
        for i in range(index, indexLimit):
            
            # empty means passed by default, but look through all voters
            # account for disputes later...
            if (not anonVoters):
                return True

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
                        anonVoters.remove(voter)
                    else:
                        # not unanimously agreed upon!
                        return False
        
        # not everyone has responded yet
        return False