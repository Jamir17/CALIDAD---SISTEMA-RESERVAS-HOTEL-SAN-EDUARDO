from flask import Blueprint, render_template, session, redirect, url_for, flash
from bd import obtener_conexion

admin_bp = Blueprint("admin", __name__)

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

# ===== Dashboard general =====
@admin_bp.route("/dashboard", methods=["GET"])
@requiere_login_rol({1, 2})   # 1 = Administrador, 2 = Recepcionista
def dashboard():
    con = obtener_conexion()
    with con.cursor() as cur:
        # Reservas activas
        cur.execute("SELECT COUNT(*) AS total FROM reservas WHERE estado='Activa'")
        reservas_activas = cur.fetchone()["total"]

        # Habitaciones disponibles
        cur.execute("SELECT COUNT(*) AS total FROM habitaciones WHERE estado='Disponible'")
        habitaciones_disponibles = cur.fetchone()["total"]

        # Clientes registrados
        cur.execute("SELECT COUNT(*) AS total FROM clientes")
        clientes_registrados = cur.fetchone()["total"]

        # Ingresos (solo admin)
        ingresos_totales = 0
        if session["rol"] == 1:  # Solo el admin puede ver ingresos
            cur.execute("SELECT SUM(total) AS total FROM facturacion")
            result = cur.fetchone()
            ingresos_totales = result["total"] if result["total"] else 0

    return render_template(
        "dashboard.html",
        nombre=session.get("nombre"),
        reservas_activas=reservas_activas,
        habitaciones_disponibles=habitaciones_disponibles,
        clientes_registrados=clientes_registrados,
        ingresos_totales=ingresos_totales
    )
