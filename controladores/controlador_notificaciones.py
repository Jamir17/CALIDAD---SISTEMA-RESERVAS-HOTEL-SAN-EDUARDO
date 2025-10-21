from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bd import obtener_conexion
from datetime import datetime

notificaciones_bp = Blueprint("notificaciones", __name__)

# =========================
# 📧 CONFIGURACIÓN SMTP BREVO
# =========================
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "8ea603002@smtp-brevo.com"   # Tu usuario SMTP Brevo
SMTP_PASSWORD = "7KA1hPWvaVyqYTLr"       # Tu clave SMTP generada
REMITENTE = "jamir_merino@hotmail.com"   # Dirección visible


def enviar_correo(destinatario: str, asunto: str, html_contenido: str) -> bool:
    """Envia correo real por Brevo. Devuelve True/False."""
    try:
        msg = MIMEMultipart()
        msg["From"] = REMITENTE
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(html_contenido, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("❌ SMTP error:", e)
        return False


# ============ Buscar por DNI ============
@notificaciones_bp.route("/buscar_usuario", methods=["GET"])
def buscar_usuario():
    dni = (request.args.get("dni") or "").strip()
    if not dni:
        return jsonify({"ok": False, "msg": "DNI vacío"})
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT id_usuario, nombres, correo FROM usuarios WHERE dni=%s", (dni,))
        row = cur.fetchone()
    if not row:
        return jsonify({"ok": False, "msg": "No existe usuario con ese DNI"})
    return jsonify({"ok": True, "id_usuario": row["id_usuario"], "nombres": row["nombres"], "correo": row["correo"]})


# ============ Enviar correo + registrar ============
@notificaciones_bp.route("/enviar_correo", methods=["POST"])
def enviar_correo_real():
    dni = (request.form.get("dni") or "").strip()
    tipo = (request.form.get("tipo") or "confirmacion").strip().lower()

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM usuarios WHERE dni=%s", (dni,))
        usuario = cur.fetchone()

    if not usuario:
        return jsonify({"ok": False, "msg": "No se encontró un usuario con ese DNI"})

    asunto = f"{tipo.capitalize()} - Hotel San Eduardo"

    with con.cursor() as cur:
        cur.execute("""
            SELECT 
                r.id_reserva,
                h.numero AS hab_numero,
                t.nombre AS hab_tipo,
                t.precio_base,
                r.fecha_entrada,
                r.fecha_salida,
                DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
                IFNULL(f.total,0) AS total,
                r.num_huespedes
            FROM reservas r
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            LEFT JOIN facturacion f ON r.id_reserva = f.id_reserva
            WHERE r.id_usuario=%s
            ORDER BY r.fecha_entrada DESC
            LIMIT 1
        """, (usuario["id_usuario"],))
        reserva = cur.fetchone()

    if not reserva:
        reserva = {
            "id_reserva": 0,
            "hab_numero": "-",
            "hab_tipo": "Sin reservas",
            "precio_base": 0,
            "fecha_entrada": "-",
            "fecha_salida": "-",
            "noches": 0,
            "num_huespedes": 0,
            "total": 0
        }

    # Renderizar el correo con los datos esperados por la plantilla
    html = render_template("email_confirmacion.html", r=reserva, servicios=[])

    # Enviar correo real
    enviado = enviar_correo(usuario["correo"], asunto, html)
    estado = "Enviado" if enviado else "Fallido"

    # Registrar en historial
    with con.cursor() as cur:
        cur.execute("""
            INSERT INTO historial_notificaciones
                (id_usuario, tipo, correo_destino, asunto, estado, fecha_envio)
            VALUES (%s, %s, %s, %s, %s, NOW())
        """, (usuario["id_usuario"], tipo, usuario["correo"], asunto, estado))
        con.commit()

    return jsonify({"ok": enviado, "msg": ("Correo enviado correctamente" if enviado else "Error al enviar correo")})

# ============ Historial (con rango de fechas) ============
@notificaciones_bp.route("/historial", methods=["GET"])
def historial():
    desde = request.args.get("desde")
    hasta = request.args.get("hasta")

    con = obtener_conexion()
    with con.cursor() as cur:
        sql = """
            SELECT n.id_notificacion, u.nombres, n.tipo, n.correo_destino,
                   n.asunto, n.estado, n.fecha_envio
            FROM historial_notificaciones n
            JOIN usuarios u ON u.id_usuario = n.id_usuario
            WHERE 1=1
        """
        params = []
        if desde:
            sql += " AND n.fecha_envio >= %s"
            params.append(desde + " 00:00:00")
        if hasta:
            sql += " AND n.fecha_envio <= %s"
            params.append(hasta + " 23:59:59")
        sql += " ORDER BY n.fecha_envio DESC"
        cur.execute(sql, tuple(params))
        rows = cur.fetchall()

    # serializar fechas -> string
    data = []
    for r in rows:
        data.append({
            "id_notificacion": r["id_notificacion"],
            "nombres": r["nombres"],
            "tipo": r["tipo"],
            "correo_destino": r["correo_destino"],
            "asunto": r["asunto"],
            "estado": r["estado"],
            "fecha_envio": r["fecha_envio"].strftime("%Y-%m-%d %H:%M:%S") if r["fecha_envio"] else ""
        })
    return jsonify({"ok": True, "items": data})





def _enviar_correo(destinatario: str, asunto: str, html: str) -> bool:
    """Envía 1 correo HTML. Devuelve True/False."""
    try:
        msg = MIMEMultipart()
        msg["From"] = REMITENTE
        msg["To"] = destinatario
        msg["Subject"] = asunto
        msg.attach(MIMEText(html, "html"))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print("SMTP error ->", e)
        return False
    
def enviar_confirmacion_reserva_multi(id_reserva: int, correos: list[str]) -> None:
    """
    Envía la confirmación de la reserva a N correos y registra cada envío
    en historial_notificaciones.
    """
    if not correos:
        return

    con = obtener_conexion()
    with con.cursor() as cur:
        # Trae TODOS los datos que queremos en el correo
        cur.execute("""
            SELECT r.id_reserva, r.fecha_entrada, r.fecha_salida, r.num_huespedes,
                   DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
                   u.id_usuario, u.nombres AS usuario_nombres, u.correo AS correo_usuario,
                   c.nombres AS cliente_nombres, c.apellidos AS cliente_apellidos, c.correo AS correo_cliente,
                   h.numero AS hab_numero, t.nombre AS hab_tipo, t.precio_base,
                   COALESCE(f.total,0) AS total
            FROM reservas r
            JOIN usuarios u   ON u.id_usuario  = r.id_usuario
            JOIN clientes c   ON c.id_cliente  = r.id_cliente
            JOIN habitaciones h ON h.id_habitacion = r.id_habitacion
            JOIN tipo_habitacion t ON t.id_tipo = h.id_tipo
            LEFT JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        datos = cur.fetchone()

        # Servicios seleccionados
        cur.execute("""
            SELECT s.nombre, rs.cantidad AS qty, rs.subtotal
            FROM reserva_servicio rs
            JOIN servicios s ON s.id_servicio = rs.id_servicio
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        servicios = cur.fetchall()

    # Render del correo
    html = render_template("email_confirmacion.html", r=datos, servicios=servicios)
    asunto = f"Confirmación de Reserva #{datos['id_reserva']} • Hotel San Eduardo"

    # Enviar a cada destinatario y registrar
    con = obtener_conexion()
    with con.cursor() as cur:
        for correo in {c.strip().lower() for c in correos if c}:
            exito = _enviar_correo(correo, asunto, html)
            cur.execute("""
                INSERT INTO historial_notificaciones (id_usuario, tipo, correo_destino, asunto, estado, fecha_envio)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (datos["id_usuario"], "confirmacion", correo, asunto, "Enviado" if exito else "Error"))
        con.commit()