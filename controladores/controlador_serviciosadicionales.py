from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from datetime import date
from bd import obtener_conexion
import json, decimal
from datetime import datetime
from flask import make_response

servicios = Blueprint('servicios', __name__, url_prefix='/servicios')

# ================================
# LISTAR SERVICIOS DISPONIBLES
# ================================
@servicios.route('/')
def listar_servicios():
    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT id_servicio, nombre, descripcion, precio, estado
            FROM servicios
            WHERE estado = 1
        """)
        filas = cursor.fetchall()
    conexion.close()

    lista = []
    for fila in filas:
        precio_val = fila.get('precio', 0)
        if isinstance(precio_val, decimal.Decimal):
            precio_val = float(precio_val)

        lista.append({
            'id_servicio': fila.get('id_servicio'),
            'nombre': fila.get('nombre', 'Servicio sin nombre'),
            'descripcion': fila.get('descripcion', 'Sin descripción disponible'),
            'precio': precio_val,
            'estado': fila.get('estado', 1)
        })

    return render_template(
        'servicios_adicionales.html',
        servicios=lista,
        servicios_json=json.dumps(lista, ensure_ascii=False),
        fecha_actual=date.today().strftime("%Y-%m-%d")
    )

# ================================
# FILTRAR SERVICIOS DISPONIBLES
# ================================
@servicios.route('/disponibles', methods=['POST'])
def servicios_disponibles():
    data = request.get_json()
    fecha = data.get('fecha')
    hora = data.get('hora')

    if not fecha or not hora:
        return jsonify({'ok': False, 'msg': 'Fecha u hora no proporcionada.'}), 400

    con = obtener_conexion()
    with con.cursor() as cur:
        # 🧩 1️⃣ Obtener todos los servicios activos
        cur.execute("""
            SELECT id_servicio, nombre, descripcion, precio, tipo_disponibilidad
            FROM servicios
            WHERE estado = 1
        """)
        servicios = cur.fetchall()

        # 🧩 2️⃣ Buscar servicios reservados en ese horario (solo los de tipo "único")
        cur.execute("""
            SELECT sr.id_servicio
            FROM servicio_reservado sr
            WHERE sr.fecha = %s AND sr.hora = %s AND sr.estado = 'Ocupado'
        """, (fecha, hora))
        reservados = {row["id_servicio"] for row in cur.fetchall()}

    con.close()

    # 🧩 3️⃣ Filtrar: ocultar servicios "únicos" reservados, mostrar siempre los "múltiples"
    disponibles = []
    for s in servicios:
        if s["tipo_disponibilidad"] == "multiple" or s["id_servicio"] not in reservados:
            disponibles.append(s)

    return jsonify({'ok': True, 'servicios': disponibles})


# ================================
# RESERVAR SERVICIOS
# ================================
@servicios.route('/reservar', methods=['POST'])
def reservar_servicios():
    data = request.get_json(silent=True) or {}
    id_cliente = data.get("id_cliente")
    fecha = data.get("fecha")
    servicios_sel = data.get("servicios")  # [{id, nombre, precio, hora, qty?}]

    if not id_cliente or not fecha or not servicios_sel:
        return jsonify({"ok": False, "msg": "Datos incompletos para la reserva."})

    # Validar formato de horas por ítem y rango 06:00-21:00
    def hora_valida(hhmm: str) -> bool:
        try:
            hh, mm = hhmm.split(":")
            hh = int(hh); mm = int(mm)
            return (6 <= hh <= 21) and (mm in (0, 30))
        except Exception:
            return False

    for s in servicios_sel:
        if not s.get("id") or not s.get("hora"):
            return jsonify({"ok": False, "msg": "Cada servicio debe incluir id y hora."})
        if not hora_valida(s["hora"]):
            return jsonify({"ok": False, "msg": f"Hora inválida para {s.get('nombre','servicio')}."})

    # Chequeo de disponibilidad para servicios de tipo 'unico'
    # (si tu tabla 'servicios' tiene tipo_disponibilidad: 'unico'/'multiple')
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            ids = tuple({int(s["id"]) for s in servicios_sel})
            # Obtener tipo_disponibilidad por id
            cur.execute(f"""
                SELECT id_servicio, 
                       COALESCE(tipo_disponibilidad, 'unico') AS tipo
                FROM servicios
                WHERE id_servicio IN {ids if len(ids)>1 else f'({list(ids)[0]})'}
            """)
            tipos = {row["id_servicio"]: row["tipo"] for row in cur.fetchall()}

            # Validar conflictos solo para 'unico'
            conflictos = []
            for s in servicios_sel:
                sid = int(s["id"])
                if tipos.get(sid, "unico") == "unico":
                    cur.execute("""
                        SELECT COUNT(*) AS c
                        FROM servicio_reservado
                        WHERE id_servicio=%s AND fecha=%s AND hora=%s AND estado='Ocupado'
                    """, (sid, fecha, s["hora"]))
                    if cur.fetchone()["c"] > 0:
                        conflictos.append(f"{s.get('nombre','Servicio')} a las {s['hora']}")

            if conflictos:
                return jsonify({"ok": False,
                                "msg": "No disponible: " + ", ".join(conflictos)})

        # Si todo OK, NO guardamos nada en DB. Solo confirmamos.
        return jsonify({"ok": True, "msg": "Servicios listos para continuar con el pago."})
    finally:
        try:
            con.close()
        except:  # noqa
            pass


# =====================================================
# 🧾 PAGO DE SERVICIOS ADICIONALES
# =====================================================
@servicios.route("/pago", methods=["POST", "GET"])
def pago_servicios():
    # Validar sesión
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    # Si llega por POST → guardar datos en sesión
    if request.method == "POST":
        if request.is_json:
            datos = request.get_json()
            session["reserva_servicio_temp"] = datos
            return jsonify({"ok": True})
        else:
            return jsonify({"ok": False, "msg": "Datos inválidos."})

    # Si llega por GET → mostrar formulario de pago
    reserva_temp = session.get("reserva_servicio_temp")
    if not reserva_temp:
        flash("No hay servicios pendientes de pago.", "error")
        return redirect(url_for("servicios.listar_servicios"))

    # Obtener tipos de pago
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT id_tipo_pago, descripcion FROM tipo_pago")
        tipos_pago = cur.fetchall()
    con.close()

    return render_template("pago_reservas_sa.html", reserva=reserva_temp, tipos_pago=tipos_pago)



# =====================================================
# 💳 CONFIRMAR PAGO DE SERVICIOS ADICIONALES
# =====================================================
@servicios.route("/confirmar_pago", methods=["POST"])
def confirmar_pago():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    reserva_temp = session.get("reserva_servicio_temp")
    if not reserva_temp:
        flash("No hay servicios pendientes de confirmación.", "error")
        return redirect(url_for("servicios.pago_servicios"))

    id_usuario = session["usuario_id"]
    total = float(reserva_temp.get("total", 0))
    servicios_list = reserva_temp.get("servicios", [])
    fecha = reserva_temp.get("fecha")

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            # 🔹 Obtener ID del cliente asociado al usuario
            cur.execute("SELECT id_cliente, correo FROM clientes WHERE id_usuario = %s", (id_usuario,))
            cliente = cur.fetchone()
            if not cliente:
                flash("Cliente no encontrado.", "error")
                return redirect(url_for("servicios.pago_servicios"))

            id_cliente = cliente["id_cliente"]
            correo_cliente = cliente["correo"]

            # ==============================================
            # 🔍 1️⃣ Buscar si el cliente tiene una reserva activa en ese rango de fechas
            # ==============================================
            cur.execute("""
                SELECT id_reserva
                FROM reservas
                WHERE id_cliente = %s
                  AND %s BETWEEN fecha_entrada AND fecha_salida
                  AND estado IN ('Activa', 'Pendiente')
                LIMIT 1
            """, (id_cliente, fecha))
            reserva_existente = cur.fetchone()

            if reserva_existente:
                # ✅ Si hay una reserva activa, la usamos
                id_reserva = reserva_existente["id_reserva"]
                print(f"🔗 Servicio vinculado a la reserva existente ID {id_reserva}")
            else:
                # 🚫 Si no hay reserva activa, crear una nueva (como antes)
                cur.execute("""
                    INSERT INTO reservas (id_cliente, id_usuario, fecha_entrada, fecha_salida, num_huespedes, estado)
                    VALUES (%s, %s, %s, %s, 1, 'Activa')
                """, (id_cliente, id_usuario, fecha, fecha))
                id_reserva = cur.lastrowid
                print(f"🆕 Se creó nueva reserva ID {id_reserva} para el servicio adicional")

            # ==============================================
            # 💾 2️⃣ Insertar los servicios asociados
            # ==============================================
            for s in servicios_list:
                cantidad = s.get("qty", 1)
                subtotal = float(s["precio"]) * cantidad
                origen = "Vinculado" if reserva_existente else "Independiente"
                cur.execute("""
                    INSERT INTO reserva_servicio (id_reserva, id_cliente, id_servicio, fecha_uso, hora_uso, cantidad, subtotal, origen)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (id_reserva, id_cliente, s["id"], fecha, s.get("hora"), cantidad, subtotal, origen))


            # ==============================================
            # 🧾 3️⃣ Registrar facturación (solo una vez por conjunto de servicios)
            # ==============================================
            cur.execute("""
                INSERT INTO facturacion (id_reserva, id_tipo_pago, id_usuario, fecha_emision, total, estado)
                VALUES (%s, %s, %s, NOW(), %s, 'Pagado')
            """, (id_reserva, 1, id_usuario, total))

            con.commit()

        # 🔄 Limpiar sesión temporal
        session.pop("reserva_servicio_temp", None)

    finally:
        con.close()

    # ==============================================
    # 📧 4️⃣ Enviar correo de confirmación
    # ==============================================
    try:
        from controladores.controlador_notificaciones import enviar_confirmacion_reserva_multi
        destinatarios = [correo_cliente]
        enviar_confirmacion_reserva_multi(id_reserva, destinatarios)
    except Exception as e:
        print("⚠️ Error al enviar correo:", e)

    flash("Pago confirmado y vinculado correctamente.", "success")
    return redirect(url_for("servicios.reserva_exitosa_sa", id_reserva=id_reserva))


