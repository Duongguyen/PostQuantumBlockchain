import hashlib
import json

from menu.models import Blockchains, Transaction


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


def check_blockchain():
    results = Blockchains.objects.all()
    if results:
        return True
    else:
        return False


def mine(block_number, transactions, previous_hash, prefix_zeros):
    prefix_str = '0' * prefix_zeros
    block = str(block_number) + transactions + previous_hash + prefix_str
    while not hash(block).startswith(prefix_str):
        block.nonce += 1
        block.hash = hash(block)


class Blockchain:
    def __init__(self, owner):
        self.owner = owner
        self.chain = []

    def add_block(self, data):
        block = Block(data)
        # Lấy prev_hash từ giao dịch trước đó rồi cho vào block.
        # List blockchain ra rồi lấy hash gần nhất gán cho block.prev_hash
        check = check_blockchain()
        if check:
            results = Blockchains.objects.all().values().last()
            value = results['hash_blockchain']
            block.prev_hash = value
            block.hash = hash(block)

            self.chain.append(block)
        else:
            # Thay đổi đoạn này đáng lẽ ra Geneis Block thì previous hash phải là "". Và số nonce phải bằng 0
            block.hash = hash(block)
            block.prev_hash = ""
            self.chain.append(block)

    def get_blockchain(self):
        transaction = Transaction.objects.all().values().last()
        print(len(self.chain))
        for block in self.chain:
            print("Data:", transaction)
            print("Previous hash:", block.prev_hash)
            print("Hash:", block.hash)
            print("Nonce:", block.nonce)
            block_data = Blockchains(
                previous_hash=block.prev_hash,
                hash_blockchain=block.hash,
                nonce=block.nonce
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

