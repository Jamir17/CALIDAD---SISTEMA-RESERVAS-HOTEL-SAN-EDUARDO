from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from bd import obtener_conexion

gestion_usuarios_roles_bp = Blueprint("gestion_usuarios_roles", __name__, url_prefix="/admin/usuarios_roles")

# ==============================================
# 👥 LISTAR USUARIOS Y ROLES
# ==============================================
@gestion_usuarios_roles_bp.route("/asignar")
def listar_usuarios_y_roles():
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT u.id_usuario, u.dni, u.nombres, u.apellidos, u.correo, u.telefono,
                       u.estado, u.id_rol, r.nombre_rol
                FROM usuarios u
                JOIN roles r ON u.id_rol = r.id_rol
                ORDER BY u.id_usuario ASC;
            """)
            usuarios = cur.fetchall()

            cur.execute("SELECT id_rol, nombre_rol FROM roles ORDER BY id_rol;")
            roles = cur.fetchall()
    finally:
        con.close()

    return render_template("gestion_usuarios_roles.html", usuarios=usuarios, roles=roles)


# ==============================================
# 🔄 ACTUALIZAR ROL DE USUARIO
# ==============================================
@gestion_usuarios_roles_bp.post("/actualizar")
def actualizar_rol_usuario():
    id_usuario = request.form["id_usuario"]
    id_rol = request.form["id_rol"]

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("UPDATE usuarios SET id_rol = %s WHERE id_usuario = %s", (id_rol, id_usuario))
            con.commit()
        flash("✅ Rol del usuario actualizado correctamente.", "success")
    except Exception as e:
        flash(f"❌ Error al actualizar el rol: {e}", "danger")
    finally:
        con.close()

    return redirect(url_for("gestion_usuarios_roles.listar_usuarios_y_roles"))
