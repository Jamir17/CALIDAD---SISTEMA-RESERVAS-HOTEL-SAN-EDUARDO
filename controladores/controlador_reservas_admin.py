from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from bd import obtener_conexion

# Blueprint del panel administrativo
reservas_admin_bp = Blueprint("reservas_admin", __name__)

# ======================================
# Protección de acceso
# ======================================
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


# ======================================
# Panel de reservas (RF05)
# ======================================
@reservas_admin_bp.route("/panel/reservas")
@requiere_login_rol({1, 2})  # 1=Administrador, 2=Recepcionista
def panel_reservas():
    """Muestra todas las reservas con su estado actual."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.id_reserva, c.nombres AS cliente, h.numero AS habitacion,
                   r.fecha_entrada, r.fecha_salida, r.estado, r.num_huespedes
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            ORDER BY r.fecha_entrada DESC
        """)
        reservas = cur.fetchall()

    return render_template("panel_reservas.html", reservas=reservas, nombre=session.get("nombre"))


# ======================================
# Nueva reserva (modal o vista separada)
# ======================================
@reservas_admin_bp.route("/panel/reservas/nueva", methods=["POST"])
@requiere_login_rol({1, 2})
def nueva_reserva():
    """Registra una nueva reserva desde el panel."""
    id_cliente = request.form.get("id_cliente")
    id_habitacion = request.form.get("id_habitacion")
    fecha_entrada = request.form.get("fecha_entrada")
    fecha_salida = request.form.get("fecha_salida")
    tipo_pago = request.form.get("tipo_pago")
    num_huespedes = request.form.get("num_huespedes", 1)
    estado = request.form.get("estado", "Pendiente")

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            INSERT INTO reservas (id_cliente, id_habitacion, id_usuario, fecha_entrada, fecha_salida, num_huespedes, estado)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (id_cliente, id_habitacion, session["usuario_id"], fecha_entrada, fecha_salida, num_huespedes, estado))
        con.commit()

    flash("Reserva registrada correctamente.", "success")
    return redirect(url_for("reservas_admin.panel_reservas"))


# ======================================
# Editar reserva
# ======================================
@reservas_admin_bp.route("/panel/reservas/editar/<int:id_reserva>", methods=["POST"])
@requiere_login_rol({1, 2})
def editar_reserva(id_reserva):
    """Edita fechas o estado de una reserva."""
    fecha_entrada = request.form.get("fecha_entrada")
    fecha_salida = request.form.get("fecha_salida")
    estado = request.form.get("estado")

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            UPDATE reservas
            SET fecha_entrada=%s, fecha_salida=%s, estado=%s
            WHERE id_reserva=%s
        """, (fecha_entrada, fecha_salida, estado, id_reserva))
        con.commit()

    flash("Reserva actualizada correctamente.", "success")
    return redirect(url_for("reservas_admin.panel_reservas"))


# ======================================
# Cancelar o eliminar reserva
# ======================================
@reservas_admin_bp.route("/panel/reservas/eliminar/<int:id_reserva>", methods=["POST"])
@requiere_login_rol({1, 2})
def eliminar_reserva(id_reserva):
    """Cancela o elimina una reserva según el rol."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            UPDATE reservas
            SET estado='Cancelada', fecha_cancelacion=NOW(), motivo_cancelacion='Cancelado por administración'
            WHERE id_reserva=%s
        """, (id_reserva,))
        con.commit()

    flash("Reserva cancelada correctamente.", "success")
    return redirect(url_for("reservas_admin.panel_reservas"))


# ======================================
# Detalle de una reserva
# ======================================
@reservas_admin_bp.route("/panel/reservas/detalle/<int:id_reserva>")
@requiere_login_rol({1, 2})
def detalle_reserva_admin(id_reserva):
    """Ver detalles completos de una reserva (cliente, habitación, pagos)."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.*, c.nombres AS cliente, h.numero AS habitacion, t.nombre AS tipo_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        reserva = cur.fetchone()

    if not reserva:
        flash("No se encontró la reserva solicitada.", "error")
        return redirect(url_for("reservas_admin.panel_reservas"))

    return render_template("detalle_reserva_admin.html", reserva=reserva)
