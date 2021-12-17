import sys
import requests

from flask import Flask
from flask.globals import request
from flask.json import jsonify

from uuid import uuid4

from blockchain import Blockchain

app = Flask(__name__)
blockchain = Blockchain()

node_identifier = str(uuid4()).replace('-', '')

# ROUTES


@app.route('/blockchain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/mine', methods=['GET'])
def mine_block():
    blockchain.append_transaction(
        sender="GENESIS",
        recipient=node_identifier,
        amount=1
    )

    last_block_hash = blockchain.hash_block(blockchain.last_block)
    index = len(blockchain.chain)
    nonce = blockchain.proof_of_work(
        index=index,
        hash_of_previous_block=last_block_hash,
        transactions=blockchain.current_transactions
    )

    block = blockchain.append_block(last_block_hash, nonce)
    response = {
        'message': 'New block has been mined!',
        'index': block['index'],
        'hash_of_previous_block': block['hash_of_previous_block'],
        'nonce': block['nonce'],
        'status': 200
    }

    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    required_fields = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required_fields):
        return ('Missing fields!', 400)

    index = blockchain.append_transaction(
        values['sender'],
        values['recipient'],
        values['amount']
    )

    response = {'message': f'Transaction will be added to block {index}'}
    return (response, 201)


if __name__ == '__main__':
    app.run(
        host='0.0.0.0',
        port=int(sys.argv[1])
    )
