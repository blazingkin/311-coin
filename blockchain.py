
from ecdsa import SigningKey
import os
import json
from hashlib import sha1
# Blockchain library function

class Block():

    def __init__(self, typ, inp, output, signature):
        self.typ = typ
        self.input = inp
        self.output = output
        self.signature = signature
        self.trans_number = self.number()

    def number(self):
        to_hash = {"input": self.input, "output": self.output, "signature": self.signature}
        to_hash_str = json.dumps(to_hash)
        return sha1(to_hash_str)

    def serialize(self):
        return json.dumps({"type": self.typ, "input": self.input, "output": self.output, "signature": self.signature})

    def verify_signature(self):
        to_hash = {"input": self.input, "type": self.type}
        to_hash_str = json.dumps(to_hash)
        calc_sig = sha1(to_hash_str)

        # Constant time compare the two signatures
        # First calculate the smallest length
        smaller_length = len(calc_sig)
        if len(self.signature) < smaller_length:
            smaller_length = len(self.signature)
        # Then iterate over the whole string without short circuiting
        equal = True
        for i in range(smaller_length):
            if calc_sig[i] != self.signature[i]:
                equal = False
        return equal

    def verify_output(self):
        pass

    def verify_input(self):
        pass

    def verify(self):
        if self.trans_number > 0x00000FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF:
            return False
        if not self.verify_signature():
            return False
        self.verify_output()
        return True

def parse_block(stri):
    obj = json.loads(stri)
    core_fields = ["type", "input", "output", "signature"]
    for f in core_fields:
        if f not in obj:
            raise ValueError("Expected block JSON to contain key {}".format(f))
    return Block(obj["type"], obj["input"], obj["output"], obj["signature"])

class Challenge():

    def __init__(self, op="x", params=[]):
        self.op = op
        self.params = params

    ops_to_operators = {
        "+": lambda x,y : x + y,
        "*": lambda x,y : x * y,
        "-": lambda x,y : x - y,
        "%": lambda x,y : x % y,
        "**": lambda x,y : x ** y,
        ">>": lambda x,y : x >> y,
        "<<": lambda x,y : x << y,
        "^": lambda x,y : x ^ y,
        "|": lambda x,y : x | y,
        "&": lambda x,y : x & y,    
    }

    def __str__(self):
        return self.serialize()

    def evaluate(self, prevValue):
        if self.op == "x":
            return prevValue
        if self.op == "constant":
            return self.params[0]
        left = self.params[0].evaluate(prevValue)
        right = self.params[1].evaluate(prevValue)
        return Challenge.ops_to_operators[self.op](left, right)
        

    def serialize(self):
        if self.op == "x":
            return "{\"op\": \"x\"}"
        if self.op == "constant":
            return "{" + "\"op\": \"constant\", \"value\": {}".format(self.params[0]) + "}"
        return "{" + "\"op\": \"{}\", \"left\": {}, \"right\": {}".format(self.op, self.params[0].serialize(), self.params[1].serialize()) + "}"



def parse_challenge_object(obj):
    if not "op" in obj:
        raise ValueError("Bad JSON String")
    if obj["op"] == "x":
        return Challenge(op="x")
    elif obj["op"] == "constant":
        if not "value" in obj:
            raise ValueError("No value given for constant")
        return Challenge(op="constant", params=[obj["value"]])
    else:
        if (not "left" in obj) or (not "right" in obj):
            raise ValueError("A node was missing left or right")
        left = parse_challenge_object(obj["left"])
        right = parse_challenge_object(obj["right"])
        return Challenge(op=obj["op"], params=[left, right])


def deserialize_to_challenge(string):
    return parse_challenge_object(json.loads(string))



class Wallet():

    def cache_signing_key(self):
        open("pkey.pem", "w").write(self.private_key.to_pem())

    def get_signing_key(self):
        if os.access("pkey.pem", os.R_OK):
            return SigningKey.from_pem(open("pkey.pem", "r").read())
        return SigningKey.generate()
        
    def sign_challenge(self, challenge):
        return self.private_key.sign(challenge.serialize()).encode('hex')


    def __init__(self):
        self.private_key = self.get_signing_key()
        self.cache_signing_key()
        

