import hashlib
import json

from time import time


class Blockchain(object):

    difficulty_target = "0000"

    def __init__(self):
        self.chain = []
        self.current_transactions = []

        genesis_hash = self.hash_block("GENESIS_BLOCK")
        self.append_block(
            genesis_hash,
            self.proof_of_work(0, genesis_hash, [])
        )

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=False).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0

        while(self.nonce_validation(index, hash_of_previous_block, transactions, nonce) is False):
            nonce += 1

        return nonce

    def nonce_validation(self, index, hash_of_previous_block, transaction, nonce):
        content = f"{index}{hash_of_previous_block}{transaction}{nonce}".encode()
        content = hashlib.sha256(content).hexdigest()

        print(content)
        return content[:len(self.difficulty_target)] == self.difficulty_target

    def append_block(self, hash_of_previous_block, nonce):
        block = {
            'index': len(self.chain),
            'timestamp': time(),
            'transactions': self.current_transactions,
            'nonce': nonce,
            'hash_of_previous_block': hash_of_previous_block
        }

        self.current_transactions = []
        self.chain.append(block)

        return block

    def append_transaction(self, sender, recipient, amount):
        transaction = {
            'index': len(self.current_transactions),
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        }

        self.current_transactions.append(transaction)

        return len(self.chain) + 1

    @property
    def last_block(self):
        return self.chain[-1]
