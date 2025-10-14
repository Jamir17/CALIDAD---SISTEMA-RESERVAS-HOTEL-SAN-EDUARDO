from flask import Blueprint, render_template, session, redirect, url_for, flash

admin_bp = Blueprint("admin", __name__)

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

@admin_bp.route("/dashboard", methods=["GET"])
@requiere_login_rol({1, 2})   # Admin o Recepcionista
def dashboard():
    return render_template("index.html", nombre=session.get("nombre"))
    # Cuando tengas tu panel real, cámbialo a render_template("admin_dashboard.html")
