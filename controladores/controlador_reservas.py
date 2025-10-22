from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from bd import obtener_conexion
import os
from werkzeug.utils import secure_filename

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


# ================================================
#  RUTA para recibir la reserva y mostrar pago
# ================================================
@reservas_bp.route("/cliente/pago_reserva", methods=["POST", "GET"])
def pago_reserva():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    # Si el método es POST → guarda los datos en la sesión
    if request.method == "POST":
        datos = request.get_json()
        session["reserva_temp"] = datos
        return jsonify({"ok": True})

    # Si es GET → muestra el HTML de pago
    reserva_temp = session.get("reserva_temp")
    if not reserva_temp:
        flash("No hay datos de reserva seleccionados.", "error")
        return redirect(url_for("reservas.habitaciones_cliente"))

    # Consultar tipos de pago
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT id_tipo_pago, descripcion FROM tipo_pago")
        tipos_pago = cur.fetchall()

    return render_template("pago_reserva.html", reserva=reserva_temp, tipos_pago=tipos_pago)




# ================================================
# Confirmar reserva cliente (actualizado)
# ================================================
UPLOAD_FOLDER = "static/img/comprobantes"
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS



@reservas_bp.route("/cliente/confirmar_reserva", methods=["POST"])
def confirmar_reserva():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    reserva_temp = session.get("reserva_temp")
    if not reserva_temp:
        flash("No hay datos de reserva.", "error")
        return redirect(url_for("reservas.habitaciones_cliente"))

    id_usuario = session["usuario_id"]
    tipo_pago = request.form.get("tipo_pago")

    # Datos del huésped (puede ser familiar)
    nombre_huesped = request.form.get("nombre_huesped")
    documento_huesped = request.form.get("documento_huesped")
    telefono_huesped = request.form.get("telefono_huesped")
    correo_huesped = request.form.get("correo_huesped")

    # Archivo del comprobante
    archivo = request.files.get("comprobante")
    nombre_archivo = None
    if archivo and allowed_file(archivo.filename):
        if not os.path.exists(UPLOAD_FOLDER):
            os.makedirs(UPLOAD_FOLDER)
        nombre_archivo = secure_filename(archivo.filename)
        ruta_guardar = os.path.join(UPLOAD_FOLDER, nombre_archivo)
        archivo.save(ruta_guardar)

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            # Obtener el id_cliente asociado al usuario logueado
            cur.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (id_usuario,))
            cliente = cur.fetchone()
            if not cliente:
                flash("No se encontró cliente asociado.", "error")
                return redirect(url_for("reservas.habitaciones_cliente"))

            # Insertar en reservas
            cur.execute("""
                INSERT INTO reservas (id_cliente, id_habitacion, id_usuario, fecha_entrada, fecha_salida, num_huespedes, estado, imagen_seleccionada)
                VALUES (%s, %s, %s, %s, %s, %s, 'Activa', %s)
            """, (cliente["id_cliente"], reserva_temp["id_habitacion"], id_usuario,
                  reserva_temp["entrada"], reserva_temp["salida"], 1,
                  reserva_temp.get("imagen_seleccionada")))
            id_reserva = cur.lastrowid

            # Insertar servicios adicionales (si los hay)
            for s in reserva_temp.get("servicios", []):
                subtotal = float(s["precio"]) * int(s["qty"])
                cur.execute("""
                    INSERT INTO reserva_servicio (id_reserva, id_servicio, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (id_reserva, s["id"], s["qty"], subtotal))

            # Calcular total final
            total = float(reserva_temp["precio"]) * int(reserva_temp["noches"])
            total_serv = sum(float(s["precio"]) * int(s["qty"]) for s in reserva_temp.get("servicios", []))
            total_final = total + total_serv

            # Insertar en facturación
            cur.execute("""
                INSERT INTO facturacion (id_reserva, id_tipo_pago, id_usuario, fecha_emision, total, estado, comprobante_pago)
                VALUES (%s, %s, %s, CURDATE(), %s, 'Pagado', %s)
            """, (id_reserva, tipo_pago, id_usuario, total_final, nombre_archivo))

            con.commit()
    finally:
        try:
            con.close()
        except Exception:
            pass

    # Eliminar la reserva temporal
    session.pop("reserva_temp", None)

    # ===== Enviar confirmación a 3 posibles correos =====
    # 1) correo del dueño de la cuenta (usuarios)
    # 2) correo del cliente (clientes)
    # 3) correo del huésped adicional (formulario), si lo ingresaron
    con2 = obtener_conexion()
    try:
        with con2.cursor() as cur:
            cur.execute("""
                SELECT u.correo AS correo_usuario, c.correo AS correo_cliente
                FROM reservas r
                JOIN usuarios u ON u.id_usuario = r.id_usuario
                JOIN clientes c ON c.id_cliente = r.id_cliente
                WHERE r.id_reserva = %s
            """, (id_reserva,))
            row = cur.fetchone()
    finally:
        try:
            con2.close()
        except Exception:
            pass

    destinatarios = []
    if row and row.get("correo_usuario"):
        destinatarios.append(row["correo_usuario"])
    if row and row.get("correo_cliente"):
        destinatarios.append(row["correo_cliente"])
    if correo_huesped:
        destinatarios.append(correo_huesped)

    # Quitar duplicados y vacíos
    destinatarios = [c.strip() for c in destinatarios if c and c.strip()]
    destinatarios = list(dict.fromkeys(destinatarios))

    # Enviar (y registrar en historial_notificaciones)
    try:
        from controladores.controlador_notificaciones import enviar_confirmacion_reserva_multi
        if destinatarios:
            enviar_confirmacion_reserva_multi(id_reserva, destinatarios)
    except Exception as _e:
        # No rompemos el flujo por el correo, solo informativo
        print("Aviso: no se pudo enviar confirmación por correo ->", _e)

    flash("¡Reserva confirmada con éxito! Se envió la confirmación por correo.", "success")
    return redirect(url_for("habitaciones.habitaciones_cliente"))


# ================================================
# Mis reservas de cliente
@reservas_bp.route("/cliente/mis_reservas")
def mis_reservas():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    id_usuario = session["usuario_id"]
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.id_reserva, r.codigo_confirmacion, r.fecha_entrada, r.fecha_salida,
                   r.num_huespedes, r.estado, t.nombre AS tipo, h.numero AS habitacion
            FROM reservas r
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE r.id_usuario = %s
            ORDER BY r.fecha_entrada DESC
        """, (id_usuario,))
        reservas = cur.fetchall()

    return render_template("mis_reservas.html", reservas=reservas, nombre=session.get("nombre"))

