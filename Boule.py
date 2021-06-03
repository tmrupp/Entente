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

        # self.modifications = [] # list -> executable code

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

    def verifyModify (self, Tx):
        return True

    def modify (self, Tx):
        self.logCall(Tx)

    def passModify (self, Tx):
        (msg, signature) = Tx
        op, sender, time, code = msg
        # self.modifications.append(code)
        eval(compile(code,  "", 'exec'))

    def verifyRespond (self, Tx):
        (msg, signature) = Tx
        op, sender, time, resp, index = msg

        if sender not in self.citizens:
            print("not a valid citizen:", sender)
            return False

        # out of bounds
        if index >= len(self.ledger.chain) or index < 0:
            print("out of bounds response index")
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

    def verifyGrant (self, Tx):
        return True

    def grant (self, Tx):
        self.logCall(Tx)

    def passGrant (self, Tx):
        (msg, signature) = Tx
        op, sender, time, newVoters = msg
        self.citizens.extend(newVoters)

        for x in newVoters:
            self.pots[x] = 1.0

    verifyOperations = {
        RESPOP : verifyRespond,
        GRNTOP : verifyGrant,
        SNDOP : verifySend,
        MODOP : verifyModify
    }

    operations = {
        RESPOP : respond,
        GRNTOP : grant,
        SNDOP : send,
        MODOP : modify,
    }

    # responses cannot be passed
    passOperations = {
        GRNTOP : passGrant,
        SNDOP : passSend,
        MODOP : passModify,
    }

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
        
        return index

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