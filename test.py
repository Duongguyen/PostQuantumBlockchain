from pyspplus import random_sign_keypair, sign, verify

# Tạo cặp khóa
private_key, public_key = random_sign_keypair()

# Dữ liệu cần ký
data = b"Hello, World!"

# Tạo chữ ký số
signature = sign(data, private_key)

# Xác minh chữ ký số
verification_result = verify(data, signature, public_key)

if verification_result:
    print("Chữ ký số hợp lệ.")
else:
    print("Chữ ký số không hợp lệ.")
