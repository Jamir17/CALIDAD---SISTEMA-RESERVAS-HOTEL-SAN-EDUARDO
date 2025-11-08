from flask import Blueprint, render_template, session, request, jsonify, flash, redirect, url_for
from bd import obtener_conexion
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

def get_menu_text():
    """Genera el texto del menú principal con enlaces HTML."""
    return (
        "¡Hola! Soy tu asistente virtual. ¿Cómo puedo ayudarte?\n\n"
        "Escribe una de estas opciones:\n"
        "1. **Reservar**: Para iniciar una nueva reserva.\n"
        "2. **Mi reserva**: Para consultar el estado de tu reserva.\n"
        "3. **Ubicación**: Para saber dónde estamos.\n"
        "4. **Servicios**: Para ver nuestros servicios y horarios.\n"
        "5. **Incidencia**: Para reportar un problema.\n"
        "6. **Contáctanos**: Para contactar con una persona."
    )

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

def consultar_reserva_por_codigo(codigo):
    """Busca una reserva por su código y devuelve los detalles."""
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT r.estado, r.fecha_entrada, r.fecha_salida, t.nombre as tipo_habitacion, h.numero as num_habitacion
                FROM reservas r
                JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                WHERE r.codigo_confirmacion = %s
            """, (codigo,))
            reserva = cur.fetchone()
            if not reserva:
                return "No encontré ninguna reserva con ese código."

            return (
                f"Detalles de la reserva {codigo}:\n"
                f"• Estado: {reserva['estado']}\n"
                f"• Habitación: {reserva['num_habitacion']} ({reserva['tipo_habitacion']})\n"
                f"• Check-in: {reserva['fecha_entrada'].strftime('%d/%m/%Y')}\n"
                f"• Check-out: {reserva['fecha_salida'].strftime('%d/%m/%Y')}"
            )
    finally:
        con.close()

def obtener_info_servicios():
    """Obtiene información de horarios y servicios desde la BD."""
    base_info = (
        "<b>Nuestros Horarios Principales:</b>\n"
        "- <b>Check-in:</b> A partir de las 14:00\n"
        "- <b>Check-out:</b> Hasta las 12:00\n"
        "- <b>Desayuno:</b> De 07:00 a 10:00\n\n"
        "<b>Servicios Adicionales:</b>\n"
    )
    servicios_activos = []
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT nombre, precio FROM servicios WHERE estado = 1 ORDER BY nombre")
            for servicio in cur.fetchall():
                servicios_activos.append(f"- {servicio['nombre']} (S/ {servicio['precio']:.2f})")
    finally:
        con.close()

    return base_info + "\n".join(servicios_activos)

def registrar_incidencia(descripcion, habitacion=None):
    """Registra una nueva incidencia en la base de datos."""
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO incidencias (descripcion, id_habitacion) VALUES (%s, %s)", (descripcion, habitacion))
            con.commit()
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

    def ask_codigo_reserva():
        conv["state"] = "CONSULTA_RESERVA"
        return _reply("Por favor, introduce tu código de confirmación:", state="CONSULTA_RESERVA")

    def ask_descripcion_incidencia():
        conv["state"] = "REGISTRO_INCIDENCIA"
        return _reply("Lamento oír eso. Por favor, describe el problema que estás experimentando:", state="REGISTRO_INCIDENCIA")

    def ask_habitacion_incidencia():
        conv["state"] = "HABITACION_INCIDENCIA"
        return _reply("¿Sabes el número de habitación afectada? Si no lo sabes, escribe 'no'.", state="HABITACION_INCIDENCIA")

    # Comando global para cancelar/reiniciar
    if text.lower() in ("cancelar", "menú", "ayuda", "volver"):
        _CONV.pop(_sid(), None)
        return _reply(get_menu_text(), done=True)

    # Inicio / ayuda
    if st == "IDLE":
        user_message = text.lower()
        # 1. Iniciar flujo de reserva
        if any(word in user_message for word in ["1", "reservar", "reserva"]):
            return ask_fecha_in()

        # 2. Ver/Modificar Reserva
        if any(word in user_message for word in ["2", "mi reserva"]):
            return ask_codigo_reserva()

        # 3. Ubicación
        if any(word in user_message for word in ["3", "ubicación", "direccion"]):
            reply = (
                "¡Claro! Nos encontramos en el Hotel San Eduardo, en el corazón de Santa Victoria, Chiclayo. "
                "Es una zona muy céntrica y de fácil acceso."
            )
            return _reply(reply)

        # 4. Servicios y Horarios
        if any(word in user_message for word in ["4", "servicios", "horario"]):
            return _reply(obtener_info_servicios())

        # 5. Reportar incidencia
        if any(word in user_message for word in ["5", "incidencia", "problema", "reportar"]):
            return ask_descripcion_incidencia()

        # 6. Hablar con un agente
        if any(word in user_message for word in ["6", "agente", "persona", "contactar", "contáctanos"]):
            whatsapp_number = "+51942030088" # Reemplaza con tu número
            reply = f"Si prefieres hablar con una persona, puedes contactarnos a nuestro WhatsApp: <a href='https://wa.me/{whatsapp_number}' target='_blank'>{whatsapp_number}</a>."
            return _reply(reply)
        return _reply(get_menu_text())

    # --- Flujo de Reserva ---
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

    # --- Flujo de Consulta de Reserva ---
    if st == "CONSULTA_RESERVA":
        codigo = text.strip().upper()
        respuesta = consultar_reserva_por_codigo(codigo)
        _CONV.pop(_sid(), None)
        return _reply(respuesta, done=True)

    # --- Flujo de Registro de Incidencia ---
    if st == "REGISTRO_INCIDENCIA":
        data["incidencia_desc"] = text
        return ask_habitacion_incidencia()

    if st == "HABITACION_INCIDENCIA":
        num_hab = text.strip()
        id_hab = num_hab if num_hab.isdigit() else None
        registrar_incidencia(data["incidencia_desc"], id_hab)
        _CONV.pop(_sid(), None)
        return _reply("Gracias por tu reporte. Hemos registrado la incidencia y nuestro equipo la revisará a la brevedad.", done=True)


    # Fallback
    return _reply("No entendí tu mensaje. Escribe 'menú' para ver las opciones.")

@webchat_bp.route("/welcome", methods=["GET"])
def webchat_welcome():
    """Devuelve el mensaje de bienvenida inicial con el menú."""
    _CONV.pop(_sid(), None) # Reinicia cualquier estado previo al cargar
    return _reply(get_menu_text())

@webchat_bp.route("/reset", methods=["POST"])
def webchat_reset():
    """Reinicia la conversación del chatbot para el usuario actual."""
    _CONV.pop(_sid(), None)
    return jsonify({"ok": True})
