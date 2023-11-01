from menu.utils.common.security import Blockchain
from ...models import User


def create_blockchain_use_case(from_send: str, destination: str, amount: float):
    blockchain = Blockchain("Duong")
    blockchain.add_block([
        {"from": from_send, "to": destination, "amount": float(amount)}
    ])
    get_blockchain = blockchain.get_blockchain()
    get_balance = blockchain.get_balance(from_send)
    get_user = User.objects.get(username=from_send)
    get_user.balance -= float(amount)
    get_user.save()
