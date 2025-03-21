from django.contrib.auth.tokens import PasswordResetTokenGenerator
import six
from pqcrypto.pqcrypto.sign.sphincs_sha256_128s_simple import sign, verify
from ...models import Account
from ...utils.common.security import encrypt_aes_256, decrypt_aes_256
from pqcrypto.pqcrypto.config import PDD_SEA, SK_SEA


class EmailVerificationTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return six.text_type(user.pk) + six.text_type(timestamp) + six.text_type(user.is_active)

email_verification_token = EmailVerificationTokenGenerator()

def sign_transactions(encrypt_data: bytes, user_id):
    sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
    pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)
    decrypt_data = decrypt_aes_256(encrypt_data, sk_sea_bytes_hex, pdd_sea_bytes_hex)

    decrypt_key_hex, public_key_hex = select_key(user_id)
    sign_key = bytes.fromhex(decrypt_key_hex)

    signature_based = sign(sign_key, decrypt_data)
    signature_hex = signature_based
    return signature_hex, encrypt_data

def verify_sign_transactions(signature_hex, data_bytes, user_id):
    sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
    pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)
    decrypt_key_hex, public_key_hex = select_key(user_id)
    decrypt_data = decrypt_aes_256(data_bytes, sk_sea_bytes_hex, pdd_sea_bytes_hex)

    public_key_from_hex = bytes.fromhex(public_key_hex)
    signature_verify = verify(public_key_from_hex, decrypt_data, signature_hex)
    print(signature_verify)
    return signature_verify

def select_key(user_id):
    user_account = Account.objects.get(user_id=user_id)

    secret_key_bytes = bytes.fromhex(user_account.private_key)

    sk_sea_bytes_hex = bytes.fromhex(SK_SEA)
    pdd_sea_bytes_hex = bytes.fromhex(PDD_SEA)

    decrypt_key = decrypt_aes_256(secret_key_bytes, sk_sea_bytes_hex, pdd_sea_bytes_hex)
    decrypt_key_hex = decrypt_key.hex()

    public_key_hex = user_account.address_wallet
    return decrypt_key_hex, public_key_hex