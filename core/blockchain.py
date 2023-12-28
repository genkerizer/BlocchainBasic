
import json
import time
from hashlib import sha256

from .block import Block
from .merkle_tree import MerkleTree

class Blockchain:

    difficulty = 5
 
    def __init__(self):
        self.chain = []
        self.create_first_block()
        self.unconfirmed_transactions = []
 
    def create_first_block(self):
        firtst_block = Block(0, [], time.time(), "")
        firtst_block.hash = firtst_block.get_hash()
        self.chain.append(firtst_block)
 
    @property
    def last_block(self):
        return self.chain[-1]
    

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.get_hash()
        while not computed_hash.startswith('0' * Blockchain.difficulty):
            block.nonce += 1
            computed_hash = block.get_hash()
        return computed_hash
    

    def add_block(self, block, proof):
        previous_hash = self.last_block.hash

        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False

        block.hash = proof
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.get_hash())
    

    def add_block(self, block, proof, merkle_hash):
        if self.last_block.index == 0:
            block.previous_hash = self.last_block.hash
            self.chain.append(block)
            return True
        
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False

        if not Blockchain.is_valid_proof(block, proof):
            return False
        
        if not Blockchain.is_valid_transaction(block, merkle_hash):
            return False

        block.hash = proof
        self.chain.append(block)
        return True
    
    @classmethod
    def is_valid_proof(cls, block, block_hash):
        return (block_hash.startswith('0' * Blockchain.difficulty) and
                block_hash == block.get_hash())
    
    @classmethod
    def is_valid_transaction(cls, block, merkle_hash):
        return (merkle_hash == MerkleTree(block.transactions).root.hash)
    

    def add_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)
 
    def mining_block(self):
        if not self.unconfirmed_transactions:
            return False
        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time.time(),
                          previous_hash=last_block.hash)
 
        proof = self.proof_of_work(new_block)
        self.add_block(new_block, proof, new_block.merkle_root)
        return new_block.index
    

    def update_chain(self, chain):
        self.chain = chain
    

    def check_chain_validity(cls, chain):
        """
        Là một hàm helper để check nếu toàn bộ blockchain là đúng
        """
        result = True
        previous_hash = "0"

        # Lặp lại qua tất cả các block
        for block in chain:
            block_hash = block.hash
            # xóa trường đã băm để tính toán lại giá trị băm
            # sử dụng `compute_hash` method.
            delattr(block, "hash")

            if not cls.is_valid_proof(block, block.hash) or \
                    previous_hash != block.previous_hash:
                result = False
                break

            block.hash, previous_hash = block_hash, block_hash

        return result
    

