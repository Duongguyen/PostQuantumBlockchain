import hashlib
import json

from menu.models import Blockchains, Transaction
from datetime import datetime
from pqcrypto.pqcrypto.config import PUBLIC_KEY, SECRET_KEY, NONCE
from pqcrypto.pqcrypto.sign.sphincs_sha256_256f_robust import generate_keypair, sign, verify


class Block:
    def __init__(self, data):
        self.data = data
        self.prev_hash = ""
        self.hash = ""
        self.create_at = ""


def hash(block):
    data = json.dumps(block.data) + block.prev_hash + block.create_at
    data = data.encode('utf-8')
    # Thay sha256 bang mat ma luong tu
    return hashlib.sha256(data).hexdigest()


def SHA256(data):
    data = data.encode('utf-8')
    return hashlib.sha256(data).hexdigest()


# def hash(block):
#     data = json.dumps(block.data) + block.prev_hash + block.create_at
#     data = data.encode('utf-8')
#     secret_key_original = bytes.fromhex(SECRET_KEY)
#     signature_based = sign(secret_key_original, data)
#     signature_original = signature_based.hex()
#     return signature_original
#
#
# def signature(data):
#     data = data.encode('utf-8')
#     secret_key_original = bytes.fromhex(SECRET_KEY)
#     signature_based = sign(secret_key_original, data)
#     signature_original = signature_based.hex()
#     return signature_original


def check_blockchain():
    results = Blockchains.objects.all()
    if results:
        return True
    else:
        return False


def mine(transactions, timestamp: str):
        results = Blockchains.objects.all().values().last()
        block = json.dumps(transactions) + results['previous_hash'] + str(results['nonce']) + timestamp
        new_hash = SHA256(block)
        while not new_hash.startswith(NONCE):
            results['nonce'] += 1
            block = json.dumps(transactions) + new_hash + str(results['nonce']) + timestamp
            new_hash = SHA256(block)

        if results['header'] == results['nonce']:
            return True

        return False


def check_valid_mine(transactions, nonce: int):
    block = json.dumps(transactions) + str(nonce)
    new_hash = SHA256(block)
    if new_hash.startswith(str(NONCE)):
        return new_hash
    return False


class Blockchain:
    def __init__(self):
        self.chain = []

    def add_block(self, data):
        block = Block(data)
        check = check_blockchain()
        results = Blockchains.objects.all().values().last()
        print(data)
        if check:
            if data[0]["destination"] == "":
                value = results['hash_blockchain']
                block.prev_hash = value
                block.hash = data[0]["hash_mine"]
                self.chain.append(block)
            else:
                value = results['hash_blockchain']
                block.prev_hash = value
                block.hash = str(NONCE) + hash(block)
                self.chain.append(block)
        else:
            if data[0]["destination"] == "":
                block.prev_hash = ""
                block.hash = data[0]["hash_mine"]
                self.chain.append(block)
            else:
                block.hash = str(NONCE) + hash(block)
                block.prev_hash = ""
                self.chain.append(block)

    def get_blockchain(self):
        transaction = Transaction.objects.all().values().last()
        print(len(self.chain))
        for block in self.chain:
            print("Data:", transaction)
            print("Previous hash:", block.prev_hash)
            print("Hash:", block.hash)
            block_data = Blockchains(
                previous_hash=block.prev_hash,
                hash_blockchain=block.hash
            )
            print("DONE: ")
            block_data.save()

    def is_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            prev_block = self.chain[i - 1]

            if hash(current_block) != current_block.hash:
                return False

            if prev_block.hash != current_block.prev_hash:
                return False

        return True

    def get_balance(self, person):
        balance = 0
        print(self.chain)
        print(person)
        for block in self.chain:
            if type(block.data) != list:
                continue

            for transfer in block.data:
                if transfer["from"] == person:
                    balance = balance - transfer["amount"]

                if transfer["to"] == person:
                    balance = balance + transfer["amount"]
        return balance

# blockchain = Blockchain("Duong")
# print(blockchain.get_blockchain())
# blockchain.add_block([
#     {"from": "Duong", "to": "Quynh", "amount": 1000},
# ])
#
# blockchain.add_block([
#     {"from": "Vu", "to": "Duong", "amount": 50},
# ])
#
# blockchain.add_block([
#     {"from": "Duong", "to": "Yen", "amount": 50},
# ])
#
# blockchain.add_block([
#     {"from": "Yen", "to": "Duong", "amount": 50},
# ])
#
# print(blockchain.get_balance("Duong"))
# print('------------------------------------------------------')
# print(blockchain.get_balance("Yen"))
