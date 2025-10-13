# seguridad/telefono.py
import re
def a_e164(codigo_pais: str, telefono_raw: str) -> str | None:
    codigo = re.sub(r"\D", "", (codigo_pais or ""))
    numero = re.sub(r"\D", "", (telefono_raw or ""))
    if not codigo or not numero:
        return None
    return f"+{codigo}{numero}"