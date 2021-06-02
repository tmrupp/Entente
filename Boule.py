from Crypto import Signature
from BlockChain import *
from Pot import Pot
import time

# starter, no anon
# fixed cost of 1, eventually logistic curve

RESPOP = "respond"
GRNTOP = "grant"
SNDOP = "send"
CALLOP = "call"
MODOP = "modify"

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

def costFunction (transaction):
    (msg, signature) = transaction
    op, sender, time, *rest = msg
    return 0 if op == RESPOP else 1

"""
    def verifyOp (self, Tx):
        ???

    def op (self, Tx):
        ???

    def passOp (self, Tx):
        ???
"""

class Boule:
    def __init__ (self, initialTx) -> None:
        self.costFn = costFunction
        self.ledger = BlockChain()
        self.citizens = []
        self.pots = {}

        self.calls = {} # dict -> index : (dict -> citizen : response)
        self.callIsPassed = {} # dict -> index : bool (is passed or rejected, None if unresolved)

        self.processTx(initialTx)

    def getBlock (self, index):
        return self.ledger.chain[index]

    def verifySend (self, Tx):
        (msg, signature) = Tx
        op, sender, time, reciever, amount = msg

        if self.pots[sender] < (self.costFn(Tx) + amount):
            print("sender:", sender, "has", self.pots[sender], "does not have enough Ostraka for the transation:", (self.costFn(Tx) + amount))
            return False

        return True

    def send (self, Tx):
        self.logCall(Tx)

    def passSend (self, Tx):
        (msg, signature) = Tx
        op, sender, time, reciever, amount = msg

        self.pots[sender] -= amount
        self.pots[reciever] += amount


    def verifyRespond (self, Tx):
        (msg, signature) = Tx
        op, sender, time, resp, index = msg

        if sender not in self.citizens:
            print("not a valid citizen:", sender)
            return False

        # out of bounds
        if index >= len(self.ledger.chain) or index < 0:
            return False

        # not a valid citizen
        if sender not in self.calls[index]:
            print("not a valid responder to this call, citizen:", sender)
            return False

        # already responded to this call
        if self.calls[index][sender] != None:
            print("already responded, citizen:", sender)
            return False

        target = self.getBlock(index)
        (targetMsg, _) = target.tx
        checkOp, *_ = targetMsg

        if (checkOp == RESPOP):
            print("cannot respond to a response")
            return False

        return True

    def verifyGrant (self, Tx):
        return True

    verifyOperations = {
        RESPOP : verifyRespond,
        GRNTOP : verifyGrant,
        SNDOP : verifySend
    }

    def passGrant (self, Tx):
        (msg, signature) = Tx
        op, sender, time, newVoters = msg
        self.citizens.extend(newVoters)

        for x in newVoters:
            self.pots[x] = 1.0

    passOperations = {
        GRNTOP : passGrant,
        SNDOP : passSend
    }

    def respond (self, Tx):
        (msg, signature) = Tx
        op, sender, time, resp, index = msg

        self.calls[index][sender] = resp
        self.pots[sender] += 1.0

        # actually can do something
        if self.callIsPassed[index] == None:
            if resp == "N":
                self.callIsPassed[index] = False # unanimous
            elif len([x for x in self.calls[index].values() if x is None or x == "N"]) == 0:
                self.callIsPassed[index] = True
                
                target = self.getBlock(index)
                (targetMsg, _) = target.tx
                passOp, *_ = targetMsg
                self.passOperations[passOp](self, target.tx)

    def logCall (self, Tx):
        index = len(self.ledger.chain)
        self.calls[index] = {}
        self.callIsPassed[index] = None
        for x in self.citizens:
            self.calls[index][x] = None

        # do the op if there is nobody
        if len(self.citizens) == 0:
            (msg, signature) = Tx
            op, *rest = msg
            self.callIsPassed[index] = True
            self.passOperations[op](self, Tx)

    def grant (self, Tx):
        self.logCall(Tx)

    operations = {
        RESPOP : respond,
        GRNTOP : grant,
        SNDOP : send
    }

    def verifyTxCost (self, sender, Tx):
        if len(self.pots) == 0:
            return True

        return self.pots[sender] >= self.costFn(Tx)

    def doCost (self, Tx):
        (msg, signature) = Tx
        op, sender, time, *rest = msg
        if sender in self.pots:
            self.pots[sender] -= self.costFn(Tx)

    def doOp (self, Tx):
        (msg, signature) = Tx
        op, sender, time, *rest = msg
        self.doCost(Tx)
        self.operations[op](self, Tx)

    def verifyOp (self, Tx):
        (msg, signature) = Tx
        op, sender, time, *rest = msg
        return self.verifyOperations[op](self, Tx)

    def processTx (self, Tx):
        if (self.verifyTx(Tx)):
            self.doOp(Tx)
            self.ledger.addBlock(Block(Tx))
            return True
        else:
            print ("rejected Tx")
            return False

    def verifyTx (self, Tx):
        if not verifyTxSignature(Tx):
            return False
        
        if not verifyTxTime(Tx, self.ledger):
            return False

        (msg, signature) = Tx
        op, sender, time, *rest = msg

        if not self.verifyTxCost(sender, Tx):
            return False

        if not self.verifyOp(Tx):
            return False

        return True

    def potsStr (self):
        s = "pots: \n{\n"
        for pot in self.pots.items():
            s = s + "\t" + str(pot) + "\n"
        return s + "}"

    def isPassedStr (self, index):
        if self.callIsPassed[index] == True:
            return "Passed"
        elif self.callIsPassed[index] == False:
            return "Failed"
        else:
            return "Unresolved"

    def callsStr (self):
        s = "calls: \n{\n"
        for call in self.calls.items():
            (index, _) = call
            s = s + "\t" + str(call) + " " + self.isPassedStr(index) + "\n"
        return s + "}"


    def __str__(self) -> str:
        return self.potsStr() + "\n" + self.callsStr()

class BouleOld:
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

    print("hi, pots=", pots)

    boule = Boule(pots[0].grantTx([pots[0].get_public_key()]))
    print (str(boule) + "\n")

    Tx = pots[0].grantTx([pots[1].get_public_key()])
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[0].respondTx(1, "Y")
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[0].grantTx([pots[2].get_public_key(), pots[3].get_public_key()])
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[0].respondTx(3, "Y")
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[1].respondTx(3, "Y")
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[1].sendTx(pots[0].get_public_key(), 0.6)
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[0].respondTx(6, "Y")
    boule.processTx(Tx)
    Tx = pots[1].respondTx(6, "Y")
    boule.processTx(Tx)
    Tx = pots[2].respondTx(6, "Y")
    boule.processTx(Tx)
    Tx = pots[3].respondTx(6, "Y")
    boule.processTx(Tx)
    print (str(boule) + "\n")

test()