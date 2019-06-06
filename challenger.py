#!/usr/bin/env python
import blockchain
import random
import json


class Challenger:

    def __init__(self, wallet):
        self.wallet = wallet
        self.chain = blockchain.deserialize_blockchain(open("base_blockchain.json").read())
        self.prev_block_hash = "9d6ffb21a7e3457bdb2fb6d7e1b401b9144b8236861ca44c866c0f625fbaf5d7"
        self.current_challenge = self.generate_next_input()

    def generate_next_input(self):
        inp = {
            "problem": json.loads(self.generate_random_challenge().serialize()),
            "initial_value":  random.randint(0,1000),
            "public_keys":  [self.wallet.verifying_key.to_string().encode('hex')],
            "sources": [{"kind": "requester", "block": self.prev_block_hash}],
            "to_miner": 0,
            "to_self": 500000,
        }
        inp = json.dumps(inp)
        typ = "TRANS"
        sig = self.wallet.sign_input_and_type(inp, typ)
        return inp, typ, [sig]

    def get_current_chain(self):
        return self.chain

    def get_current_challenge(self):
        return self.current_challenge

    def present_solution(self, block):
        if block.verify(self.chain):
            print("Added block {}".format(block.string_number()))
            self.chain.add_block(block)
            self.prev_block_hash = block.string_number()
            self.current_challenge = self.generate_next_input()
            open("blockchain.json", "w").write(self.chain.serialize())
            return True
        return False





    def generate_random_challenge(self, depth=0):
        if depth > 3:
            return blockchain.Challenge(op="x")
        elif random.random() < 0.2:
            return blockchain.Challenge(op="constant", params=[random.randint(1, 1000)])
        else:
            ops = ["+", "*", "**", "%", "^"]
            return blockchain.Challenge(op=ops[random.randrange(0, len(ops))], params=[self.generate_random_challenge(depth + 1), self.generate_random_challenge(depth + 1)])



#print(wallet.sign_challenge(blockchain.deserialize_to_challenge(open("challenge.json").read())))