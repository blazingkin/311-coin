#!/usr/bin/env python
from blockchain import Block
from blockchain import Wallet
from blockchain import deserialize_blockchain
from hashlib import sha256
import json

class Miner:

    def __init__(self, pubkeyhash, blockchain):
        self.pubkeyhash = pubkeyhash
        self.blockchain = blockchain

    def update_blockchain(self, blockchain):
        self.blockchain = blockchain

    def mine(self, inp, typ, signatures):
        block = Block(typ, inp, signatures, public_key_hash=self.pubkeyhash)
        if not block.verify_signatures():
            raise ValueError("Bad mining request. Signature was not valid")
        if not block.verify_input(self.blockchain):
            raise ValueError("Bad block given. The input could not be verified")
        while not block.verify_number():
            block.generate_next_term()
        return block


if __name__ == "__main__":
    miner_wallet = Wallet()
    vk_string = miner_wallet.verifying_key.to_string().encode('hex')
    vk_hash = sha256(vk_string).hexdigest()
    miner = Miner(vk_hash, blockchain)

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
        "public_keys":  [vk_string],
        "sources": [{"kind": "miner", "block": "9d6ffb21a7e3457bdb2fb6d7e1b401b9144b8236861ca44c866c0f625fbaf5d7"}],
        "to_miner": 1,
        "to_self": 1,
    }
    inp = json.dumps(inp)
    typ = "TRANS"

    sig = miner_wallet.sign_input_and_type(inp, typ)


    miner.mine(inp, typ, [sig])
