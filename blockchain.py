
from ecdsa import SigningKey
from ecdsa import VerifyingKey
import os
import json
from hashlib import sha256
import random
# Blockchain library function

class BlockChain():

    # Block is a hashmap from blockhash to block
    def __init__(self, blocks):
        self.blocks = blocks

    def add_block(self, block):
        if block.verify(self):
            print("Added block {}".format(block.string_number()))
            self.blocks[block.string_number()] = block


    def is_miner_reward_spent(self, hsh):
        for h in self.blocks:
            block = self.blocks[h]
            for src in block.sources:
                if src["kind"].encode('utf-8') == u'miner':
                    print(src["block"])
                    print(hsh)
                    if src["block"] == hsh:
                        return True
        return False
    
    def serialize(self):
        result = {}
        for k in self.blocks:
            result[k] = self.blocks[k].serialize()
        return json.dumps(result)

    def is_self_reward_spent(self, hsh):
        for h in self.blocks:
            block = self.blocks[h]
            for src in block.sources:
                if src["kind"].encode('utf-8') == u'requester':
                    print(src["block"])
                    print(hsh)
                    if src["block"] == hsh:
                        return True
        return False
    

def deserialize_blockchain(stri):
    blocks = json.loads(stri)
    for b in blocks:
        blocks[b] = parse_block(blocks[b])
    return BlockChain(blocks)

class Block():

    def __init__(self, typ, inp, signatures, output=None, public_key_hash=""):
        self.typ = typ
        self.input = inp
        input_object = json.loads(inp)
        input_fields = ["problem", "initial_value", "public_keys", "sources", "to_miner", "to_self"]
        for field in input_fields:
            if not field in input_object:
                raise ValueError("Expected input to have value for {}".format(field))


        # Parse fields in the input
        self.problem = parse_challenge_object(input_object["problem"])
        self.public_keys = []
        for key in input_object["public_keys"]:
            self.public_keys.append(VerifyingKey.from_string(key.decode('hex')))
        self.to_miner = input_object["to_miner"]
        self.to_self = input_object["to_self"]
        self.signatures = signatures
        self.initial_value = input_object["initial_value"]

        self.sources = input_object["sources"]
        required_source_fields = ["kind", "block"]
        for source in self.sources:
            for field in required_source_fields:
                if not field in source:
                    raise ValueError("A source ({}) was missing the required field {}".format(source, field))

        # Parse fields in the output
        if output != None:
            if type(output) == type(""):
                output_object = json.loads(output)
            else:
                output_object = output
            output_fields = ["solution", "public_key_hash"]
            for field in output_fields:
                if not field in output_object:
                    raise ValueError("Expected output to have value for {}".format(field))
            self.solution = output_object["solution"]
            self.public_key_hash = output_object["public_key_hash"]
        else:
            self.solution = [self.initial_value]
            self.public_key_hash = public_key_hash
        self.output = self.calculate_output()


    def generate_next_term(self):
        self.solution.append(self.problem.evaluate(self.solution[-1]))
        self.output = self.calculate_output()


    def calculate_output(self):
        return {"solution": self.solution, "public_key_hash": self.public_key_hash}

    def number(self):
        to_hash = {"input": self.input, "output": self.output, "signatures": self.signatures}
        to_hash_str = json.dumps(to_hash)
        return int(sha256(to_hash_str).hexdigest(), 16)

    def string_number(self):
        to_hash = {"input": self.input, "output": self.output, "signatures": self.signatures}
        to_hash_str = json.dumps(to_hash)
        return sha256(to_hash_str).hexdigest()

    def serialize(self):
        return json.dumps({"type": self.typ, "input": self.input, "output": self.calculate_output(), "signatures": self.signatures})

    def verify_signatures(self):
        if len(self.signatures) != len(self.public_keys):
            raise ValueError("The number of signatures and public keys did not match")
        valid = True
        for sig, key in zip(self.signatures, self.public_keys):
            valid = valid and key.verify(sig.decode('hex'), json.dumps({"input": self.input, "type": self.typ}))
        return valid

    def verify_output(self):
        solution = self.output["solution"]
        if self.initial_value != solution[0]:
            return False
        if len(solution) == 1:
            return True
        for i in range(100):
            first_val = random.randrange(0, len(solution) - 1)
            print("Checked {}".format(first_val))
            if self.problem.evaluate(solution[first_val]) != solution[first_val + 1]:
                return False
        return True

    def verify_input(self, blockchain):
        if len(self.sources) != len(self.public_keys):
            return False
        for source, key in zip(self.sources, self.public_keys):
            source_hash = source["block"]
            if not source_hash in blockchain.blocks:
                print("Block does not exist")
                return False
            source_block = blockchain.blocks[source_hash]
            if source["kind"] == "miner":
                print("Checking miner")
                if blockchain.is_miner_reward_spent(source_hash):
                    print("Spent")
                    return False
                pubkeyhash = sha256(key.to_string().encode('hex')).hexdigest()
                if pubkeyhash != source_block.public_key_hash:
                    print("Invalid pubkey hash")
                    return False
            elif source["kind"] == "requester":
                if blockchain.is_self_reward_spent(source_hash):
                    return False
        return True
            

    def verify_number(self):
        return self.number() < 0x0007FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF

    def verify(self, blockchain):
        if not self.verify_signatures():
            print("Signature failed")
            return False
        if not self.verify_number():
            print("Invalid number")
            return False
        if not self.verify_input(blockchain):
            print("Invalid input")
            return False
        return self.verify_output()


def parse_block(stri):
    obj = json.loads(stri)
    core_fields = ["type", "input", "output", "signatures"]
    for f in core_fields:
        if f not in obj:
            raise ValueError("Expected block JSON to contain key {}".format(f))
    return Block(obj["type"], obj["input"], obj["signatures"], obj["output"])

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

    def get_signing_key(self, private_key_file=None):
        if private_key_file == None:
            private_key_file = "pkey.pem"
        if os.access(private_key_file, os.R_OK):
            return SigningKey.from_pem(open(private_key_file, "r").read())
        return SigningKey.generate()
        
    def sign_challenge(self, challenge):
        return self.private_key.sign(challenge.serialize()).encode('hex')

    def sign_input_and_type(self, inp, typ):
        return self.private_key.sign(json.dumps({"input": inp, "type": typ})).encode('hex')

    def __init__(self, private_key=None, private_key_file=None):
        if private_key == None:
            self.private_key = self.get_signing_key(private_key_file)
        else:
            self.private_key = private_key
        self.verifying_key = self.private_key.get_verifying_key()
        self.cache_signing_key()
        

