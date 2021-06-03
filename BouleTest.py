from Boule import Boule
from Pot import Pot

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

    Tx = pots[1].modifyTx("""
def newCostFunction (transaction):
    (msg, signature) = transaction
    op, sender, time, *rest = msg
    return 0 if op == RESPOP else 0.1

self.costFn = newCostFunction
""")
    boule.processTx(Tx)
    # convert(boule)
    print (str(boule) + "\n")
    
    Tx = pots[0].respondTx(11, "Y")
    boule.processTx(Tx)
    Tx = pots[1].respondTx(11, "Y")
    boule.processTx(Tx)
    Tx = pots[2].respondTx(11, "Y")
    boule.processTx(Tx)
    Tx = pots[3].respondTx(11, "Y")
    boule.processTx(Tx)
    print (str(boule) + "\n")

    Tx = pots[3].sendTx(pots[0].get_public_key(), 0.2)
    boule.processTx(Tx)
    print (str(boule) + "\n")

test()