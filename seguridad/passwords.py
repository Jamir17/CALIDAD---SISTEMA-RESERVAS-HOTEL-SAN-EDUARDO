# seguridad/passwords.py
from argon2 import PasswordHasher, exceptions as argon2_errors

ph = PasswordHasher()  # valores por defecto (Argon2id)

def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(stored_hash: str, plain: str) -> bool:
    if not stored_hash:
        return False
    try:
        ph.verify(stored_hash, plain)
        return True
    except argon2_errors.VerifyMismatchError:
        return False


