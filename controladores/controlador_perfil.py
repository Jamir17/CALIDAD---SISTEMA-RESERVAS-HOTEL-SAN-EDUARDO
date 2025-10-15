from flask import Blueprint, render_template, session, redirect, url_for, flash, request
from bd import obtener_conexion

perfil_bp = Blueprint("perfil", __name__)

def login_required(f):
    """
    Decorador que verifica si un usuario ha iniciado sesión.
    Si no, lo redirige a la página de inicio de sesión.
    """
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Debes iniciar sesión para ver tu perfil.", "warning")
            return redirect(url_for("usuarios.iniciosesion"))
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@perfil_bp.route("/perfil", methods=["GET", "POST"])
@login_required
def ver_perfil():
    """
    Muestra la página de perfil (GET) y maneja la actualización de datos (POST).
    """
    usuario_id = session.get("usuario_id")

    if request.method == "POST":
        # --- Lógica para actualizar el perfil ---
        nombres = request.form.get("nombres", "").strip()
        apellidos = request.form.get("apellidos", "").strip()
        telefono = request.form.get("telefono", "").strip()
        direccion = request.form.get("direccion", "").strip()

        if not all([nombres, apellidos, telefono]):
            flash("Nombre, apellido y teléfono son campos obligatorios.", "error")
            return redirect(url_for("perfil.ver_perfil"))

        try:
            con = obtener_conexion()
            with con.cursor() as cur:
                # Actualizar tabla usuarios
                cur.execute("""
                    UPDATE usuarios SET nombres=%s, apellidos=%s, telefono=%s
                    WHERE id_usuario=%s
                """, (nombres, apellidos, telefono, usuario_id))

                # Actualizar tabla clientes
                cur.execute("""
                    UPDATE clientes SET nombres=%s, apellidos=%s, telefono=%s, direccion=%s
                    WHERE id_usuario=%s
                """, (nombres, apellidos, telefono, direccion, usuario_id))
            con.commit()
            flash("¡Perfil actualizado con éxito!", "success")
        except Exception as e:
            flash(f"Error al actualizar el perfil: {e}", "error")
        finally:
            con.close()
        
        return redirect(url_for("perfil.ver_perfil"))

    # --- Lógica para mostrar el perfil (GET) ---
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT u.nombres, u.apellidos, u.correo, u.telefono, c.tipo_documento, c.num_documento, c.direccion, c.nacionalidad
            FROM usuarios u
            LEFT JOIN clientes c ON u.id_usuario = c.id_usuario
            WHERE u.id_usuario = %s
        """, (usuario_id,))
        usuario = cur.fetchone()

    if not usuario:
        flash("No se pudieron cargar los datos del perfil.", "error")
        return redirect(url_for("index"))

    return render_template("perfil.html", usuario=usuario)