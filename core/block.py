
import json
import time
from hashlib import sha256
from .merkle_tree import MerkleTree


class Block:
    def __init__(self, index, transactions, timestamp, previous_hash="", nonce=0):
          
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.hash = self.get_hash()
        self.previous_hash = previous_hash
        self.nonce = nonce
        if not isinstance(transactions, list):
            transactions = [transactions]
        if len(transactions) == 0:
            self.merkle_root = ""
        else:
            self.merkle_root = MerkleTree(transactions).root.hash
 
    def get_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True) 
        return sha256(block_string.encode()).hexdigest()
    

    def mine(self, difficulty):
        proof = '0' * difficulty
        while self.hash[:difficulty] != proof:
            self.nonce += 1
            self.timestamp = time.time()
            self.hash = self.get_hash()
