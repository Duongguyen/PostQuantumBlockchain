from datetime import datetime

from menu.utils.common.security import Blockchain
from ...models import BlockchainUser, User, Account


def create_blockchain_use_case(from_send: str, amount: float, create_at: str, destination: str, hash_mine: str, user_id: str):
    blockchain = Blockchain()

    if isinstance(create_at, datetime):
        create_at = create_at.strftime('%Y-%m-%d %H:%M:%S')

    blockchain.add_block([
        {"from": from_send,
         "create_at": create_at,
         "destination": destination,
         "hash_mine": hash_mine}
    ])
    get_blockchain = blockchain.get_blockchain()
    get_user = Account.objects.get(user_id=user_id)
    if destination == "":
        get_user.balance += float(amount)
    else:
        get_user.balance -= float(amount)
    get_user.save()
    # get_balance = blockchain.get_balance(from_send)


