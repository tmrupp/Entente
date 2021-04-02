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
    knowledge of discrete log, using Fiat Shamir Heuristic i.e. noninteractive
    proof that given y = g^x, x is known
    '''
    x, q, p, g, y = decomposeKey(key)
    v = Crypto.Random.random.randint(0, int(q))
    t = pow(g, v, p)
    c = sha_crypto_ints([g, y, t])
    r = (v - (c * int(x))) % int(p-1)

    return (t, r)

def DLVerify (publicKey, proof):
    q, p, g, y = decomposePublicKey(publicKey)
    t, r = proof
    c = sha_crypto_ints([g, y, t])
    return t == ((pow(g, r, p) * pow (y, c, p)) % p)

myProof = FSProof(myKey)
print("verified?", FSVerify(myKey.publickey(), myProof))

