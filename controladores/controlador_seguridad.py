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



# seguridad/telefono.py
import re
def a_e164(codigo_pais: str, telefono_raw: str) -> str | None:
    codigo = re.sub(r"\D", "", (codigo_pais or ""))
    numero = re.sub(r"\D", "", (telefono_raw or ""))
    if not codigo or not numero:
        return None
    return f"+{codigo}{numero}"