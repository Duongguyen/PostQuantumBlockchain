import hashlib
import json
from fastapi import FastAPI

from menu.models import Blockchains


class Block:
    def __init__(self, data):
        self.data = data
        self.prev_hash = ""
        self.nonce = 0
        self.hash = ""


def hash(block):
    data = json.dumps(block.data) + block.prev_hash + str(block.nonce)
    data = data.encode('utf-8')
    # Thay sha256 bang mat ma luong tu
    return hashlib.sha256(data).hexdigest()


def list_blockchain():
    results = Blockchains.objects.all()
    if results:
        value = results[-1]['hash_blockchain']
        return value


class Blockchain:
    def __init__(self, owner):
        self.owner = owner
        self.chain = []
        block = Block("Geneis Block")
        block.hash = hash(block)

        self.chain.append(block)

    def add_block(self, data):
        block = Block(data)
        # Lấy prev_hash từ giao dịch trước đó rồi cho vào block.
        # List blockchain ra rồi lấy hash gần nhất gán cho block.prev_hash
        results = Blockchains.objects.all()
        value = results[-1]['hash_blockchain']
        block.prev_hash = value
        block.hash = hash(block)
        while not hash(block).startswith("00"):
            block.nonce += 1
            block.hash = hash(block)

        self.chain.append(block)

    def get_blockchain(self):
        # Thay phần này bằng lưu data vào cơ sở dữ liệu.
        for block in self.chain:
            print("Data:", block.data)
            print("Previous hash:", block.prev_hash)
            print("Hash:", block.hash)
            print("Nonce:", block.nonce)
            print("")
            block_data = Blockchains(
                data=block.data,
                previous_hash=block.prev_hash,
                hash_blockchain=block.hash,
                nonce=block.nonce
            )
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
# print(blockchain.get_blockchain())
# print(blockchain.get_balance("Duong"))
# print('------------------------------------------------------')
# print(blockchain.get_balance("Yen"))
