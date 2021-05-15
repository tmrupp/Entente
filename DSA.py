from Crypto.PublicKey import DSA
from Crypto.Signature import DSS
from Crypto.Hash import SHA256
import Crypto.Random

# p, mod boy
# q, who the fuck knows
# g, generator
# p, q, g = key.domain()

def decomposeKey (k):
    ''' x, q, p, g, y '''
    return [k._key[comp] for comp in ['x', 'q', 'p', 'g', 'y']]

def decomposePublicKey (k):
    ''' q, p, g, y '''
    return [k._key[comp] for comp in ['q', 'p', 'g', 'y']]

def int_to_bytes(x: int) -> bytes:
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')
    
def int_from_bytes(xbytes: bytes) -> int:
    return int.from_bytes(xbytes, 'big')

def ints_to_bytes (xs):
    if (len(xs) == 0):
        return bytes(0)
    
    # recursion... very haskellian
    s = str(int_to_bytes(int(xs[0])))
    s += str(ints_to_bytes(xs[1:]))
    return s.encode('utf8')

def sha_crypto_ints (xs):
    return int_from_bytes(sha(ints_to_bytes(xs)).encode('utf8'))

myKey = DSA.generate(1024)

x, q, p, g, y = decomposeKey(myKey)
pq, pp, pg, py = decomposePublicKey(myKey.publickey())

# x is secret, y is public
# g^x = y mod q
# pow(a, b, p) => (a^b) % p

def sha (a):
    h = SHA256.new()
    h.update(a)
    return h.hexdigest()

def DLProof (key):
    '''
    knowledge of discrete log, using Fiat Shamir Heuristic i.e. noninteractive\n
    proof that given y = g^x, x is known
    '''
    x, q, p, g, y = decomposeKey(key)
    v = Crypto.Random.random.randint(0, int(p))
    t = pow(g, v, p)
    c = sha_crypto_ints([g, y, t])
    r = (v - (c * int(x))) % int(p-1)
    return (t, r)

def DLVerify (publicKey, proof, cin=None):
    q, p, g, y = decomposePublicKey(publicKey)
    t, r = proof
    c = sha_crypto_ints([g, y, t]) if cin is None else cin
    return t == ((pow(g, r, p) * pow (y, c, p)) % p)

def DLEqualityProof (keyA, keyB):
    '''
    knowledge of the equality of two discrete logs\n
    log_ag(ay) == log_bg(by), ay & by are public keys, ag & bg are generators
    '''
    ax, q, p, ag, ay = decomposeKey(keyA)
    bx, _, _, bg, by = decomposeKey(keyB)
    v = Crypto.Random.random.randint(0, int(p))
    ts = (pow(ag, v, p), pow(bg, v, p))
    c = sha_crypto_ints([ag, ay, ts[0], bg, by, ts[1]])
    r = (v - (c * int(x))) % int(p-1)
    return (ts, r)

def DLEqualityVerify (publicKeyA, publicKeyB, proof):
    (ta, tb), r = proof
    q, p, ag, ay = decomposePublicKey(publicKeyA)
    _, _, bg, by = decomposePublicKey(publicKeyB)
    c = sha_crypto_ints([ag, ay, ta, bg, by, tb])
    return DLVerify(publicKeyA, (ta, r), c) and DLVerify(publicKeyB, (tb, r), c)


# TODO: could be ng=g^a, ny=y^a???
# do not reveal a...
def keyFromNewGenerator (key):
    '''
    creates a new key with a new generator, with the same private key
    '''
    x, q, p, g, y = decomposeKey(key)
    ng = 1
    while (ng == g or ng == 1):
        h = Crypto.Random.random.randint(2, int(p)-2)
        ng = pow(h, (int(p)-1)//int(q), int(p))

    ny = pow(ng, int(x), int(p))
    return DSA.construct((ny, ng, p, q, x))

def ILMPP (aKeys, bKeys):
    '''
    Iterated Logarithmic Multiplication Proof Protocol\n
    log_g(a_0)*...log_g(a_k) == log_g(b_0)*...log_g(b_k)
    '''
    _, q, p, g, _ = decomposeKey(aKeys[0])
    k = len(aKeys)
    assert(len(aKeys) == len(bKeys))
    thetas = [Crypto.Random.random.randint(0, int(p)) for x in range(k-1)]
    # print (len(thetas), " thetas=", thetas)


myProof = DLProof(myKey)
print("verified?", DLVerify(myKey.publickey(), myProof))
newKey = keyFromNewGenerator(myKey)
myEqProof = DLEqualityProof(myKey, newKey)
print("equality verified?", DLEqualityVerify(myKey.publickey(), newKey.publickey(), myEqProof))

ILMPP([newKey]*10, [newKey]*10)





