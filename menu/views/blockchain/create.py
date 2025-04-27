from datetime import datetime

from menu.utils.common.security import Blockchain
from ...models import Account
from ..transaction.utils import verify_sign_transactions
from pqcrypto.pqcrypto.config import PDD_SEA, SK_SEA
from ...utils.common.security import encrypt_aes_256, decrypt_aes_256


def create_blockchain_use_case(encrypt_data_block: bytes, hash_mine: str, user_id: str, signature_hex, data):
    blockchain = Blockchain()
    ver = verify_sign_transactions(signature_hex, data, user_id)
    if ver:
        sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
        pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)
        encrypt_data_block = decrypt_aes_256(encrypt_data_block, sk_sea_bytes_hex, pdd_sea_bytes_hex)
        decoded_string = encrypt_data_block.decode("utf-8")
        # print(f"Data đã giải mã: {decoded_string}")
        data_split = decoded_string.split(",")

        if isinstance(data_split[3], datetime):
            data_split[3] = data_split[3].strftime('%Y-%m-%d %H:%M:%S')

        blockchain.add_block([
            {"from": data_split[0],
             "create_at": data_split[3],
             "destination": data_split[1],
             "hash_mine": hash_mine,
             "header": data_split[4]}
        ])

        get_blockchain = blockchain.get_blockchain()
        get_user = Account.objects.get(user_id=user_id)

        if data_split[1] and data_split[0] and data_split[1] != 'none':
            get_destination = Account.objects.get(address_wallet=data_split[1])
            get_user.balance -= float(data_split[2])
            get_destination.balance += float(data_split[2])
            get_destination.save()
        elif data_split[1] == "none":
            get_user.balance += float(data_split[2])
        else:
            get_user.balance -= float(data_split[2])

        get_user.save()

        return True
    return False
        # get_balance = blockchain.get_balance(from_send)


