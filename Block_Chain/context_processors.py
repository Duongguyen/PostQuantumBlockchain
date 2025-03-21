from menu.models import Account
from pqcrypto.pqcrypto.sign.sphincs_sha256_256f_robust import generate_keypair, sign, verify
from pqcrypto.pqcrypto.config import PDD_SEA, SK_SEA
from menu.utils.common.security import decrypt_aes_256
from menu.views.transaction.utils import select_key

def user_keys(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        decrypt_key_hex, public_key_hex = select_key(request.user.id)
        return {
            "public_key": public_key_hex,
            "private_key": decrypt_key_hex
        }
    return {}


def user_balance(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        try:
            user_account = Account.objects.get(user=request.user)
            return {'user_account': user_account}
        except Account.DoesNotExist:
            return {'user_account': None}
    return {'user_account': None}


def user_info(request):
    if request.user.is_authenticated and request.user.username != 'admin':
        return {
            'username': request.user.username  # Lấy username của user
        }
    return {'user_account': None, 'username': None}