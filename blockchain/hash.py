#!/usr/bin/env python3
from hashlib import blake2b
import json
from hmac import compare_digest
import cryptocode

print("---")
chain = []
transaction = [] 
        
SECRET_KEY = "lifeisachessgame,youdontwanttowasteamove"
AUTH_SIZE = 32

def sign(cookie):
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY.encode())
    h.update(cookie)
    return h.hexdigest()

def verify(cookie, sig):
    good_sig = sign(cookie)
    return compare_digest(good_sig, sig)

cookie = json.dumps(transaction).encode()
sig = sign(cookie)

if verify(json.dumps(transaction).encode(), sig):
    block = {
            "hash": 123,
            "transactions_blake2b": sig
        }
    chain.append(block)
    print(f"chain: {block}")

#0c58831b58ddba74a348023490236d37aa533418bf680522c7606e02f3115d7f
print(f"decode: {cookie.decode()}")
print(verify(cookie, "6edecf1ec96de4d8f1fd903c762ae10e681e469d5cf1aa5e61309a8dcf2a0875"))
print(verify(json.dumps(transaction).encode(), sig))
print(verify(b'user-alice', sig))

print(json.dumps(transaction).encode())
#print(dir(blake2b))

encoded = cryptocode.encrypt("mystring","mypassword")
## And then to decode it:
decoded = cryptocode.decrypt("Tlji0aqkKW0mQzSnkV5wXcdVDn4qmwR6sYjSgx69NNFELJnpCezIvsu6gWPciquIXtFRdc2fDbazpOsPAzfNe9PXMCyUQg49D+YN/4QsMEcx9bl1B1y4YVj7rkAYMwln3boY2YApoIddIpI5IgsLUdWjKhPudBJ79VL1/OuFL4kNM+tdFd/2J+HFdXqvXzcFRRfy++UZ4LkwKg5Y3bcO0kLZKj7uMXC6ngX7KAqD+iNy2TWIKAF7R91OigAEc8yvkML5hFSFSvEtcC16bCuxK1hnvjmnbjpwO9Lh4sIBYe2TeNwkpkRvWBPBXfVtDEK/DubLb3Zc8cBOt5xNfEBVS2ykZdY0ZoermSiBSZ389+/cKdvyGt0Poyn2pYP/Rb1E4Z6HGpkdNorWu9jNUHTeSJFltCvBOd7VLmyVxCUwBJW45D1yrz5CMnFlC9i9ZXV5Ih9Km3OkKnmrDjPO0XzUW+AIrqCifuQpXNpifn9A5WF7jzU25V0o5PT6qgPct5idwNG8sPPULsaGQvWMryilYv08Hb+FT286/cqnKVfnVXz3snxu9rhJg2e/uX0YANa0FAOOTTQo01/WUKl31nfwgKTktzkBbSteL+sCM+oL6Ko9xuEI4XsI9L1JcFWGA4p0jn4jTiaefTfWKwDefIefj+2l7aggMLmHkw15HyjWbSgktSt1l/362GHjE0fzWJ7jVmWdZSTrB9YvNQBvuOm6d+M1Ryv3DcRI/JGlAGWbbAG0qjyEhxPp9ehGpUvRGhWKtn+EwwhiepNXw1jnqDs702EWvjJBFO9v3UL+OZkoz6n5DJrNwN3PD0PBXYrV9nr/qkVwoMRAK7KS2/ZpgLdFORKen+/mrFePVblu/VoGmBOp6nPUzcd0RjqpiYS4A818mrzbp1CExDsAlcT0eKn3q5F+UDJP0fuOUVOL0h46kd2eB/ylFw0n0UJnvTTQstcUFYYt/Zv++i0/c2pfDLFROFuw87cJGZdVIJ3K7toJWGfH1IUcgnSLCTt0jNEFAYGrRpwaX5dasNhLKFkC5eMapoNNsR4AWpyvGNaSNwBM2AeIQf9fEDOVpBl4EVnboWqWOk226GuGqC6tfAq6Vntfsm1uVkzgRGjR5m3AwOjpbkQS9P8aRQo49BfAu9I9afWdkk93QIWPPEP6o0Ty9lBLY2xxJKgLRxm6m0hYLtzE90qjh+ehc1yhWbJCsXf0lcgFh86zuvkKiRGplPKp5PaSF+8hn+0/lKajrmfd4mJIHB7A85aR79rPi6Ur1hkgWTLVQwRQRD/iVO4qsYc0XW6gDeDVs8Q1vJzYdZFF5o9w6bJBfpSphqi60flOBC2OWZbxf5xYeKtuXek4dwsoTxBxQMlQy6XvE/mFzxvJ72ZfQg6yPSXO08KruEh7goAIcFN1NtcnkGkInPi7HV2PfQRebWS9ijVcKMoRWpVwkhTSzqMBsugAVkYLwZ6hZIA/32BIxaLsKzn9yW8nxNccuRLBsq0wbjVFb4c5Fq6S9YfmZRMGzVdjD9BY1YhvDNSBWEjqliF318PaZM6VtrkULoq1E75naSeqKdYqqqgn/rNFOw5roMQy/v0bY9zZLqYmsyHXlUxif8ae+iCMp9Cy6ub/K9+d411Ky5AFgAnh48wvUB28/YyC30cg8E8GukYiquQnGYC6mvn62FrS5ctgnXVrGqIv444SoPH/iIvn0bNkUJ0gYRLn9E1+uazGHND74d3euwLGVEoX8dMHGT0IhjXGZYEYdlmIzEWsyUeEQYvyco7jW9WT30/vHukByQrcsW5Hxz6Qk9AMnbPEZ14HT/0Zti+6NYZRCvtfXywrqCLRRX3EGJGaImyHLQssCbg4el0xLzzYbq675ViqmGVoUQwiw71EsXU5bn3OueRxz+W4LZztwL26cF1EvGxsfKlqlf9VAZ+8iHr45Oabw7EJitS+PneUnwPcBFUCqG1UbPOZUbXJgEpIVdSjUD4chOJMn7SO/YmlGy7qW5HtgGZXV0l51+A1ArZzSMaX9N48QTTFwRo6fzAZwiPWwoXmSeXNoUuHOmXiNt7IDHpFeehs4GmndaV5KR9NvhubzM97XF/tkFw+BGIlajgXsQ0SPw6e4xvUQeo2D15y1pWiEYiyZ3Bd98GtfPvf41pIHZG8EcG0pqKAWzpJhQmul8k5K7QXpFmkNnLnBw2nDZPeR88cr44OuaxNaRLw9jms6/aYtcX8Js/ZqUyFdoslnDzFqyd6LoBK2Q==*5fUa91DwZdlx0xcOmqrEZw==*/5DjPbNS3aQMgmjA+nSXew==*RSOXfxN3Uv7ewlOsEPc7BA==", SECRET_KEY)
print(decoded)

print(dir(cryptocode.myfunctions))


