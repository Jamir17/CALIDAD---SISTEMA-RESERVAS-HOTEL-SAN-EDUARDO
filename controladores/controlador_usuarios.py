from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bd import obtener_conexion
from argon2 import PasswordHasher
import re

usuarios_bp = Blueprint("usuarios", __name__)
ph = PasswordHasher()

# =========================================================
# REGISTRO (CLIENTE)
# =========================================================
@usuarios_bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        try:
            nombre = request.form.get("nombre", "").strip()
            apellido = request.form.get("apellido", "").strip()
            correo = request.form.get("correo", "").strip().lower()
            codigo_pais = request.form.get("codigo_pais", "").strip()
            telefono_raw = request.form.get("telefono", "").strip()
            password = request.form.get("password", "")
            confirm_pass = request.form.get("confirm_password", "")
            tipo_doc = request.form.get("tipo_documento", "")
            num_doc = request.form.get("num_documento", "").strip().upper()
            nacionalidad = request.form.get("nacionalidad", "").strip()
            direccion = request.form.get("direccion", "").strip()

            # --- VALIDACIONES ---
            if not all([nombre, apellido, correo, password, confirm_pass, tipo_doc, num_doc, telefono_raw]):
                flash("Completa todos los campos obligatorios.", "error")
                return render_template("registro.html")

            if password != confirm_pass:
                flash("Las contraseñas no coinciden.", "error")
                return render_template("registro.html")

            # Validación de formato de documento
            if tipo_doc == "DNI" and not (num_doc.isdigit() and len(num_doc) == 8):
                flash("El DNI debe tener 8 dígitos numéricos.", "error")
                return render_template("registro.html")

            if tipo_doc == "Pasaporte" and not re.match(r"^[A-Za-z0-9]{6,12}$", num_doc):
                flash("El pasaporte debe tener entre 6 y 12 caracteres alfanuméricos.", "error")
                return render_template("registro.html")

            if tipo_doc == "CE" and not re.match(r"^[A-Za-z0-9]{6,9}$", num_doc):
                flash("El carné de extranjería debe tener entre 6 y 9 caracteres alfanuméricos.", "error")
                return render_template("registro.html")

            # --- TELÉFONO ---
            codigo = re.sub(r"\D", "", codigo_pais)
            numero = re.sub(r"\D", "", telefono_raw)
            telefono_e164 = f"+{codigo}{numero}" if codigo and numero else None

            if not telefono_e164 or len(numero) < 6:
                flash("Número de teléfono inválido.", "error")
                return render_template("registro.html")

            # --- CONEXIÓN BD ---
            con = obtener_conexion()
            with con.cursor() as cur:
                # Correo duplicado
                cur.execute("SELECT 1 FROM usuarios WHERE correo=%s", (correo,))
                if cur.fetchone():
                    flash("El correo ya está registrado.", "error")
                    return render_template("registro.html")

                # Documento duplicado
                cur.execute("SELECT 1 FROM clientes WHERE num_documento=%s", (num_doc,))
                if cur.fetchone():
                    flash("Ya existe un cliente con ese número de documento.", "error")
                    return render_template("registro.html")

                # --- Hash Argon2 ---
                pwd_hash = ph.hash(password)

                # Si es DNI guardamos ese número, si no, guardamos NULL
                dni_valor = num_doc if tipo_doc == "DNI" else None

                # --- Inserción en usuarios ---
                cur.execute("""
                    INSERT INTO usuarios (dni, nombres, apellidos, correo, password_hash, telefono, estado, id_rol)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (dni_valor, nombre, apellido, correo, pwd_hash, telefono_e164, 1, 3))
                id_usuario = cur.lastrowid

                # --- Inserción en clientes ---
                cur.execute("""
                    INSERT INTO clientes
                    (tipo_documento, num_documento, nombres, apellidos, telefono, correo, nacionalidad, direccion, id_usuario)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (tipo_doc, num_doc, nombre, apellido, telefono_e164, correo,
                      nacionalidad or None, direccion or None, id_usuario))

                con.commit()

            flash("✅ Cuenta creada exitosamente. Ahora puedes iniciar sesión.", "success")
            return redirect(url_for("usuarios.iniciosesion"))

        except Exception as e:
            flash(f"⚠️ Error interno: {e}", "error")
            return render_template("registro.html")

    # --- GET ---
    return render_template("registro.html")


# =========================================================
# INICIO DE SESIÓN
# =========================================================
@usuarios_bp.route("/iniciar-sesion", methods=["GET", "POST"])
def iniciosesion():
    if request.method == "POST":
        correo = (request.form.get("email") or "").strip().lower()
        password = request.form.get("password") or ""

        con = obtener_conexion()
        with con.cursor() as cur:
            cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
            usuario = cur.fetchone()

        if not usuario:
            flash("Correo no encontrado.", "error")
            return render_template("iniciosesion.html")

        try:
            if not ph.verify(usuario["password_hash"], password):
                flash("Contraseña incorrecta.", "error")
                return render_template("iniciosesion.html")
        except Exception:
            flash("Error verificando contraseña.", "error")
            return render_template("iniciosesion.html")

        session["usuario_id"] = usuario["id_usuario"]
        session["nombre"] = usuario["nombres"]
        session["rol"] = usuario["id_rol"]
        return redirect(url_for("index"))

    return render_template("iniciosesion.html")


# =========================================================
# CERRAR SESIÓN
# =========================================================
@usuarios_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("usuarios.iniciosesion"))
