from .pqcrypto.pqcrypto.sign.dilithium4 import generate_keypair, sign, verify

public_key, secret_key = generate_keypair()

signature = sign(secret_key, b"Hello world")

assert verify(public_key, b"Hello world", signature)