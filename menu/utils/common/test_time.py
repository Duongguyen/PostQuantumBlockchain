import json
import math
import time
import hashlib
from pqcrypto.pqcrypto.config import NONCE, SK_1, SK_2, SK_3, SK_4
from menu.sphincs_python.package.sphincs import Sphincs, prf_msg, hash_msg

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

difficulty_1 = "0"
difficulty_2 = "00"
difficulty_3 = "000"
difficulty_4 = "0000"
def test_SHA(difficulty: str):
    data = {
        "from_send": "Duong",
        "timestamp": "2025-03-27 12:29:21",
        "amount": 1.0
    }
    data = json.dumps(data)
    nonce = 0
    start = time.time()
    new_hash = SHA256(data)
    while not new_hash.startswith(difficulty):
        nonce += 1
        data = data + str(nonce)
        new_hash = SHA256(data)
    end = time.time()
    print(f"SHA-256 với độ khó {len(difficulty)}: {nonce} lần thử, mã băm thu được: {new_hash}, thời gian đào: {end - start:.4f} giây")
def test_SPHINCS(difficulty: str):
    data = {
        "from_send": "Duong",
        "timestamp": "2025-03-27 12:29:21",
        "amount": 1.0
    }
    nonce = 0
    data = json.dumps(data)
    start = time.time()
    new_hash = hash_mine(data)
    while not new_hash.startswith(difficulty):
        nonce += 1
        data = data + str(nonce)
        new_hash = hash_mine(data)
    end = time.time()
    print(f"SPHINCS+ với độ khó {len(difficulty)}: {nonce} lần thử, mã băm thu được: {new_hash}, thời gian đào: {end - start:.4f} giây")

test_SHA(difficulty_1)
test_SPHINCS(difficulty_1)
test_SHA(difficulty_2)
test_SPHINCS(difficulty_2)
test_SHA(difficulty_3)
test_SPHINCS(difficulty_3)
test_SHA(difficulty_4)
test_SPHINCS(difficulty_4)
