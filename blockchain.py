import hashlib
import json

from time import time
from urllib.parse import urlparse

import requests


class Blockchain(object):

    difficulty_target = "0000"

    def __init__(self):
        self.nodes = set()
        self.chain = []
        self.current_transactions = []

        genesis_hash = self.hash_block("GENESIS_BLOCK")
        self.append_block(
            genesis_hash,
            self.proof_of_work(0, genesis_hash, [])
        )

    def add_node(self, address):
        parse_url = urlparse(address)
        self.nodes.add(parse_url.netloc)

        print(parse_url.netloc)

    def chain_validation(self, chain):
        previous_block = chain[0]
        index = 1

        while (index < len(chain)):
            block = chain[index]
            hash_of_previous_block = block['hash_of_previous_block']
            transactions = block['transactions']
            nonce = block['nonce']

            if (hash_of_previous_block != self.hash_block(previous_block)):
                return False

            if not self.nonce_validation(index, hash_of_previous_block, transactions, nonce):
                return False

            previous_block = block
            index += 1

        return True

    def update_chain(self):
        neighbours = self.nodes
        new_chain = None

        maximum_length = len(self.chain)

        for node in neighbours:
            response = requests.get(f'http://{node}/blockchain')

            if (response.status_code == 200):
                length = response.json()['length']
                chain = response.json()['chain']

                if (length > maximum_length and self.chain_validation(chain) == True):
                    maximum_length = length
                    new_chain = chain

                if (new_chain):
                    self.chain = new_chain
                    return True
        return False

    def hash_block(self, block):
        encoded_block = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(encoded_block).hexdigest()

    def proof_of_work(self, index, hash_of_previous_block, transactions):
        nonce = 0

        while(self.nonce_validation(index, hash_of_previous_block, transactions, nonce) is False):
            nonce += 1

        return nonce

    def nonce_validation(self, index, hash_of_previous_block, transactions, nonce):
        content = hashlib.sha256(
            f"{index}{hash_of_previous_block}{transactions}{nonce}".encode()).hexdigest()
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

    @ property
    def last_block(self):
        return self.chain[-1]