@servicios.route("/reserva_exitosa_sa/<int:id_reserva>")
def reserva_exitosa_sa(id_reserva):
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        # 🔹 Datos generales del cliente y reserva
        cur.execute("""
            SELECT 
                r.id_reserva,
                c.nombres AS cliente_nombres,
                c.apellidos AS cliente_apellidos,
                DATE(MAX(f.fecha_emision)) AS fecha_reserva,
                MAX(r.id_habitacion) AS id_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            LEFT JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_reserva = %s
            GROUP BY r.id_reserva
        """, (id_reserva,))
        reserva = cur.fetchone()

        if not reserva:
            flash("No se encontró la reserva.", "error")
            return redirect(url_for("servicios.listar_servicios"))

        # 🔹 Calcular el costo total de los servicios de esta reserva
        cur.execute("""
            SELECT SUM(rs.subtotal) AS total_servicio
            FROM reserva_servicio rs
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        total_servicio = cur.fetchone()["total_servicio"] or 0

        # 🔹 Calcular el total acumulado de todos los pagos asociados a esta reserva
        cur.execute("""
            SELECT COALESCE(SUM(f.total), 0) AS total_acumulado
            FROM facturacion f
            WHERE f.id_reserva = %s
        """, (id_reserva,))
        total_acumulado = cur.fetchone()["total_acumulado"]

        # 🔹 Obtener los servicios de la reserva actual
        cur.execute("""
            SELECT s.nombre, rs.cantidad, rs.subtotal
            FROM reserva_servicio rs
            JOIN servicios s ON s.id_servicio = rs.id_servicio
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        servicios = cur.fetchall()

        # 🔹 Si hay una habitación vinculada, mostrarla
        habitacion_vinculada = None
        if reserva["id_habitacion"]:
            cur.execute("""
                SELECT h.numero, t.nombre AS tipo_hab
                FROM habitaciones h
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                WHERE h.id_habitacion = %s
            """, (reserva["id_habitacion"],))
            habitacion_vinculada = cur.fetchone()

    con.close()

    # 🔸 Agregar los totales al diccionario
    reserva["total_servicio"] = total_servicio
    reserva["total_acumulado"] = total_acumulado

    return render_template(
        "reserva_exitosa_sa.html",
        reserva=reserva,
        servicios=servicios,
        habitacion_vinculada=habitacion_vinculada
    )




@servicios.route("/tarjeta")
def tarjeta():
    reserva_temp = session.get("reserva_servicio_temp", {})
    if not reserva_temp:
        flash("No hay servicios para pagar.", "error")
        return redirect(url_for("servicios.pago_servicios"))
    return render_template("tarjeta_servicios.html", reserva=reserva_temp)


@servicios.route("/descargar_comprobante_sa/<int:id_reserva>")
def descargar_comprobante_sa(id_reserva):
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        # 🧾 Datos generales de la reserva
        cur.execute("""
            SELECT 
                r.id_reserva,
                c.nombres AS cliente_nombres,
                c.apellidos AS cliente_apellidos,
                DATE(MAX(f.fecha_emision)) AS fecha_reserva
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            LEFT JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_reserva = %s
            GROUP BY r.id_reserva
        """, (id_reserva,))
        reserva = cur.fetchone()

        if not reserva:
            flash("No se encontró el comprobante o no tienes permiso para verlo.", "error")
            return redirect(url_for("servicios.listar_servicios"))

        # 🔹 Total del servicio actual
        cur.execute("""
            SELECT SUM(rs.subtotal) AS total_servicio
            FROM reserva_servicio rs
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        total_servicio = cur.fetchone()["total_servicio"] or 0

        # 🔹 Total acumulado de todos los pagos de esa reserva
        cur.execute("""
            SELECT COALESCE(SUM(f.total), 0) AS total_acumulado
            FROM facturacion f
            WHERE f.id_reserva = %s
        """, (id_reserva,))
        total_acumulado = cur.fetchone()["total_acumulado"]

        # 🔹 Listar servicios asociados
        cur.execute("""
            SELECT s.nombre, rs.cantidad, rs.subtotal
            FROM reserva_servicio rs
            JOIN servicios s ON s.id_servicio = rs.id_servicio
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        servicios = cur.fetchall()

    con.close()

    # Añadimos los valores al dict
    reserva["total_servicio"] = total_servicio
    reserva["total_acumulado"] = total_acumulado

    # Renderizar el comprobante HTML
    html_content = render_template(
        "comprobante_servicio.html",
        reserva=reserva,
        servicios=servicios
    )

    # Descargar como archivo HTML
    response = make_response(html_content)
    response.headers["Content-Disposition"] = f"attachment; filename=comprobante_servicio_{id_reserva}.html"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response


@servicios.route("/cancelar/<int:id_reserva>", methods=["POST"])
def cancelar_servicio(id_reserva):
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

            # 🔹 2️⃣ Cancelar registros
            cur.execute("""
                UPDATE reserva_servicio
                SET estado='Cancelado'
                WHERE id_reserva=%s
            """, (id_reserva,))

            cur.execute("""
                UPDATE facturacion
                SET estado='Anulado'
                WHERE id_reserva=%s
            """, (id_reserva,))

            cur.execute("""
                UPDATE reservas
                SET estado='Cancelada',
                    motivo_cancelacion=%s,
                    fecha_cancelacion=NOW()
                WHERE id_reserva=%s
            """, (motivo, id_reserva))

            con.commit()

        flash("Reserva de servicio cancelada correctamente.", "success")

        # ==============================================
        # 📧 Enviar correo de cancelación
        # ==============================================
        if correo_cliente:
            try:
                from controladores.controlador_notificaciones import enviar_cancelacion_reserva_multi
                enviar_cancelacion_reserva_multi(id_reserva, [correo_cliente])
                print("✅ Correo de cancelación de servicio enviado correctamente.")
            except Exception as e:
                print("⚠️ Error al enviar correo de cancelación de servicios:", e)
        else:
            print("⚠️ No se encontró correo del cliente, no se envió el correo.")

    except Exception as e:
        con.rollback()
        print("❌ Error al cancelar servicio:", e)
        flash("Ocurrió un error al cancelar el servicio.", "error")

    finally:
        con.close()

    return redirect(url_for("servicios.listar_servicios"))
