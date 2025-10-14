from flask import Blueprint, render_template, session, redirect, url_for, flash
from bd import obtener_conexion

reservas_bp = Blueprint("reservas", __name__)

# Listado de habitaciones
@reservas_bp.route("/cliente/habitaciones")
def habitaciones_cliente():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT h.id_habitacion, h.numero, h.estado,
                   t.nombre AS tipo, t.descripcion, t.precio_base
            FROM habitaciones h
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            ORDER BY t.precio_base ASC
        """)
        habitaciones = cur.fetchall()

    return render_template("habitaciones_cliente.html",
                           habitaciones=habitaciones,
                           nombre=session.get("nombre"))

# Detalle de habitación
@reservas_bp.route("/cliente/habitacion/<int:id_habitacion>")
def ver_habitacion(id_habitacion):
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT h.id_habitacion, h.numero, h.estado,
                   t.nombre AS tipo, t.descripcion, t.precio_base
            FROM habitaciones h
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE h.id_habitacion = %s
        """, (id_habitacion,))
        habitacion = cur.fetchone()

    if not habitacion:
        flash("Habitación no encontrada.", "error")
        return redirect(url_for("reservas.habitaciones_cliente"))

    return render_template("reserva_cliente.html", habitacion=habitacion, nombre=session.get("nombre"))
