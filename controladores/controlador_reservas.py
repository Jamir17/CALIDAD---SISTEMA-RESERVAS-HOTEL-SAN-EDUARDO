from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from bd import obtener_conexion
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime

reservas_bp = Blueprint("reservas", __name__)

@reservas_bp.route("/cliente/habitaciones")
def habitaciones_cliente():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    # Leer y normalizar fechas del GET
    fecha_entrada = request.args.get("fecha_entrada") or ""
    fecha_salida = request.args.get("fecha_salida") or ""
    tipo = request.args.get("tipo") or ""
    huespedes = request.args.get("huespedes") or ""

    # Normalizar formato YYYY-MM-DD (evita desfases por zona horaria)
    def normalizar(fecha_str):
        try:
            fecha = datetime.strptime(fecha_str, "%Y-%m-%d")
            return fecha.strftime("%Y-%m-%d")
        except Exception:
            return ""

    fecha_entrada = normalizar(fecha_entrada)
    fecha_salida = normalizar(fecha_salida)

    con = obtener_conexion()
    with con.cursor() as cur:
        query = """
            SELECT h.id_habitacion, h.numero, h.estado,
                   t.nombre AS tipo, t.descripcion, t.precio_base
            FROM habitaciones h
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE 1=1
        """
        params = []

        if tipo:
            query += " AND t.nombre = %s"
            params.append(tipo)
        if huespedes:
            query += " AND h.capacidad >= %s"
            params.append(huespedes)

        query += " ORDER BY t.precio_base ASC"

        cur.execute(query, tuple(params))
        habitaciones = cur.fetchall()

        cur.execute("SELECT DISTINCT nombre FROM tipo_habitacion ORDER BY nombre")
        tipos_unicos = cur.fetchall()

        cur.execute("SELECT id_servicio, nombre, precio FROM servicios WHERE estado = 1")
        servicios = cur.fetchall()

    return render_template(
        "habitaciones_cliente.html",
        habitaciones=habitaciones,
        tipos_unicos=tipos_unicos,
        servicios=servicios,
        servicios_json=json.dumps(servicios),
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        tipo=tipo,
        huespedes=huespedes,
        nombre=session.get("nombre")
    )

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

    # Si es POST desde habitaciones_cliente, guarda la reserva en sesión
    if request.method == "POST":
        if request.is_json:
            datos = request.get_json()
            # Si viene de servicios adicionales, no hay habitación asociada
            if datos.get("tipo") == "Servicios adicionales":
                datos["id_habitacion"] = None
                datos["entrada"] = datos.get("fecha")
                datos["salida"] = datos.get("fecha")
                datos["noches"] = 1
                datos["precio"] = 0  # no aplica habitación
            session["reserva_temp"] = datos
            return jsonify({"ok": True})


        # Si es POST desde el form de datos de huésped, los guarda y redirige
        reserva_temp = session.get("reserva_temp", {})
        reserva_temp['huesped'] = {
            "nombre": request.form.get("nombre_huesped"),
            "documento": request.form.get("documento_huesped"),
            "telefono": request.form.get("telefono_huesped"),
            "correo": request.form.get("correo_huesped"),
        }
        # Guardar el método de pago seleccionado
        reserva_temp['id_tipo_pago'] = request.form.get("tipo_pago")
        session["reserva_temp"] = reserva_temp

        # Si el pago es con tarjeta (ID 2), ir al form de tarjeta.
        # Si no, confirmar directamente.
        if reserva_temp['id_tipo_pago'] == '2':
            return redirect(url_for('reservas.tarjeta'))
        else:
            return redirect(url_for('reservas.confirmar_reserva'))

    # Si es GET → muestra el HTML de pago
    reserva_temp = session.get("reserva_temp")
    if not reserva_temp:
        flash("No hay datos de reserva seleccionados.", "error")
        return redirect(url_for("reservas.habitaciones_cliente"))
    
    # Obtener tipos de pago para el formulario
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT id_tipo_pago, descripcion FROM tipo_pago")
        tipos_pago = cur.fetchall()
    
    return render_template("pago_reserva.html", reserva=reserva_temp, tipos_pago=tipos_pago)


