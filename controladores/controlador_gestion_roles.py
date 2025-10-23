from flask import Blueprint, render_template, request, redirect, url_for, flash
from bd import obtener_conexion

gestion_roles_bp = Blueprint("gestion_roles", __name__, url_prefix="/admin/roles")

# ==============================================
# ⚙️ LISTAR ROLES
# ==============================================
@gestion_roles_bp.route("/gestion")
def listar_roles():
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("SELECT * FROM roles ORDER BY id_rol ASC;")
            roles = cur.fetchall()
    finally:
        con.close()
    return render_template("gestion_roles.html", roles=roles)


# ==============================================
# ➕ CREAR ROL
# ==============================================
@gestion_roles_bp.route("/crear", methods=["POST"])
def crear_rol():
    nombre = request.form.get("nombre_rol")
    if not nombre:
        flash("⚠️ Ingresa un nombre para el rol.", "warning")
        return redirect(url_for("gestion_roles.listar_roles"))

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("INSERT INTO roles (nombre_rol) VALUES (%s);", (nombre,))
        con.commit()
        flash("✅ Rol creado correctamente.", "success")
    except Exception as e:
        print("❌ Error al crear rol:", e)
        flash("❌ No se pudo crear el rol.", "danger")
    finally:
        con.close()

    return redirect(url_for("gestion_roles.listar_roles"))


# ==============================================
# ✏️ EDITAR ROL
# ==============================================
@gestion_roles_bp.route("/editar", methods=["POST"])
def editar_rol():
    id_rol = request.form.get("id_rol")
    nombre = request.form.get("nombre_rol")

    if not id_rol or not nombre:
        flash("⚠️ Datos incompletos.", "warning")
        return redirect(url_for("gestion_roles.listar_roles"))

    if int(id_rol) == 3:
        flash("⚠️ El rol 'Cliente' no puede modificarse.", "warning")
        return redirect(url_for("gestion_roles.listar_roles"))

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("UPDATE roles SET nombre_rol=%s WHERE id_rol=%s;", (nombre, id_rol))
        con.commit()
        flash("✅ Rol actualizado correctamente.", "success")
    except Exception as e:
        print("❌ Error al actualizar rol:", e)
        flash("❌ No se pudo actualizar el rol.", "danger")
    finally:
        con.close()

    return redirect(url_for("gestion_roles.listar_roles"))


# ==============================================
# 🗑️ ELIMINAR ROL
# ==============================================
@gestion_roles_bp.route("/eliminar", methods=["POST"])
def eliminar_rol():
    id_rol = request.form.get("id_rol")

    if not id_rol:
        flash("⚠️ No se recibió el ID del rol.", "warning")
        return redirect(url_for("gestion_roles.listar_roles"))

    if int(id_rol) == 3:
        flash("⚠️ El rol 'Cliente' no puede eliminarse.", "warning")
        return redirect(url_for("gestion_roles.listar_roles"))

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("DELETE FROM roles WHERE id_rol=%s;", (id_rol,))
        con.commit()
        flash("🗑️ Rol eliminado correctamente.", "success")
    except Exception as e:
        print("❌ Error al eliminar rol:", e)
        flash("❌ No se pudo eliminar el rol.", "danger")
    finally:
        con.close()

    return redirect(url_for("gestion_roles.listar_roles"))
