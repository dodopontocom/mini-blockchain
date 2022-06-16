#!/usr/bin/env python3
from hashlib import blake2b
import json
from hmac import compare_digest
import cryptocode

print("---")
chain = []
transaction = [] 
        
SECRET_KEY = "lifeisachessgame,youdontwanttowasteamove".encode()
AUTH_SIZE = 32

def sign(cookie):
    h = blake2b(digest_size=AUTH_SIZE, key=SECRET_KEY)
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
decoded = cryptocode.decrypt("c8BupMPlnDcfy8OzwvH9yeoIbijaJrR0s6jTfqJ5YKnpQ7yXSCTpJamTNtM84xItGF25QNcnibTlmXqOL9m6VGa9uOFPkfy1QEn4z+6m7JgrT46y+aj6TdKs+qF299kNRZ9pj7W6bdhfmz7DPYGpe0nM1GIpxz3gyrTGUF+BVsiVmumJuE0cGqPx8P7KrJi3bW/I9aHnTJgKNxOPCAU+45ElFc+doecSWBa7sutPHe94OnMtnclik5VoliX3Q7Pq2RwG32rl/Wda3C3crYdtWLlWH21WdDlMQCBXczuAisBivHCbe0x4SVlZnBxOGr8NiG5kT9Mn5sb/OqfQ11ccK6BDlivAZOkzENbJiLwoiZPHN70DuavzD8mgojRjhCZChQg/mq46ieGFnPXxk1O//oXa65w944HX296PqFxW2aVzTBU4IOhXfm2HSJcEFQKcT6fGNjZMz2fT2CLihlf48IBhHydEwWv7ywD6OnrUo8bR6McS6rdGVRv6IhOa8q6NKdiXJK9pJrC2I4Nn6gFLFNvRtDrP1Vhd73fepLyYyXLbB7NdOZZaPRfY9ETWD0RLe5KaqV5OuQG2pjqOekMPCPA0n+DAdyH1wXyiV8u4PmZH6V2e71PdfHd2X2aML1daTpKTgzJunFWP1x54r1O0qtHfcrY9XazT2ch9HPaU3EyckvaKpWCWMI3RzDW66gxnW5FgkjTbc7oHT6QGgv6DyuGeuQ9HVKhBrpodsZT7+HctJ3yUXDXRv05YK8NQ3pY0jcfjt0RmgPWK77YafOooC7F5h3v3bVkv6VCg02FrEtqvRjFtgTZdltg1ge4QSzjqftGafyvTwGWls4gsG4oqh1ZnQCyF0WN2ApGFHcyhPWSgpKJHJ/Erv1t356YfxPWF6Vw02fVpk9B07K0A9oSuZIDhVI/hRrJUF1PFOq5+yDXIsabvI9IiWxrzwDnxCDSZOFdUUlGAK3kOs9m2MniTvobB0EQClrC7fQ5I1lGdr5wQFRL/UCtdtTfgI8+hy21laWxGjHPgKTeti6s7GkA5vi1DM724B+qz8a/gJDT7HBnRJkKywGCr1kt9P9OmUBANPOWybhrlnWtTHqm9bU/wjt6uiQiJmVnbraleZ+b7p0EiAuCo9m6e8EPe/atWgArve9rXN4C5VsYGjYaTvSYDunNWVXosYqLnYqLqqSACW0XYLjeFqAXH1EYAWQolXzRWGOQWFPwHDMKphFg0KVEfsZIAlEoqYammHzqmiAHI2VAPzGiNH6y0D6bp8BbQJFAn4hpG+XD/XJRGNLoN9bwjp2lv3aNfQTB0xinOinfx3OMOONdH*AtneBhfkREVL9IDxTmA1iA==*19Wxya1xRbDuVP21ajrY4Q==*vQrWCszFNPBWl3hDbxqd/Q==", SECRET_KEY.decode())
print(decoded)