@reservas_bp.route("/cliente/tarjeta", methods=["GET"])
def tarjeta():
    reserva_temp = session.get("reserva_temp")
    if not reserva_temp or not reserva_temp.get('huesped'):
        flash("Por favor, complete primero los datos del huésped.", "error")
        return redirect(url_for("reservas.pago_reserva"))
    return render_template("tarjeta.html", reserva=reserva_temp)




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
    huesped_data = reserva_temp.get("huesped", {})

    # Datos del huésped (puede ser familiar)
    nombre_huesped = huesped_data.get("nombre")
    documento_huesped = huesped_data.get("documento")
    telefono_huesped = huesped_data.get("telefono")
    correo_huesped = huesped_data.get("correo")

    # Archivo del comprobante
    archivo = None # Ya no se usa comprobante, es pago con tarjeta
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
                INSERT INTO reservas (id_cliente, id_habitacion, id_usuario, fecha_entrada, fecha_salida, num_huespedes, estado)
                VALUES (%s, %s, %s, %s, %s, %s, 'Activa')
            """, (cliente["id_cliente"], reserva_temp["id_habitacion"], id_usuario,
                  reserva_temp["entrada"], reserva_temp["salida"], 1))
            id_reserva = cur.lastrowid

            # Insertar servicios adicionales (si los hay)
            for s in reserva_temp.get("servicios", []):
                subtotal = float(s["precio"]) * int(s["qty"])
                cur.execute("""
                    INSERT INTO reserva_servicio (id_reserva, id_servicio, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (id_reserva, s["id"], s["qty"], subtotal))

            # --- Calcular total final con descuento por larga estancia ---
            noches = int(reserva_temp["noches"])
            precio_noche = float(reserva_temp["precio"])
            total_habitacion = precio_noche * noches

            descuento_porcentaje = 0
            if noches >= 30:
                descuento_porcentaje = 0.25  # 25%
            elif noches >= 15:
                descuento_porcentaje = 0.20  # 20%
            elif noches >= 8:
                descuento_porcentaje = 0.10  # 10%

            monto_descuento = total_habitacion * descuento_porcentaje
            subtotal_habitacion = total_habitacion - monto_descuento
            total_serv = sum(float(s["precio"]) * int(s["qty"]) for s in reserva_temp.get("servicios", []))
            total_final = subtotal_habitacion + total_serv

            # Insertar en facturación
            cur.execute("""
                INSERT INTO facturacion (id_reserva, id_tipo_pago, id_usuario, fecha_emision, total, estado, comprobante_pago)
                VALUES (%s, %s, %s, CURDATE(), %s, 'Pagado', NULL)
            """, (id_reserva, reserva_temp.get('id_tipo_pago', 2), id_usuario, total_final))

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
    return redirect(url_for("reservas.reserva_exitosa", id_reserva=id_reserva))


