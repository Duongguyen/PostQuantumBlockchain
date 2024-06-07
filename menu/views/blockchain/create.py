from menu.utils.common.security import Blockchain
from ...models import BlockchainUser


def create_blockchain_use_case(from_send: str, amount: float, create_at: str, destination: str, hash_mine: str):
    blockchain = Blockchain()
    blockchain.add_block([
        {"from": from_send,
         "create_at": create_at,
         "destination": destination,
         "hash_mine": hash_mine}
    ])
    get_blockchain = blockchain.get_blockchain()
    get_user = BlockchainUser.objects.get(username=from_send)
    if destination == "":
        get_user.balance += float(amount)
    else:
        get_user.balance -= float(amount)
    get_user.save()
    # get_balance = blockchain.get_balance(from_send)