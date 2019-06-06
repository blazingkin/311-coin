#!/usr/bin/env python

import threading
import time
from challenger import Challenger
from blockchain import Wallet
from blockchain import BlockChain
from blockchain import Block
from miner import Miner
from hashlib import sha256

class MinerThread(threading.Thread):
    def run(self):
        wallet = Wallet(private_key_file="pkey{}.pem".format(self.getName()))
        vk_string = wallet.verifying_key.to_string().encode('hex')
        vk_hash = sha256(vk_string).hexdigest()
        miner = Miner(vk_hash, None)
        while True:
            miner.update_blockchain(challenger.get_current_chain())
            inp, typ, sigs = challenger.get_current_challenge()
            try:
                print("Thread-{} starting to mine".format(self.getName()))
                block = miner.mine(inp, typ, sigs)
                print("Thread-{} found a solution".format(self.getName()))
                challenger.present_solution(block)
            except ValueError:
                print("error!")
                pass




if __name__ == "__main__":
    challenger_wallet = Wallet(private_key_file="base_pkey.pem")
    challenger = Challenger(challenger_wallet)
    for i in range(10):
        miner = MinerThread(name="{}".format(i))
        miner.start()