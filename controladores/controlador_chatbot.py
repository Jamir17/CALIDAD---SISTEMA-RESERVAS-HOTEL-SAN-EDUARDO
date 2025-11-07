from flask import Blueprint, render_template, session, request, jsonify, flash, redirect, url_for
from bd import obtener_conexion
from flask import jsonify, Blueprint
from datetime import datetime
import secrets

# ===== WebChat (embebido en la web) =====
webchat_bp = Blueprint("webchat", __name__)

# Memoria simple por sesión de navegador (para demo/local)
# En prod usar Redis/BD.
_CONV = {}  # {session_id: {"state": "IDLE", "data": {...}}}

def _sid():
    """Obtiene o crea un ID de sesión único para el chat."""
    if "webchat_sid" not in session:
        session["webchat_sid"] = secrets.token_hex(8)
    return session["webchat_sid"]

def _get_conv():
    sid = _sid()
    if sid not in _CONV:
        _CONV[sid] = {"state": "IDLE", "data": {}}
    return _CONV[sid]

def _reply(text, done=False, state=None):
    """Crea una respuesta JSON estándar para el chatbot."""
    return jsonify({"reply": text, "done": done, "state": state})

def crear_reserva(fecha_in_str, fecha_out_str, huespedes, tipo_hab, nombre_huesped, doc_huesped):
    """
    Crea una reserva en la base de datos a partir de los datos del chatbot.
    Devuelve (codigo_confirmacion, None) en caso de éxito, o (None, error_msg) en caso de fallo.
    """
    try:
        # 1. Validar y convertir fechas
        fecha_in = datetime.strptime(fecha_in_str, "%d/%m/%Y").date()
        fecha_out = datetime.strptime(fecha_out_str, "%d/%m/%Y").date()
        if fecha_out <= fecha_in:
            return None, "La fecha de salida debe ser posterior a la de entrada."
    except ValueError:
        return None, "El formato de fecha debe ser dd/mm/aaaa."

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            # 2. Encontrar una habitación disponible que cumpla los criterios
            cur.execute("""
                SELECT h.id_habitacion, t.id_tipo
                FROM habitaciones h
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                WHERE h.estado = 'Disponible'
                  AND t.nombre LIKE %s
                  AND t.capacidad >= %s
                LIMIT 1
            """, (f"%{tipo_hab}%", huespedes))
            hab_disponible = cur.fetchone()

            if not hab_disponible:
                return None, "No hay habitaciones disponibles con esas características."

            id_habitacion = hab_disponible["id_habitacion"]
            codigo_confirmacion = f"CHAT-{secrets.token_hex(4).upper()}"

            # 3. Crear un cliente "temporal" o buscarlo si ya existe
            cur.execute("SELECT id_cliente FROM clientes WHERE num_documento = %s", (doc_huesped,))
            cliente = cur.fetchone()
            if cliente:
                id_cliente = cliente["id_cliente"]
            else:
                # Dividir el nombre completo en nombre y apellido
                partes_nombre = nombre_huesped.split(' ', 1)
                nombres = partes_nombre[0]
                apellidos = partes_nombre[1] if len(partes_nombre) > 1 else '(sin apellido)'

                cur.execute("""
                    INSERT INTO clientes (nombres, apellidos, num_documento, tipo_documento)
                    VALUES (%s, %s, %s, %s)
                """, (nombres, apellidos, doc_huesped, 'DNI'))
                id_cliente = cur.lastrowid

            # 4. Insertar la reserva
            cur.execute("""
                INSERT INTO reservas (id_cliente, id_habitacion, fecha_entrada, fecha_salida, num_huespedes, estado, codigo_confirmacion)
                VALUES (%s, %s, %s, %s, %s, 'Activa', %s)
            """, (id_cliente, id_habitacion, fecha_in, fecha_out, huespedes, codigo_confirmacion))
            con.commit()
            return codigo_confirmacion, None
    finally:
        con.close()

@webchat_bp.route("/message", methods=["POST"])
def webchat_message():
    payload = request.get_json(silent=True) or {}
    text = (payload.get("text") or "").strip()

    conv = _get_conv()
    st = conv["state"]
    data = conv["data"]

    def ask_fecha_in():
        conv["state"] = "FECHA_IN"
        return _reply("📅 Indica *fecha de entrada* (dd/mm/aaaa):", state="FECHA_IN")

    def ask_fecha_out():
        conv["state"] = "FECHA_OUT"
        return _reply("📅 Ahora la *fecha de salida* (dd/mm/aaaa):", state="FECHA_OUT")

    def ask_huespedes():
        conv["state"] = "HUESPEDES"
        return _reply("👥 ¿Cuántos huéspedes?", state="HUESPEDES")

    def ask_tipo():
        conv["state"] = "TIPO"
        return _reply("🏨 Tipo de habitación (individual | doble | familiar):", state="TIPO")

    def ask_nombre():
        conv["state"] = "NOMBRE"
        return _reply("🧾 Tu *nombre completo*:", state="NOMBRE")

    def ask_doc():
        conv["state"] = "DOC"
        return _reply("🪪 Tu *documento* (DNI/Pasaporte):", state="DOC")

    def ask_confirm():
        conv["state"] = "CONFIRM"
        d = data
        resumen = (f"Confirma tu reserva:\n"
                   f"• Entrada: {d['fecha_in']}\n"
                   f"• Salida: {d['fecha_out']}\n"
                   f"• Huéspedes: {d['huespedes']}\n"
                   f"• Tipo: {d['tipo'].title()}\n"
                   f"• Nombre: {d['nombre']}\n"
                   f"• Doc: {d['doc']}\n\n"
                   f"Responde SI para confirmar o NO para cancelar.")
        return _reply(resumen, state="CONFIRM")

    # Inicio / ayuda
    if st == "IDLE":
        if text.lower() in ("reservar", "/reservar", "/start", "hola", "buenas"):
            return ask_fecha_in()
        return _reply("👋 Hola, soy tu asistente de reservas. Escribe *reservar* para empezar.")

    # Paso a paso
    if st == "FECHA_IN":
        data["fecha_in"] = text
        return ask_fecha_out()

    if st == "FECHA_OUT":
        data["fecha_out"] = text
        return ask_huespedes()

    if st == "HUESPEDES":
        try:
            n = int(text)
            if n <= 0: raise ValueError()
            data["huespedes"] = n
        except:
            return _reply("Ingresa un número válido de huéspedes.", state="HUESPEDES")
        return ask_tipo()

    if st == "TIPO":
        data["tipo"] = text
        return ask_nombre()

    if st == "NOMBRE":
        data["nombre"] = text
        return ask_doc()

    if st == "DOC":
        data["doc"] = text
        return ask_confirm()

    if st == "CONFIRM":
        if text.strip().upper() in ("SI", "SÍ"):
            codigo, err = crear_reserva(
                data["fecha_in"], data["fecha_out"], data["huespedes"],
                data["tipo"], data["nombre"], data["doc"]
            )
            # Reiniciar estado
            _CONV.pop(_sid(), None)
            if err:
                return _reply(f"⚠️ {err}", done=True)
            return _reply(f"✅ ¡Listo! Tu código de reserva es {codigo}.", done=True)
        else:
            _CONV.pop(_sid(), None)
            return _reply("Operación cancelada. Escribe *reservar* cuando quieras.", done=True)

    # Fallback
    return _reply("No entendí. Escribe *reservar* para empezar.")

@webchat_bp.route("/reset", methods=["POST"])
def webchat_reset():
    """Reinicia la conversación del chatbot para el usuario actual."""
    _CONV.pop(_sid(), None)
    return jsonify({"ok": True})
