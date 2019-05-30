
from ecdsa import SigningKey
import os
import json
# Blockchain library function

class Block():

    def __init__(self, number, typ, inp, output, signature):
        self.number = number
        self.typ = typ
        self.input = inp
        self.output = output
        self.signature = signature

    def serialize():
        pass

    def verify_signature():
        pass

    def verify_output():
        pass

    def verify():
        verify_signature()
        verify_output()


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
        

