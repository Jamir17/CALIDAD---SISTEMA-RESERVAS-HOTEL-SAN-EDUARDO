from flask import Blueprint, render_template, request, jsonify
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from bd import obtener_conexion
from datetime import datetime

notificaciones_bp = Blueprint("notificaciones", __name__)

# ============ CONFIG SMTP (Brevo) ============
# Configura tus credenciales de Brevo
SMTP_SERVER = "smtp-relay.brevo.com"
SMTP_PORT = 587
SMTP_USER = "8ea603001@smtp-brevo.com"  # login brevo
SMTP_PASSWORD = "6x2k9byOXhwPJW0d"          # clave SMTP generada
REMITENTE = "jamir_merino@hotmail.com"  # tu correo visible al usuario                    # <-- usa el mismo remitente verificado

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
            SELECT r.id_reserva, h.numero, t.nombre AS tipo,
                r.fecha_entrada, r.fecha_salida,
                IFNULL(f.total,0) AS total
            FROM reservas r
            JOIN habitaciones h ON r.id_habitacion=h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo=t.id_tipo
            LEFT JOIN facturacion f ON r.id_reserva=f.id_reserva
            WHERE r.id_usuario=%s
            ORDER BY r.fecha_entrada DESC LIMIT 1
        """, (usuario["id_usuario"],))
        reserva = cur.fetchone()

    if not reserva:
        reserva = {"id_reserva": 0, "numero": "-", "tipo": "Sin reservas",
                "fecha_entrada": "-", "fecha_salida": "-", "total": 0}

    html = render_template("email_confirmacion.html", reserva={
        **reserva,
        "nombres": usuario["nombres"],
        "correo": usuario["correo"]
    })


    enviado = enviar_correo(usuario["correo"], asunto, html)
    estado = "Enviado" if enviado else "Fallido"

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


def enviar_confirmacion_reserva(id_reserva: int, correo_override: str | None = None) -> bool:
    """
    Envía correo de confirmación usando los datos reales de la reserva.
    Si 'correo_override' viene (p.ej. correo del huésped), se usa ese destino.
    Si no, se usa el correo del cliente dueño de la cuenta (tabla clientes).
    También registra el envío en 'historial_notificaciones'.
    """
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.id_reserva, r.id_usuario,
                   c.nombres, c.correo,
                   h.numero,
                   t.nombre AS tipo,
                   DATE_FORMAT(r.fecha_entrada, '%%Y-%%m-%%d') AS fecha_entrada,
                   DATE_FORMAT(r.fecha_salida, '%%Y-%%m-%%d') AS fecha_salida,
                   IFNULL(f.total, 0) AS total
            FROM reservas r
            JOIN clientes c        ON r.id_cliente     = c.id_cliente
            JOIN habitaciones h     ON r.id_habitacion  = h.id_habitacion
            JOIN tipo_habitacion t  ON h.id_tipo        = t.id_tipo
            LEFT JOIN facturacion f ON f.id_reserva     = r.id_reserva
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        datos = cur.fetchone()

    if not datos:
        return False

    # destinatario: huésped si lo ingresaste; si no, el correo del cliente
    destinatario = (correo_override or "").strip() or datos["correo"]

    asunto = f"Confirmación de reserva #{datos['id_reserva']} – Hotel San Eduardo"
    html = render_template("email_confirmacion.html", reserva=datos)

    ok = enviar_correo(destinatario, asunto, html)

    # Registrar en historial_notificaciones
    try:
        with con.cursor() as cur:
            cur.execute("""
                INSERT INTO historial_notificaciones
                    (id_usuario, tipo, correo_destino, asunto, estado, fecha_envio)
                VALUES (%s, %s, %s, %s, %s, NOW())
            """, (
                datos["id_usuario"],
                "confirmacion",
                destinatario,
                asunto,
                "Enviado" if ok else "Error"
            ))
        con.commit()
    except Exception as e:
        print("LOG NOTI ERROR:", e)

    return ok