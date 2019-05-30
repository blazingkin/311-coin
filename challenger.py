#!/usr/bin/env python
import blockchain


wallet = blockchain.Wallet()

print(wallet.sign_challenge(blockchain.deserialize_to_challenge(open("challenge.json").read())))