# ================================================
# Detalle reserva
# ================================================
@reservas_bp.route("/cliente/reserva/<int:id_reserva>")
def detalle_reserva(id_reserva):
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.*, h.numero, t.nombre AS tipo
            FROM reservas r
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        reserva = cur.fetchone()

    return render_template("detalle_reserva.html", reserva=reserva)

# ================================================
# Modificar reserva
# ================================================
@reservas_bp.route("/cliente/modificar_reserva/<int:id_reserva>", methods=["POST"])
def modificar_reserva(id_reserva):
    fecha_entrada = request.form.get("fecha_entrada")
    fecha_salida = request.form.get("fecha_salida")
    huespedes = request.form.get("num_huespedes")

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            UPDATE reservas
            SET fecha_entrada=%s, fecha_salida=%s, num_huespedes=%s
            WHERE id_reserva=%s
        """, (fecha_entrada, fecha_salida, huespedes, id_reserva))
        con.commit()

    flash("Reserva modificada correctamente.", "success")
    return redirect(url_for("reservas.mis_reservas"))

# ================================================
# Cancelar reserva
# ================================================
@reservas_bp.route("/cliente/cancelar_reserva/<int:id_reserva>", methods=["POST"])
def cancelar_reserva(id_reserva):
    motivo = request.form.get("motivo") or "Cancelado por el cliente"

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            UPDATE reservas
            SET estado='Cancelada', motivo_cancelacion=%s, fecha_cancelacion=NOW()
            WHERE id_reserva=%s
        """, (motivo, id_reserva))
        con.commit()

    flash("Reserva cancelada con éxito.", "success")
    return redirect(url_for("reservas.mis_reservas"))
