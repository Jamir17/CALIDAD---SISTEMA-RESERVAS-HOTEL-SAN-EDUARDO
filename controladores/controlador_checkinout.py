from flask import Blueprint, render_template, session, request, jsonify, flash, redirect, url_for
from bd import obtener_conexion
from datetime import datetime
import pymysql

checkinout_bp = Blueprint("checkinout", __name__)

# ===== Decorador de seguridad =====
def requiere_login_rol(roles_permitidos):
    def wrapper(fn):
        def inner(*args, **kwargs):
            if not session.get("usuario_id"):
                flash("Primero inicia sesión.", "error")
                return redirect(url_for("usuarios.iniciosesion"))
            if session.get("rol") not in roles_permitidos:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        inner.__name__ = fn.__name__
        return inner
    return wrapper

def registrar_actividad(accion, id_reserva, id_habitacion, nuevo_estado_hab):
    """Función auxiliar para registrar una acción en la tabla de actividad."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            INSERT INTO actividad (accion, id_reserva, id_habitacion, nuevo_estado_hab, fecha_hora)
            VALUES (%s, %s, %s, %s, %s)
        """, (accion, id_reserva, id_habitacion, nuevo_estado_hab, datetime.now()))
        con.commit()

@checkinout_bp.route("/panel/checkinout")
@requiere_login_rol({1, 2})
def panel_checkinout():
    """Muestra el panel principal de Check-in/out con datos dinámicos."""
    con = None
    try:
        con = obtener_conexion()
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            # 1. Obtener reservas activas para el select
            cur.execute("""
                SELECT r.id_reserva, c.nombres, c.apellidos, h.numero
                FROM reservas r
                JOIN clientes c ON r.id_cliente = c.id_cliente
                JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
                WHERE r.estado = 'Activa'
                ORDER BY r.id_reserva DESC
            """)
            reservas_activas = cur.fetchall()

            # 2. Obtener estado de todas las habitaciones
            cur.execute("SELECT id_habitacion, numero, estado FROM habitaciones ORDER BY numero ASC")
            habitaciones = cur.fetchall()

            # 3. Obtener KPIs
            cur.execute("SELECT estado, COUNT(*) as total FROM habitaciones GROUP BY estado")
            kpis_raw = cur.fetchall()
            kpis = {'Disponible': 0, 'Ocupada': 0, 'En Limpieza': 0}
            for kpi in kpis_raw:
                if kpi['estado'] in kpis:
                    kpis[kpi['estado']] = kpi['total']

            # 4. Obtener actividad reciente
            cur.execute("""
                SELECT a.fecha_hora, a.accion, a.id_reserva, c.nombres, c.apellidos, h.numero, a.nuevo_estado_hab
                FROM actividad a
                LEFT JOIN reservas r ON a.id_reserva = r.id_reserva
                LEFT JOIN clientes c ON r.id_cliente = c.id_cliente
                LEFT JOIN habitaciones h ON a.id_habitacion = h.id_habitacion
                ORDER BY a.fecha_hora DESC
                LIMIT 10
            """)
            actividades = cur.fetchall()

        return render_template(
            "panel_checkinout.html",
            nombre=session.get("nombre"),
            reservas_activas=reservas_activas,
            habitaciones=habitaciones,
            kpis=kpis,
            actividades=actividades
        )
    finally:
        if con:
            con.close()

# --- API Endpoints para JavaScript ---

@checkinout_bp.route("/checkinout/api/reserva/<int:id_reserva>")
@requiere_login_rol({1, 2})
def get_reserva_details(id_reserva):
    """Devuelve los detalles de una reserva específica en formato JSON."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.id_reserva, r.fecha_entrada, r.fecha_salida, r.estado AS estado_reserva,
                   c.nombres, c.apellidos, h.id_habitacion, h.numero AS numero_habitacion, h.estado AS estado_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        reserva = cur.fetchone()

    if reserva:
        # Formatear fechas para que sean compatibles con JSON
        reserva['fecha_entrada'] = reserva['fecha_entrada'].strftime('%Y-%m-%d')
        reserva['fecha_salida'] = reserva['fecha_salida'].strftime('%Y-%m-%d')
        return jsonify({"ok": True, "reserva": reserva})
    return jsonify({"ok": False, "message": "Reserva no encontrada"})

@checkinout_bp.route("/checkinout/api/checkin", methods=["POST"])
@requiere_login_rol({1, 2})
def api_checkin():
    id_reserva = request.json.get('id_reserva')
    id_habitacion = request.json.get('id_habitacion')
    if not id_reserva or not id_habitacion:
        return jsonify({"ok": False, "message": "Faltan datos"}), 400

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("UPDATE habitaciones SET estado = 'Ocupada' WHERE id_habitacion = %s", (id_habitacion,))
        con.commit()
    
    registrar_actividad('Check-in', id_reserva, id_habitacion, 'Ocupada')
    return jsonify({"ok": True, "message": "Check-in realizado con éxito"})

@checkinout_bp.route("/checkinout/api/checkout", methods=["POST"])
@requiere_login_rol({1, 2})
def api_checkout():
    id_reserva = request.json.get('id_reserva')
    id_habitacion = request.json.get('id_habitacion')
    if not id_reserva or not id_habitacion:
        return jsonify({"ok": False, "message": "Faltan datos"}), 400

    con = obtener_conexion()
    with con.cursor() as cur:
        # Cambiar estado de la habitación a 'En Limpieza'
        cur.execute("UPDATE habitaciones SET estado = 'En Limpieza' WHERE id_habitacion = %s", (id_habitacion,))
        # Cambiar estado de la reserva a 'Finalizada'
        cur.execute("UPDATE reservas SET estado = 'Finalizada' WHERE id_reserva = %s", (id_reserva,))
        con.commit()
    
    registrar_actividad('Check-out', id_reserva, id_habitacion, 'En Limpieza')
    return jsonify({"ok": True, "message": "Check-out realizado con éxito. Habitación marcada para limpieza."})

@checkinout_bp.route("/checkinout/api/limpieza", methods=["POST"])
@requiere_login_rol({1, 2})
def api_limpieza():
    id_habitacion = request.json.get('id_habitacion')
    if not id_habitacion:
        return jsonify({"ok": False, "message": "Falta el ID de la habitación"}), 400

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("UPDATE habitaciones SET estado = 'Disponible' WHERE id_habitacion = %s", (id_habitacion,))
        con.commit()
    
    registrar_actividad('Limpieza OK', None, id_habitacion, 'Disponible')
    return jsonify({"ok": True, "message": "Habitación marcada como disponible."})