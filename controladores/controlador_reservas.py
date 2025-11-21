from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from bd import obtener_conexion
import json
import os
from werkzeug.utils import secure_filename
from datetime import datetime
from decimal import Decimal
from flask import make_response

reservas_bp = Blueprint("reservas", __name__)

from datetime import datetime, date, timedelta

def _parse_to_date(value):
    """Convierte value a objeto date de forma segura.
       Acepta: date, datetime, str en formatos comunes.
       Devuelve None si no puede parsear.
    """
    if value is None:
        return None
    # si ya es date
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    # si es datetime
    if isinstance(value, datetime):
        return value.date()
    # si es string, probar varios formatos
    if isinstance(value, str):
        for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                return datetime.strptime(value, fmt).date()
            except Exception:
                pass
        # intentar parseo heurístico (ISO)
        try:
            return datetime.fromisoformat(value).date()
        except Exception:
            return None
    # fallback
    return None

@reservas_bp.route("/cliente/habitacion/<int:id_habitacion>/ocupadas")
def obtener_fechas_ocupadas(id_habitacion):
    """Devuelve una lista de fechas ocupadas (YYYY-MM-DD) para una habitación."""
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT fecha_entrada, fecha_salida
                FROM reservas
                WHERE id_habitacion = %s
                  AND estado IN ('Activa', 'Pendiente')
            """, (id_habitacion,))
            registros = cur.fetchall()

        fechas_ocupadas = set()

        for fila in registros:
            # soporte para cursor que devuelve dicts o tuplas
            if fila is None:
                continue

            if isinstance(fila, dict):
                raw_ini = fila.get("fecha_entrada") or fila.get("fecha_inicio") or fila.get("entrada")
                raw_fin = fila.get("fecha_salida") or fila.get("fecha_fin") or fila.get("salida")
            else:
                # tupla: asumimos (fecha_entrada, fecha_salida, ...)
                raw_ini = fila[0] if len(fila) > 0 else None
                raw_fin = fila[1] if len(fila) > 1 else None

            fecha_ini = _parse_to_date(raw_ini)
            fecha_fin = _parse_to_date(raw_fin)

            # si no podemos parsear, saltar este registro
            if not fecha_ini or not fecha_fin:
                continue

            # si rango inválido o 0 noches, saltar
            if fecha_fin <= fecha_ini:
                continue

            actual = fecha_ini
            while actual < fecha_fin:
                fechas_ocupadas.add(actual.strftime("%Y-%m-%d"))
                actual += timedelta(days=1)

        return jsonify(sorted(list(fechas_ocupadas)))
    except Exception as e:
        print("❌ Error al obtener fechas ocupadas:", e)
        # opcional: imprimir stacktrace para debug en local
        import traceback; traceback.print_exc()
        return jsonify([]), 200
    finally:
        try:
            con.close()
        except Exception:
            pass

def safe_strftime(value, fmt="%Y-%m-%d"):
    """
    Convierte value a string formateado de forma segura.
    - Si value es datetime -> usa .strftime(fmt)
    - Si value es str -> intenta parsearlo con varios formatos y luego formatear
    - Si no puede -> devuelve str(value)
    """
    if value is None:
        return None

    # ya es str con el formato deseado (optimización)
    if isinstance(value, str):
        # intentamos parsear ISO / SQL DATETIME / fecha corta
        for f in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S", "%d/%m/%Y", "%d-%m-%Y"):
            try:
                dt = datetime.strptime(value, f)
                return dt.strftime(fmt)
            except Exception:
                pass
        # si no pudimos parsear, devolvemos la cadena tal cual
        return value

    # si ya es datetime (o date)
    if hasattr(value, "strftime"):
        try:
            return value.strftime(fmt)
        except Exception:
            return str(value)

    # fallback general
    return str(value)

@reservas_bp.route("/cliente/habitaciones")
def habitaciones_cliente():
    if not session.get("usuario_id"):
        flash("Debes iniciar sesión.", "error")
        return redirect(url_for("usuarios.iniciosesion"))

    # --- Filtros del formulario ---
    fecha_entrada = request.args.get("fecha_entrada") or ""
    fecha_salida = request.args.get("fecha_salida") or ""
    tipo = request.args.get("tipo") or ""
    huespedes = request.args.get("huespedes") or ""

    # --- Normalizar fechas ---
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
        # =====================================================
        # 📊 Consulta principal: muestra todas las habitaciones
        # pero marca las que están reservadas en el rango dado
        # =====================================================
        query = """
            SELECT 
                h.id_habitacion,
                h.numero,
                h.estado,
                t.nombre AS tipo,
                t.descripcion,
                t.precio_base,
                t.capacidad,
                COALESCE(t.comodidades, '') AS comodidades,
                h.imagen AS portada,
                CASE
                    WHEN EXISTS (
                        SELECT 1
                        FROM reservas r
                        WHERE r.id_habitacion = h.id_habitacion
                          AND r.estado IN ('Activa', 'Pendiente')
                          AND %s < r.fecha_salida
                          AND %s > r.fecha_entrada
                    )
                    THEN 1 ELSE 0
                END AS reservada
            FROM habitaciones h
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE 1=1
        """
        params = [fecha_salida or "2100-01-01", fecha_entrada or "1900-01-01"]

        # --- Filtro por tipo ---
        if tipo:
            query += " AND t.nombre = %s"
            params.append(tipo)

        # --- Filtro por capacidad ---
        if huespedes:
            query += " AND t.capacidad >= %s"
            params.append(int(huespedes))

        query += " ORDER BY t.precio_base ASC"

        cur.execute(query, tuple(params))
        habitaciones = cur.fetchall()

        # 🔸 Recuperar combos
        cur.execute("SELECT DISTINCT nombre FROM tipo_habitacion ORDER BY nombre")
        tipos_unicos = cur.fetchall()

        cur.execute("SELECT id_servicio, nombre, precio FROM servicios WHERE estado = 1")
        servicios = cur.fetchall()

    return render_template(
        "habitaciones_cliente.html",
        habitaciones=habitaciones,
        tipos_unicos=tipos_unicos,
        servicios=servicios,
        servicios_json=json.dumps(servicios, default=str),
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



def json_safe(x):
    if isinstance(x, Decimal):
        return float(x)
    if isinstance(x, (list, tuple)):
        return [json_safe(i) for i in x]
    if isinstance(x, dict):
        return {k: json_safe(v) for k, v in x.items()}
    return x

@reservas_bp.route("/cliente/pago_reserva", methods=["POST", "GET"])
def pago_reserva():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    # =======================================================
    # POST → Guarda reserva en sesión o procesa pago
    # =======================================================
    if request.method == "POST":
        # 🔹 JSON (desde habitaciones_cliente)
        if request.is_json:
            datos = request.get_json()
            reserva = datos[0] if isinstance(datos, list) else datos
            if not isinstance(reserva, dict):
                return jsonify({"ok": False, "error": "Formato JSON no válido"}), 400

            # Si es servicios adicionales
            if reserva.get("tipo") == "Servicios adicionales":
                reserva["id_habitacion"] = None
                reserva["entrada"] = reserva.get("fecha")
                reserva["salida"] = reserva.get("fecha")
                reserva["noches"] = 1
                reserva["precio"] = 0

            session["reserva_temp"] = json_safe(reserva)
            return jsonify({"ok": True})

        # 🔹 POST del formulario
        reserva_temp = dict(session.get("reserva_temp", {}))
        reserva_temp["huesped"] = {
            "nombre": request.form.get("nombre_huesped"),
            "documento": request.form.get("documento_huesped"),
            "telefono": request.form.get("telefono_huesped"),
            "correo": request.form.get("correo_huesped"),
        }

        tipo_pago = request.form.get("tipo_pago")
        reserva_temp["id_tipo_pago"] = tipo_pago

        # Recalcular totales
        def to_float(v): return float(v) if isinstance(v, Decimal) else (v or 0)
        total_servicios = sum(to_float(s.get("precio", 0)) for s in reserva_temp.get("servicios", []))
        total_estancia = to_float(reserva_temp.get("precio", 0)) * to_float(reserva_temp.get("noches", 0))
        reserva_temp["total"] = round(total_servicios + total_estancia, 2)
        session["reserva_temp"] = json_safe(reserva_temp)

        # 💳 Pago con tarjeta
        if tipo_pago == "2":
            return redirect(url_for("reservas.tarjeta"))

        # 🧾 Pago con comprobante
        comprobante_field = None
        if tipo_pago == "1":
            comprobante_field = "comprobante_transferencia"
        elif tipo_pago == "3":
            comprobante_field = "comprobante_yape"
        elif tipo_pago == "4":
            comprobante_field = "comprobante_plin"

        comprobante_filename = None
        if comprobante_field:
            file = request.files.get(comprobante_field)
            if file and file.filename:
                carpeta = os.path.join("static", "img", "comprobantes")
                os.makedirs(carpeta, exist_ok=True)
                nombre_seguro = secure_filename(file.filename)
                ruta_guardado = os.path.join(carpeta, nombre_seguro)
                file.save(ruta_guardado)
                comprobante_filename = ruta_guardado

        # 🧩 Obtener id_cliente
        con = obtener_conexion()
        with con.cursor() as cur:
            cur.execute("SELECT id_cliente, correo FROM clientes WHERE id_usuario = %s", (session["usuario_id"],))
            cliente = cur.fetchone()

        if not cliente:
            flash("No se encontró cliente asociado al usuario actual.", "error")
            return redirect(url_for("reservas.habitaciones_cliente"))

        id_cliente = cliente["id_cliente"]
        correo_cliente = cliente.get("correo")

        # 🏨 Registrar reserva si no existe
        id_reserva = reserva_temp.get("id_reserva")
        if not id_reserva:
            with con.cursor() as cur:
                cur.execute("""
                    INSERT INTO reservas (
                        id_cliente, id_habitacion, id_usuario,
                        fecha_entrada, fecha_salida, num_huespedes,
                        noches, total, estado
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activa')
                """, (
                    id_cliente,
                    reserva_temp.get("id_habitacion"),
                    session.get("usuario_id"),
                    reserva_temp.get("entrada"),
                    reserva_temp.get("salida"),
                    1,
                    reserva_temp.get("noches", 0),
                    reserva_temp.get("total", 0)
                ))
                id_reserva = cur.lastrowid
                con.commit()
                reserva_temp["id_reserva"] = id_reserva
                session["reserva_temp"] = json_safe(reserva_temp)

        # 🧮 Registrar facturación
        with con.cursor() as cur:
            cur.execute("""
                INSERT INTO facturacion (
                    id_reserva, id_tipo_pago, id_usuario,
                    fecha_emision, total, estado, comprobante_pago
                )
                VALUES (%s, %s, %s, CURDATE(), %s, %s, %s)
            """, (
                id_reserva,
                tipo_pago,
                session.get("usuario_id"),
                float(reserva_temp.get("total", 0)),
                "Pagado",
                comprobante_filename
            ))
            con.commit()
            print("✅ Facturación registrada para la reserva:", id_reserva)

        # ==========================================
        # 📧 Enviar correo de confirmación
        # ==========================================
        try:
            print("🔔 Intentando enviar correo de confirmación...")
            from controladores.controlador_notificaciones import enviar_confirmacion_reserva_multi
            print("📨 Módulo de notificaciones importado correctamente.")
            print("📧 Correo del cliente:", correo_cliente)
            if correo_cliente:
                enviar_confirmacion_reserva_multi(id_reserva, [correo_cliente])
                print("✅ Correo de confirmación enviado correctamente.")
            else:
                print("⚠️ No se encontró correo del cliente. No se envió correo.")
        except Exception as e:
            print("❌ Error al enviar correo de confirmación:", e)

        # ✅ Limpiar sesión y redirigir
        session.pop("reserva_temp", None)
        flash("¡Reserva y pago confirmados! Se envió la confirmación por correo.", "success")
        return redirect(url_for("reservas.reserva_exitosa", id_reserva=id_reserva))

    # =======================================================
    # GET → Mostrar página de pago
    # =======================================================
    reserva_temp = session.get("reserva_temp")
    if not reserva_temp:
        flash("No hay datos de reserva seleccionados.", "error")
        return redirect(url_for("reservas.habitaciones_cliente"))

    def to_float(v): return float(v) if isinstance(v, Decimal) else (v or 0)
    total_servicios = sum(to_float(s.get("precio", 0)) for s in reserva_temp.get("servicios", []))
    total_estancia = to_float(reserva_temp.get("precio", 0)) * to_float(reserva_temp.get("noches", 0))
    reserva_temp["total"] = round(total_servicios + total_estancia, 2)
    session["reserva_temp"] = json_safe(reserva_temp)

    # Tipos de pago
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
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            # 🧩 Obtener id_cliente y correo
            cur.execute("SELECT id_cliente, correo FROM clientes WHERE id_usuario = %s", (id_usuario,))
            cliente = cur.fetchone()
            if not cliente:
                flash("No se encontró cliente asociado.", "error")
                return redirect(url_for("reservas.habitaciones_cliente"))

            # 🏨 Insertar reserva
            cur.execute("""
                INSERT INTO reservas (
                    id_cliente, id_habitacion, id_usuario,
                    fecha_entrada, fecha_salida, num_huespedes,
                    noches, total, estado
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activa')
            """, (
                cliente["id_cliente"],
                reserva_temp["id_habitacion"],
                id_usuario,
                reserva_temp["entrada"],
                reserva_temp["salida"],
                1,
                reserva_temp.get("noches", 0),
                reserva_temp.get("total", 0)
            ))
            id_reserva = cur.lastrowid

            # 🧾 Insertar servicios adicionales (si existen)
            for s in reserva_temp.get("servicios", []):
                subtotal = float(s["precio"]) * int(s["qty"])
                cur.execute("""
                    INSERT INTO reserva_servicio (id_reserva, id_servicio, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (id_reserva, s["id"], s["qty"], subtotal))

            # 💰 Insertar facturación
            cur.execute("""
                INSERT INTO facturacion (
                    id_reserva, id_tipo_pago, id_usuario,
                    fecha_emision, total, estado, comprobante_pago
                )
                VALUES (%s, %s, %s, CURDATE(), %s, 'Pagado', NULL)
            """, (
                id_reserva,
                reserva_temp.get('id_tipo_pago', 2),
                id_usuario,
                reserva_temp.get("total", 0)
            ))

            con.commit()
            print("✅ Reserva registrada correctamente con ID:", id_reserva)

        # ==========================================
        # 📧 Enviar correo de confirmación
        # ==========================================
        try:
            print("🔔 Intentando enviar correo de confirmación...")
            from controladores.controlador_notificaciones import enviar_confirmacion_reserva_multi
            print("📨 Módulo de notificaciones importado correctamente.")
            correo_cliente = cliente.get("correo")
            print("📧 Correo del cliente:", correo_cliente)
            if correo_cliente:
                enviar_confirmacion_reserva_multi(id_reserva, [correo_cliente])
                print("✅ Intento de envío de correo completado.")
            else:
                print("⚠️ No se encontró correo del cliente. No se envió el correo.")
        except Exception as e:
            print("❌ Error al enviar correo de confirmación:", e)

    finally:
        try:
            con.close()
        except Exception as e:
            print("⚠️ Error al cerrar conexión:", e)

    # Limpieza final
    session.pop("reserva_temp", None)
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
        # 🔹 Reservas de habitaciones
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

        # 🔹 Reservas de servicios (vinculadas o independientes)
        cur.execute("""
            SELECT 
                rs.id_reserva_servicio,
                COALESCE(r.id_reserva, 0) AS id_reserva,
                DATE(COALESCE(MAX(f.fecha_emision), MAX(rs.fecha_uso), CURDATE())) AS fecha,
                COALESCE(MAX(f.total), MAX(rs.subtotal), 0) AS total,
                COALESCE(MAX(f.estado), MAX(rs.estado), 'Pendiente') AS estado,
                CASE 
                    WHEN rs.id_reserva IS NULL THEN 'Independiente'
                    ELSE 'Vinculado'
                END AS origen,
                GROUP_CONCAT(CONCAT(s.nombre, ' x', rs.cantidad)
                             ORDER BY s.nombre SEPARATOR ', ') AS servicios,
                MAX(h.numero) AS habitacion_vinculada,
                MAX(t.nombre) AS tipo_habitacion
            FROM reserva_servicio rs
            LEFT JOIN reservas r         ON rs.id_reserva = r.id_reserva
            LEFT JOIN clientes c         ON c.id_cliente = COALESCE(rs.id_cliente, r.id_cliente)
            LEFT JOIN servicios s        ON s.id_servicio = rs.id_servicio
            LEFT JOIN habitaciones h     ON r.id_habitacion = h.id_habitacion
            LEFT JOIN tipo_habitacion t  ON h.id_tipo = t.id_tipo
            LEFT JOIN facturacion f      ON f.id_reserva = r.id_reserva
            WHERE c.id_usuario = %s
            GROUP BY rs.id_reserva_servicio
            ORDER BY fecha DESC
        """, (uid,))

        reservas_servicios = cur.fetchall()

    con.close()

    # 🔸 Protección adicional
    for r in reservas_servicios:
        r["total"] = float(r.get("total") or 0)
        r["estado"] = r.get("estado", "Pendiente")
        r["origen"] = r.get("origen", "Independiente")

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
    correo_cliente = None
    try:
        with con.cursor() as cur:
            # 🔹 1️⃣ Obtener correo antes de cerrar cursor
            cur.execute("""
                SELECT c.correo 
                FROM reservas r
                JOIN clientes c ON r.id_cliente = c.id_cliente
                WHERE r.id_reserva = %s
            """, (id_reserva,))
            cliente = cur.fetchone()
            correo_cliente = cliente.get("correo") if cliente else None

            # 🔹 2️⃣ Cancelar reserva principal
            cur.execute("""
                UPDATE reservas
                SET estado='Cancelada',
                    motivo_cancelacion=%s,
                    fecha_cancelacion=NOW()
                WHERE id_reserva=%s
            """, (motivo, id_reserva))

            # 🔹 3️⃣ Cancelar servicios vinculados
            cur.execute("""
                UPDATE reserva_servicio
                SET estado='Cancelado'
                WHERE id_reserva=%s
            """, (id_reserva,))

            # 🔹 4️⃣ Anular facturación
            cur.execute("""
                UPDATE facturacion
                SET estado='Anulado'
                WHERE id_reserva=%s
            """, (id_reserva,))

            con.commit()

        flash("Reserva y servicios vinculados cancelados correctamente.", "success")

        # ==============================================
        # 📧 Enviar correo de cancelación
        # ==============================================
        if correo_cliente:
            try:
                from controladores.controlador_notificaciones import enviar_cancelacion_reserva_multi
                enviar_cancelacion_reserva_multi(id_reserva, [correo_cliente])
                print("✅ Correo de cancelación de reserva enviado correctamente.")
            except Exception as e:
                print("⚠️ Error al enviar correo de cancelación:", e)
        else:
            print("⚠️ No se encontró correo del cliente, no se envió el correo.")

    except Exception as e:
        con.rollback()
        print("❌ Error al cancelar reserva:", e)
        flash("Ocurrió un error al cancelar la reserva.", "error")

    finally:
        con.close()

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

@reservas_bp.route("/cliente/comprobante/<int:id_reserva>")
def comprobante_reserva(id_reserva):
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT 
                r.id_reserva, r.fecha_entrada, r.fecha_salida,
                DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
                c.nombres AS cliente_nombres, c.apellidos AS cliente_apellidos,
                c.tipo_documento, c.num_documento, c.correo,
                h.numero AS hab_numero, t.nombre AS hab_tipo,
                f.total, f.fecha_emision, f.id_factura,
                tp.descripcion AS metodo_pago
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            JOIN facturacion f ON r.id_reserva = f.id_reserva
            JOIN tipo_pago tp ON f.id_tipo_pago = tp.id_tipo_pago
            WHERE r.id_reserva = %s AND r.id_usuario = %s
        """, (id_reserva, session["usuario_id"]))
        reserva = cur.fetchone()

    if not reserva:
        flash("No se encontró el comprobante o no tienes permiso para verlo.", "error")
        return redirect(url_for("reservas.mis_reservas"))

    return render_template("comprobante_reserva.html", reserva=reserva)

@reservas_bp.route("/cliente/descargar_comprobante/<int:id_reserva>")
def descargar_comprobante(id_reserva):
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT 
                r.id_reserva, r.fecha_entrada, r.fecha_salida,
                DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
                c.nombres AS cliente_nombres, c.apellidos AS cliente_apellidos,
                c.tipo_documento, c.num_documento, c.correo,
                h.numero AS hab_numero, t.nombre AS hab_tipo,
                f.total, f.fecha_emision, f.id_factura,
                tp.descripcion AS metodo_pago
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            JOIN facturacion f ON r.id_reserva = f.id_reserva
            JOIN tipo_pago tp ON f.id_tipo_pago = tp.id_tipo_pago
            WHERE r.id_reserva = %s AND r.id_usuario = %s
        """, (id_reserva, session["usuario_id"]))
        reserva = cur.fetchone()

    if not reserva:
        flash("No se encontró el comprobante o no tienes permiso para verlo.", "error")
        return redirect(url_for("reservas.mis_reservas"))

    # Renderizamos el HTML directamente
    html_content = render_template("comprobante_reserva.html", reserva=reserva)

    # Creamos respuesta para descarga
    response = make_response(html_content)
    response.headers["Content-Disposition"] = f"attachment; filename=comprobante_{id_reserva}.html"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response

from datetime import timedelta
from flask import jsonify

