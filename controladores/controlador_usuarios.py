from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from bd import obtener_conexion
from argon2 import PasswordHasher
import re
from argon2.exceptions import VerifyMismatchError, InvalidHashError

usuarios_bp = Blueprint("usuarios", __name__, template_folder="../templates")
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
        password = (request.form.get("password") or "").strip()
        recordarme = request.form.get("recordarme") == "on"

        con = obtener_conexion()
        try:
            with con.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE correo = %s", (correo,))
                usuario = cur.fetchone()
        finally:
            try:
                con.close()
            except Exception:
                pass

        if not usuario:
            flash("Correo no encontrado.", "error")
            return render_template("iniciosesion.html", correo=correo)

        try:
            ph.verify(usuario["password_hash"].strip(), password)
        except (VerifyMismatchError, InvalidHashError):
            flash("Contraseña incorrecta o hash inválido.", "error")
            return render_template("iniciosesion.html", correo=correo)

        # Guardar datos en sesión
        session["usuario_id"] = usuario["id_usuario"]
        session["nombre"] = usuario["nombres"]
        session["rol"] = usuario["id_rol"]   # ✅ Aquí guardamos el rol del usuario

        # Si marcó "Recordarme"
        session.permanent = bool(recordarme)
        if recordarme:
            session["correo_recordado"] = correo
        else:
            session.pop("correo_recordado", None)

        # ✅ Redirección según el rol
        rol = usuario["id_rol"]

        if rol == 1:  # Administrador
            flash("Bienvenido al panel administrativo.", "success")
            return redirect(url_for("admin.dashboard"))
        elif rol == 2:  # Recepcionista
            flash("Bienvenido al panel de recepción.", "success")
            return redirect(url_for("admin.dashboard"))
        elif rol == 3:  # Cliente
            flash("Inicio de sesión correcto.", "success")
            return redirect(url_for("reservas.habitaciones_cliente"))
        else:
            flash("Rol no reconocido. Contacte al administrador.", "error")
            return redirect(url_for("usuarios.iniciosesion"))

    # GET
    return render_template("iniciosesion.html", correo=session.get("correo_recordado", ""))


# =========================================================
# CERRAR SESIÓN
# =========================================================
@usuarios_bp.route("/logout")
def logout():
    session.clear()
    flash("Sesión cerrada correctamente.", "info")
    return redirect(url_for("usuarios.iniciosesion"))

# =========================================================
# PÁGINA DE CONTACTO
# =========================================================
@usuarios_bp.route("/contacto", methods=["GET", "POST"])
def contacto():
    if request.method == "POST":
        nombre = request.form.get("name", "").strip()
        correo = request.form.get("email", "").strip()
        mensaje = request.form.get("message", "").strip()

        if not all([nombre, correo, mensaje]):
            flash("Por favor, completa todos los campos del formulario.", "error")
            return render_template("contacto.html")

        if "@" not in correo or "." not in correo:
            flash("Por favor, ingresa un correo electrónico válido.", "error")
            return render_template("contacto.html")

        try:
            con = obtener_conexion()
            with con.cursor() as cur:
                cur.execute("""
                    INSERT INTO contacto (nombre, correo, mensaje)
                    VALUES (%s, %s, %s)
                """, (nombre, correo, mensaje))
            con.commit()
            flash("¡Gracias por tu mensaje! Nos pondremos en contacto contigo pronto.", "success")
        except Exception as e:
            flash(f"Hubo un error al enviar tu mensaje: {e}", "error")
        finally:
            con.close()
        return redirect(url_for("usuarios.contacto"))

    return render_template("contacto.html")
