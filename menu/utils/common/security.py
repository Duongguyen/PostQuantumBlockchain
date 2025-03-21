import hashlib
import json
import math

from menu.models import Blockchains, Transaction
from datetime import datetime
from pqcrypto.pqcrypto.config import PUBLIC_KEY, SECRET_KEY, NONCE, SK_1, SK_2, SK_3, SK_4
from pqcrypto.pqcrypto.sign.sphincs_sha256_256f_robust import generate_keypair, sign, verify
from menu.sphincs_python.package.sphincs import Sphincs, prf_msg, hash_msg
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

class Block:
    def __init__(self, data):
        self.data = data
        self.prev_hash = ""
        self.hash = ""
        self.create_at = ""
        self.destination = ""


def hash(block):
    data = json.dumps(block.data) + block.prev_hash + block.create_at
    data = data.encode('utf-8')
    variable_sph = Sphincs()
    bytes_sk_1 = bytes.fromhex(SK_1)
    bytes_sk_2 = bytes.fromhex(SK_2)
    bytes_sk_3 = bytes.fromhex(SK_3)
    bytes_sk_4 = bytes.fromhex(SK_4)

    opt = bytes(variable_sph._n)
    r = prf_msg(bytes_sk_2, opt, data, variable_sph._n)
    size_md = math.floor((variable_sph._k * variable_sph._a + 7) / 8)
    size_idx_tree = math.floor((variable_sph._h - variable_sph._h // variable_sph._d + 7) / 8)
    size_idx_leaf = math.floor((variable_sph._h // variable_sph._d + 7) / 8)
    digest = hash_msg(r, bytes_sk_3, bytes_sk_4, data, size_md + size_idx_tree + size_idx_leaf)
    return digest.hex()


def hash_mine(data):
    data = data.encode('utf-8')
    variable_sph = Sphincs()
    bytes_sk_1 = bytes.fromhex(SK_1)
    bytes_sk_2 = bytes.fromhex(SK_2)
    bytes_sk_3 = bytes.fromhex(SK_3)
    bytes_sk_4 = bytes.fromhex(SK_4)

    opt = bytes(variable_sph._n)
    r = prf_msg(bytes_sk_2, opt, data, variable_sph._n)
    size_md = math.floor((variable_sph._k * variable_sph._a + 7) / 8)
    size_idx_tree = math.floor((variable_sph._h - variable_sph._h // variable_sph._d + 7) / 8)
    size_idx_leaf = math.floor((variable_sph._h // variable_sph._d + 7) / 8)
    digest = hash_msg(r, bytes_sk_3, bytes_sk_4, data, size_md + size_idx_tree + size_idx_leaf)
    return digest.hex()


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
    block = json.dumps(transactions) + str(results['nonce']) + timestamp
    new_hash = SHA256(block)
    nonce = 0
    while not new_hash.startswith(NONCE):
        results['nonce'] += 1
        block = json.dumps(transactions) + str(results['nonce']) + timestamp
        new_hash = SHA256(block)

    if results['header'] == results['nonce']:
        return True

    return False

# def mine_sphincs(transactions, timestamp: str):
#     results = Blockchains.objects.all().values().last()
#     block = json.dumps(transactions) + str(results['nonce']) + timestamp
#     new_hash = SHA256(block)
#     while not new_hash.startswith(NONCE):
#         results['nonce'] += 1
#         block = json.dumps(transactions) + str(results['nonce']) + timestamp
#         new_hash = SHA256(block)
#         data = json.dumps(block.data) + block.prev_hash + block.create_at
#         data = data.encode('utf-8')
#         variable_sph = Sphincs()
#         bytes_sk_1 = bytes.fromhex(SK_1)
#         bytes_sk_2 = bytes.fromhex(SK_2)
#         bytes_sk_3 = bytes.fromhex(SK_3)
#         bytes_sk_4 = bytes.fromhex(SK_4)
#
#         opt = bytes(variable_sph._n)
#         r = prf_msg(bytes_sk_2, opt, data, variable_sph._n)
#         size_md = math.floor((variable_sph._k * variable_sph._a + 7) / 8)
#         size_idx_tree = math.floor((variable_sph._h - variable_sph._h // variable_sph._d + 7) / 8)
#         size_idx_leaf = math.floor((variable_sph._h // variable_sph._d + 7) / 8)
#         digest = hash_msg(r, bytes_sk_3, bytes_sk_4, data, size_md + size_idx_tree + size_idx_leaf)
#
#     if results['header'] == results['nonce']:
#         return True
#
#     return False


def check_valid_mine(transactions, nonce: int):
    print(transactions)
    block = json.dumps(transactions) + str(nonce)
    new_hash = SHA256(block)
    print(new_hash)
    if new_hash.startswith(str(NONCE)):
        return new_hash
    return False


def check_valid_mine_sph(transactions, nonce: int):
    block = json.dumps(transactions) + str(nonce)
    new_hash = SHA256(block)
    print(str(NONCE))
    if new_hash.startswith(str(NONCE)):
        new_hash = hash_mine(block)
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
            if data[0]["destination"] == "none":
                value = results['hash_blockchain']
                block.destination = data[0]["destination"]
                block.prev_hash = value
                block.hash = data[0]["hash_mine"]
                block.create_at = data[0]["create_at"]
                self.chain.append(block)
            else:
                value = results['hash_blockchain']
                block.destination = data[0]["destination"]
                block.prev_hash = value
                block.hash = str(NONCE) + hash(block)
                block.create_at = data[0]["create_at"]
                self.chain.append(block)
        else:
            block.destination = data[0]["destination"]
            block.hash = str(NONCE) + hash(block)
            block.prev_hash = ""
            block.create_at = data[0]["create_at"]
            self.chain.append(block)

    def get_blockchain(self):
        transaction = Transaction.objects.all().values().last()
        print(len(self.chain))
        for block in self.chain:
            print("Data:", transaction)
            print("Previous hash:", block.prev_hash)
            print("Hash:", block.hash)
            results = Blockchains.objects.last()
            if block.destination == 'none':
                block_data = Blockchains(
                    created_at=block.create_at,
                    previous_hash=block.prev_hash,
                    hash_blockchain=block.hash
                )
                block_data.save()
                return
            results = Blockchains.objects.last()
            results = Blockchains.objects.last()
            results.created_at = block.create_at
            results.previous_hash = block.prev_hash
            results.hash_blockchain = block.hash
            results.save()
            print("DONE: ")

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


def generate_key():
    """Tạo khóa AES-256 ngẫu nhiên (32 bytes)"""
    return os.urandom(32)


def generate_iv():
    """Tạo vector khởi tạo IV (16 bytes)"""
    return os.urandom(16)


def encrypt_aes_256(plaintext: bytes, key: bytes, iv: bytes) -> bytes:
    """Mã hóa AES-256 với CBC mode"""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    # Padding dữ liệu để phù hợp với block size (16 bytes)
    pad_len = 16 - (len(plaintext) % 16)
    padded_plaintext = plaintext + bytes([pad_len] * pad_len)

    ciphertext = encryptor.update(padded_plaintext) + encryptor.finalize()
    return ciphertext


def decrypt_aes_256(ciphertext: bytes, key: bytes, iv: bytes) -> bytes:
    """Giải mã AES-256 với CBC mode"""
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(ciphertext) + decryptor.finalize()
    pad_len = decrypted_padded[-1]  # Lấy số byte padding
    return decrypted_padded[:-pad_len]  # Loại bỏ padding


# Ví dụ sử dụng
# if __name__ == "__main__":
#     key = generate_key()
#     iv = generate_iv()
#     plaintext = b"Hello, AES-256!"
#
#     ciphertext = encrypt_aes_256(plaintext, key, iv)
#     decrypted_text = decrypt_aes_256(ciphertext, key, iv)
#
#     print("Plaintext:", plaintext)
#     print("Ciphertext:", ciphertext.hex())
#     print("Decrypted:", decrypted_text)

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
