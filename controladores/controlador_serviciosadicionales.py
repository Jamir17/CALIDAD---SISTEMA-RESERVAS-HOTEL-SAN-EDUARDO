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
            # Obtener ID del cliente asociado al usuario
            cur.execute("SELECT id_cliente, correo FROM clientes WHERE id_usuario = %s", (id_usuario,))
            cliente = cur.fetchone()
            if not cliente:
                flash("Cliente no encontrado.", "error")
                return redirect(url_for("servicios.pago_servicios"))

            id_cliente = cliente["id_cliente"]
            correo_cliente = cliente["correo"]

            # Registrar una reserva simple en la tabla reservas
            cur.execute("""
                INSERT INTO reservas (id_cliente, id_usuario, fecha_entrada, fecha_salida, num_huespedes, estado)
                VALUES (%s, %s, %s, %s, 1, 'Activa')
            """, (id_cliente, id_usuario, fecha, fecha))
            id_reserva = cur.lastrowid

            # Insertar los servicios asociados
            for s in servicios_list:
                cantidad = s.get("qty", 1)
                subtotal = float(s["precio"]) * cantidad
                cur.execute("""
                    INSERT INTO reserva_servicio (id_reserva, id_servicio, cantidad, subtotal)
                    VALUES (%s, %s, %s, %s)
                """, (id_reserva, s["id"], cantidad, subtotal))

            # Insertar facturación
            cur.execute("""
                INSERT INTO facturacion (id_reserva, id_tipo_pago, id_usuario, fecha_emision, total, estado)
                VALUES (%s, %s, %s, NOW(), %s, 'Pagado')
            """, (id_reserva, 1, id_usuario, total))

            con.commit()

        # Limpiar la sesión temporal
        session.pop("reserva_servicio_temp", None)

    finally:
        con.close()

    # Enviar correo de confirmación
    try:
        from controladores.controlador_notificaciones import enviar_confirmacion_reserva_multi

        destinatarios = [correo_cliente]
        enviar_confirmacion_reserva_multi(id_reserva, destinatarios)

    except Exception as e:
        print("⚠️ Error al enviar correo:", e)

    flash("Pago confirmado y correo enviado con éxito.", "success")
    return redirect(url_for("servicios.reserva_exitosa_sa", id_reserva=id_reserva))




@servicios.route("/reserva_exitosa_sa/<int:id_reserva>")
def reserva_exitosa_sa(id_reserva):
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    con = obtener_conexion()
    with con.cursor() as cur:
        # 👇 Usamos alias para que el template reciba las claves esperadas
        cur.execute("""
            SELECT 
                r.id_reserva            AS id_reserva_servicio,
                c.nombres               AS cliente_nombres,
                c.apellidos             AS cliente_apellidos,
                DATE(f.fecha_emision)   AS fecha_reserva,
                f.total                 AS total
            FROM reservas r
            JOIN clientes c   ON r.id_cliente = c.id_cliente
            JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        reserva = cur.fetchone()

        cur.execute("""
            SELECT s.nombre, rs.cantidad, rs.subtotal
            FROM reserva_servicio rs
            JOIN servicios s ON s.id_servicio = rs.id_servicio
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        servicios = cur.fetchall()

    con.close()

    # Si fecha_reserva llega como str, no uses strftime en el template
    # (el template que te dejo abajo ya lo maneja de forma segura)
    return render_template("reserva_exitosa_sa.html", reserva=reserva, servicios=servicios)



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
                r.id_reserva            AS id_reserva_servicio,
                c.nombres               AS cliente_nombres,
                c.apellidos             AS cliente_apellidos,
                DATE(f.fecha_emision)   AS fecha_reserva,
                f.total                 AS total
            FROM reservas r
            JOIN clientes c   ON r.id_cliente = c.id_cliente
            JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        reserva = cur.fetchone()

        # 🧩 Servicios asociados
        cur.execute("""
            SELECT s.nombre, rs.cantidad, rs.subtotal
            FROM reserva_servicio rs
            JOIN servicios s ON s.id_servicio = rs.id_servicio
            WHERE rs.id_reserva = %s
        """, (id_reserva,))
        servicios = cur.fetchall()

    con.close()

    # Si no se encuentra la reserva
    if not reserva:
        flash("No se encontró el comprobante o no tienes permiso para verlo.", "error")
        return redirect(url_for("servicios.listar_servicios"))

    # Renderizar el comprobante HTML
    html_content = render_template("comprobante_servicio.html", reserva=reserva, servicios=servicios)

    # Retornar el HTML como descarga directa
    response = make_response(html_content)
    response.headers["Content-Disposition"] = f"attachment; filename=comprobante_servicio_{id_reserva}.html"
    response.headers["Content-Type"] = "text/html; charset=utf-8"
    return response
