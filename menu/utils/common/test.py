# import math
# import json
#
# from pqcrypto.pqcrypto.config import PUBLIC_KEY, SECRET_KEY, NONCE, SK_1, SK_2, SK_3, SK_4
# from menu.sphincs_python.package.sphincs import Sphincs, prf_msg, hash_msg
#
# def hash(block):
#     data = json.dumps(block.data) + block.prev_hash + block.create_at
#     data = data.encode('utf-8')
#     variable_sph = Sphincs()
#     bytes_sk_1 = bytes.fromhex(SK_1)
#     bytes_sk_2 = bytes.fromhex(SK_2)
#     bytes_sk_3 = bytes.fromhex(SK_3)
#     bytes_sk_4 = bytes.fromhex(SK_4)
#
#     opt = bytes(variable_sph._n)
#     # Thay sha256 bang mat ma luong tu
#
#     r = prf_msg(bytes_sk_2, opt, data, variable_sph._n)
#     size_md = math.floor((variable_sph._k * variable_sph._a + 7) / 8)
#     size_idx_tree = math.floor((variable_sph._h - variable_sph._h // variable_sph._d + 7) / 8)
#     size_idx_leaf = math.floor((variable_sph._h // variable_sph._d + 7) / 8)
#
#     digest = hash_msg(r, bytes_sk_3, bytes_sk_4, data, size_md + size_idx_tree + size_idx_leaf)
#     return digest.hex()
#
#
# data = {"from": "Yen", "to": "Duong", "amount": 50}

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

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


if __name__ == "__main__":
    key = generate_key()
    iv = generate_iv()
    plaintext = b"9544fb9c2cb10708a174758a4ba0613c,12853db0344212c53038b95d9c1f3d,ce6bef6680e66d0b887e576,768bb3cf5eb88b70c50d4f0a9f53584557b3af2fd2d"

    ciphertext = encrypt_aes_256(plaintext, key, iv)
    decrypted_text = decrypt_aes_256(ciphertext, key, iv)
    decrypted_text_debytes = decrypted_text.decode("utf-8")

    data_split = decrypted_text_debytes.split(",")

    print("Plaintext:", plaintext)
    print("Ciphertext:", ciphertext.hex())
    print("Decrypted:", decrypted_text)
    print("Split:", data_split)
