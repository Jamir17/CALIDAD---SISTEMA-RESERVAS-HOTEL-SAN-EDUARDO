from flask import Blueprint, render_template, request, flash, redirect, url_for
from bd import obtener_conexion
from argon2 import PasswordHasher, exceptions as argon2_errors
import secrets
import re
seguridad_bp = Blueprint("seguridad", __name__)
# 👇 Ajusta el nombre del módulo según donde esté tu enviar_correo
# Ejemplo: si tu código SMTP está en "controlador_notificaciones.py":
from controladores.controlador_notificaciones import enviar_correo

# ===========================================================
# 🔐 Funciones de seguridad (hash de contraseñas y teléfonos)
# ===========================================================

ph = PasswordHasher()  # Argon2id por defecto

def hash_password(plain: str) -> str:
    return ph.hash(plain)

def verify_password(stored_hash: str, plain: str) -> bool:
    if not stored_hash:
        return False
    try:
        ph.verify(stored_hash, plain)
        return True
    except argon2_errors.VerifyMismatchError:
        return False

def a_e164(codigo_pais: str, telefono_raw: str) -> str | None:
    codigo = re.sub(r"\D", "", (codigo_pais or ""))
    numero = re.sub(r"\D", "", (telefono_raw or ""))
    if not codigo or not numero:
        return None
    return f"+{codigo}{numero}"


# ===========================================================
# 📄 Rutas de seguridad (recuperar / restablecer)
# ===========================================================


# ---------------------------
# 📩 Solicitar recuperación
# ---------------------------
@seguridad_bp.route("/recuperar_contraseña", methods=["GET", "POST"])
def recuperar_contraseña():
    if request.method == "POST":
        email = (request.form.get("email") or "").strip()

        if not email:
            flash("Ingresa un correo válido.", "error")
            return redirect(request.url)

        con = obtener_conexion()
        with con.cursor() as cur:
            # Ajustado a tu esquema: tabla usuarios
            cur.execute("SELECT id_usuario FROM usuarios WHERE correo = %s", (email,))
            usuario = cur.fetchone()

            # Siempre respondemos lo mismo por seguridad
            if not usuario:
                flash("Si el correo está registrado, se enviará un enlace de recuperación.", "info")
                return redirect(url_for("usuarios.iniciosesion"))

            # Generar token seguro
            token = secrets.token_urlsafe(32)

            # Guardar token con expiración de 1 hora
            cur.execute("""
                INSERT INTO recuperacion (usuario_id, token, expiracion)
                VALUES (%s, %s, DATE_ADD(NOW(), INTERVAL 1 HOUR))
            """, (usuario["id_usuario"], token))
            con.commit()

        # Enviar correo usando tu función Brevo
        enviar_correo_recuperacion(email, token)

        flash("Si el correo está registrado, se enviará un enlace de recuperación.", "success")
        return redirect(url_for("usuarios.iniciosesion"))

    return render_template("recuperarcontraseña.html")


# ---------------------------
# 🔑 Restablecer contraseña
# ---------------------------
@seguridad_bp.route("/restablecer/<token>", methods=["GET", "POST"])
def restablecer(token):
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT usuario_id FROM recuperacion
            WHERE token = %s AND expiracion > NOW()
        """, (token,))
        data = cur.fetchone()

        if not data:
            flash("El enlace de recuperación no es válido o ha expirado.", "error")
            return redirect(url_for("usuarios.iniciosesion"))

        if request.method == "POST":
            nueva = request.form.get("nueva") or ""
            confirmar = request.form.get("confirmar") or ""

            if len(nueva) < 6:
                flash("La contraseña debe tener al menos 6 caracteres.", "error")
                return redirect(request.url)

            if nueva != confirmar:
                flash("Las contraseñas no coinciden.", "error")
                return redirect(request.url)

            # Actualizar contraseña
            cur.execute("""
                UPDATE usuarios
                SET password_hash = %s
                WHERE id_usuario = %s
            """, (hash_password(nueva), data["usuario_id"]))

            # Borrar tokens usados de ese usuario
            cur.execute("DELETE FROM recuperacion WHERE usuario_id = %s", (data["usuario_id"],))
            con.commit()

            flash("Tu contraseña ha sido restablecida correctamente.", "success")
            return redirect(url_for("usuarios.iniciosesion"))

    return render_template("restablecercontraseña.html", token=token)


# ===========================================================
# 📧 Envío de correo de recuperación (usando Brevo)
# ===========================================================
def enviar_correo_recuperacion(destinatario: str, token: str) -> None:
    # URL absoluta usando Flask (mucho mejor que hardcodear localhost)
    enlace = url_for("seguridad.restablecer", token=token, _external=True)

    asunto = "Recuperación de contraseña - Hotel San Eduardo"
    html = f"""
    <html>
      <body style="font-family: Arial, sans-serif; color:#111827;">
        <h2>Recuperación de contraseña</h2>
        <p>Hemos recibido una solicitud para restablecer tu contraseña del sistema de reservas del <b>Hotel San Eduardo</b>.</p>
        <p>Para crear una nueva contraseña, haz clic en el siguiente botón:</p>
        <p>
          <a href="{enlace}" 
             style="background-color:#2563eb;color:#ffffff;padding:10px 18px;
                    text-decoration:none;border-radius:6px;display:inline-block;">
            Restablecer contraseña
          </a>
        </p>
        <p>Si tú no realizaste esta solicitud, puedes ignorar este mensaje.</p>
        <p style="font-size:12px;color:#6b7280;">Este enlace es válido por 1 hora.</p>
      </body>
    </html>
    """

    # Usamos tu función centralizada de envío
    ok = enviar_correo(destinatario, asunto, html)
    if not ok:
        print("❌ Error al enviar correo de recuperación a", destinatario)
