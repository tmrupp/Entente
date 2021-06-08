from Crypto.Hash import SHA256

class Block:
    def __init__ (self, tx=""):
        self.prevHash = bytes()
        self.tx = tx # signature in msg
        self.index = 0

    def getHash (self):
        info = (self.prevHash, str(self.tx).encode('utf8'), self.index)
        return SHA256.new(str(info).encode('utf8'))

    def __str__ (self):
        return str((self.index, self.tx, self.prevHash))

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
        self.chain.append(newBlock)

    def getTopTime (self):
        return self.getTopBlock().tx[0][2]

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