@reservas_bp.route("/cliente/reserva_exitosa/<int:id_reserva>")
def reserva_exitosa(id_reserva):
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT 
                r.id_reserva, r.fecha_entrada, r.fecha_salida,
                DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
                c.nombres AS cliente_nombres, c.apellidos AS cliente_apellidos,
                h.numero AS hab_numero, t.nombre AS hab_tipo,
                f.total
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            JOIN facturacion f ON r.id_reserva = f.id_reserva
            WHERE r.id_reserva = %s AND r.id_usuario = %s
        """, (id_reserva, session["usuario_id"]))
        reserva = cur.fetchone()

    if not reserva:
        flash("No se encontró la reserva o no tienes permiso para verla.", "error")
        return redirect(url_for("habitaciones.habitaciones_cliente"))

    return render_template("reserva_exitosa.html", reserva=reserva)

# ================================================
# Mis reservas de cliente
@reservas_bp.route("/cliente/mis_reservas")
def mis_reservas():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    uid = session["usuario_id"]

    con = obtener_conexion()
    with con.cursor() as cur:
        # 🔷 HABITACIONES: solo las reservas con id_habitacion (LEFT JOIN + filtro NOT NULL)
        cur.execute("""
            SELECT r.id_reserva,
                   r.fecha_entrada, r.fecha_salida,
                   r.num_huespedes, r.estado,
                   t.nombre AS tipo, h.numero AS habitacion
            FROM reservas r
            JOIN clientes c        ON c.id_cliente = r.id_cliente
            LEFT JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            LEFT JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE c.id_usuario = %s
              AND r.id_habitacion IS NOT NULL
            ORDER BY r.fecha_entrada DESC
        """, (uid,))
        reservas_habitaciones = cur.fetchall()

        # 🔷 SERVICIOS: las que tienen líneas en reserva_servicio
        cur.execute("""
            SELECT r.id_reserva AS id_reserva_servicio,
                   DATE(f.fecha_emision) AS fecha,
                   f.total, f.estado,
                   GROUP_CONCAT(CONCAT(s.nombre, ' x', rs.cantidad)
                                ORDER BY s.nombre SEPARATOR ', ') AS servicios
            FROM reservas r
            JOIN clientes c          ON c.id_cliente = r.id_cliente
            JOIN reserva_servicio rs ON rs.id_reserva = r.id_reserva
            JOIN servicios s         ON s.id_servicio = rs.id_servicio
            JOIN facturacion f       ON f.id_reserva = r.id_reserva
            WHERE c.id_usuario = %s
            GROUP BY r.id_reserva, f.fecha_emision, f.total, f.estado
            ORDER BY f.fecha_emision DESC
        """, (uid,))
        reservas_servicios = cur.fetchall()

    con.close()

    # 👉 Asegúrate que tu template use estos nombres
    return render_template(
        "mis_reservas.html",
        reservas_habitaciones=reservas_habitaciones,
        reservas_servicios=reservas_servicios,
        nombre=session.get("nombre")
    )


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






@reservas_bp.route("/cliente/mis_reservas_todo")
def mis_reservas_todo():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    id_usuario = session["usuario_id"]
    con = obtener_conexion()
    with con.cursor() as cur:
        # 🏨 Reservas de habitaciones
        cur.execute("""
            SELECT r.id_reserva, r.fecha_entrada, r.fecha_salida,
                r.num_huespedes, r.estado,
                t.nombre AS tipo, h.numero AS habitacion
            FROM reservas r
            LEFT JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            LEFT JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE r.id_usuario = %s AND r.id_habitacion IS NOT NULL
            ORDER BY r.fecha_entrada DESC
        """, (id_usuario,))
        reservas_habitaciones = cur.fetchall()

        # 🧺 Reservas de servicios adicionales
        cur.execute("""
            SELECT r.id_reserva AS id_reserva_servicio,
                f.fecha_emision AS fecha,
                f.total, f.estado,
                GROUP_CONCAT(s.nombre SEPARATOR ', ') AS servicios
            FROM reservas r
            JOIN reserva_servicio rs ON rs.id_reserva = r.id_reserva
            JOIN servicios s ON s.id_servicio = rs.id_servicio
            JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_usuario = %s
            GROUP BY r.id_reserva, f.fecha_emision, f.total, f.estado
            ORDER BY f.fecha_emision DESC
        """, (id_usuario,))
        reservas_servicios = cur.fetchall()

    con.close()

    return render_template(
        "mis_reservas.html",
        reservas_habitaciones=reservas_habitaciones,
        reservas_servicios=reservas_servicios,
        nombre=session.get("nombre")
    )
