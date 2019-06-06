#!/usr/bin/env python
import blockchain
import random


class Challenger:

    def __init__(self, wallet):
        self.wallet = wallet

    def generate_random_challenge(self):
        if random.random() < 0.1:
            return blockchain.Challenge(op="x")
        elif random.random() < 0.1:
            return blockchain.Challenge(op="constant", params=[random.randint(0, 1000)])
        else:
            ops = ["+", "*", "**", ">>" , "<<", "%", "^"]
            return blockchain.Challenge(op=ops[random.randrange(0, len(ops))], params=[self.generate_random_challenge(), self.generate_random_challenge()])


wallet = blockchain.Wallet(private_key_file="base_pkey.pem")

print(wallet.sign_challenge(blockchain.deserialize_to_challenge(open("challenge.json").read())))