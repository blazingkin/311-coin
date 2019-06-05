#!/usr/bin/env python
from blockchain import Block
from blockchain import Wallet
from hashlib import sha256
import json

class Miner:

    def __init__(self, pubkeyhash):
        self.pubkeyhash = pubkeyhash

    def mine(self, inp, typ, signatures):
        block = Block(typ, inp, signatures, public_key_hash=self.pubkeyhash)
        if not block.verify_signatures():
            raise ValueError("Bad mining request. Signature was not valid")
        while not block.verify_number():
            block.generate_next_term()
        print(hex(block.number()))
        print(block.serialize())


miner_wallet = Wallet()
vk_string = miner_wallet.verifying_key.to_string().encode('hex')
vk_hash = sha256(vk_string).hexdigest()
miner = Miner(vk_hash)

inp = {
    "problem": {
        "op": "%",
        "left": {
        "op": "*",
        "left": {
            "op": "x"
        },
        "right": {
            "op": "constant",
            "value": 3
        }},
        "right": {
            "op": "constant",
            "value": 2 ** 32
        }
    },
    "initial_value":  3,
    "public_key":  [vk_string],
    "sources": "asdfasdf",
    "to_miner": 1,
    "to_self": 1,
}
inp = json.dumps(inp)
typ = "TRANS"

sig = miner_wallet.sign_input_and_type(inp, typ)


miner.mine(inp, typ, [sig])