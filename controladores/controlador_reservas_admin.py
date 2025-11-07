from flask import Blueprint, render_template, session, redirect, url_for, flash, request, jsonify
from bd import obtener_conexion
from datetime import datetime, timedelta
from decimal import Decimal
# Blueprint del panel administrativo
reservas_admin_bp = Blueprint("reservas_admin", __name__)

# ======================================
# Protección de acceso
# ======================================
def requiere_login_rol(roles_permitidos):
    def wrapper(fn):
        def inner(*args, **kwargs):
            if not session.get("usuario_id"):
                flash("Primero inicia sesión.", "error")
                return redirect(url_for("usuarios.iniciosesion"))
            if session.get("rol") not in roles_permitidos:
                flash("No tienes permiso para acceder a esta sección.", "error")
                return redirect(url_for("index"))
            return fn(*args, **kwargs)
        inner.__name__ = fn.__name__
        return inner
    return wrapper


# ======================================
# Panel de reservas (RF05)
# ======================================
@reservas_admin_bp.route("/panel/reservas")
@requiere_login_rol({1, 2})  # 1=Administrador, 2=Recepcionista
def panel_reservas():
    """Muestra todas las reservas con su estado actual."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT 
                r.id_reserva,
                c.nombres AS cliente,
                h.numero AS habitacion,
                r.fecha_entrada,
                r.fecha_salida,
                r.estado,
                r.num_huespedes,
                r.noches,
                COALESCE(r.total, f.total, 0) AS total
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            LEFT JOIN facturacion f ON r.id_reserva = f.id_reserva
            ORDER BY r.fecha_entrada DESC
        """)
        reservas = cur.fetchall()

    # 🧮 Calcular KPIs en backend
    total_reservas = len(reservas)
    activas = len([r for r in reservas if r['estado'] in ['Activa', 'Confirmada']])

    hoy = datetime.now().date()
    proximos_7_dias = hoy + timedelta(days=7)
    proximas = len([
        r for r in reservas
        if r['estado'] in ['Activa', 'Confirmada', 'Pendiente']
        and r['fecha_entrada']
        and hoy <= r['fecha_entrada'] <= proximos_7_dias
    ])

    kpis = {
        'total': total_reservas,
        'activas': activas,
        'proximas': proximas
    }

    return render_template(
        "panel_reservas.html",
        reservas=reservas,
        nombre=session.get("nombre"),
        kpis=kpis
    )


# ======================================
# Nueva reserva (modal o vista separada)
# ======================================
@reservas_admin_bp.route("/panel/reservas/nueva", methods=["POST"])
@requiere_login_rol({1, 2})
def nueva_reserva():
    """Registra una nueva reserva desde el panel administrativo."""
    id_cliente = request.form.get("id_cliente")
    id_habitacion = request.form.get("id_habitacion")
    fecha_entrada = request.form.get("fecha_entrada")
    fecha_salida = request.form.get("fecha_salida")
    num_huespedes = request.form.get("num_huespedes", 1)
    noches = request.form.get("noches", 0)
    total = request.form.get("total", 0)

    print("🟦 Recibido:", id_cliente, id_habitacion, fecha_entrada, fecha_salida, num_huespedes, noches, total)

    if not all([id_cliente, id_habitacion, fecha_entrada, fecha_salida]):
        return jsonify({"ok": False, "error": "Faltan datos obligatorios"}), 400

    con = obtener_conexion()
    with con.cursor() as cur:
        # 🔹 Guardamos también noches y total
        cur.execute("""
            INSERT INTO reservas (
                id_cliente, id_habitacion, id_usuario, 
                fecha_entrada, fecha_salida, num_huespedes, 
                noches, total, estado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Activa')
        """, (
            id_cliente, id_habitacion, session["usuario_id"],
            fecha_entrada, fecha_salida, num_huespedes,
            noches, total
        ))
        con.commit()

    flash("✅ Reserva creada correctamente.", "success")
    return jsonify({"ok": True})



# ======================================
# Editar reserva
# ======================================
@reservas_admin_bp.route("/panel/reservas/editar/<int:id_reserva>", methods=["POST"])
@requiere_login_rol({1, 2})
def editar_reserva(id_reserva):
    """Edita fechas o estado de una reserva."""
    fecha_entrada = request.form.get("fecha_entrada")
    fecha_salida = request.form.get("fecha_salida")
    estado = request.form.get("estado")

    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            UPDATE reservas
            SET fecha_entrada=%s, fecha_salida=%s, estado=%s
            WHERE id_reserva=%s
        """, (fecha_entrada, fecha_salida, estado, id_reserva))
        con.commit()

    flash("Reserva actualizada correctamente.", "success")
    return redirect(url_for("reservas_admin.panel_reservas"))


# ======================================
# Cancelar o eliminar reserva
# ======================================
@reservas_admin_bp.route("/panel/reservas/eliminar/<int:id_reserva>", methods=["POST"])
@requiere_login_rol({1, 2})
def eliminar_reserva(id_reserva):
    """Cancela o elimina una reserva según el rol."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            UPDATE reservas
            SET estado='Cancelada', fecha_cancelacion=NOW(), motivo_cancelacion='Cancelado por administración'
            WHERE id_reserva=%s
        """, (id_reserva,))
        con.commit()

    flash("Reserva cancelada correctamente.", "success")
    return redirect(url_for("reservas_admin.panel_reservas"))


# ======================================
# Detalle de una reserva
# ======================================
@reservas_admin_bp.route("/panel/reservas/detalle/<int:id_reserva>")
@requiere_login_rol({1, 2})
def detalle_reserva_admin(id_reserva):
    """Ver detalles completos de una reserva (cliente, habitación, pagos)."""
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT r.*, c.nombres AS cliente, h.numero AS habitacion, t.nombre AS tipo_habitacion
            FROM reservas r
            JOIN clientes c ON r.id_cliente = c.id_cliente
            JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE r.id_reserva = %s
        """, (id_reserva,))
        reserva = cur.fetchone()

    if not reserva:
        flash("No se encontró la reserva solicitada.", "error")
        return redirect(url_for("reservas_admin.panel_reservas"))

    return render_template("detalle_reserva_admin.html", reserva=reserva)


@reservas_admin_bp.route("/panel/clientes/buscar")
@requiere_login_rol({1, 2})
def buscar_cliente():
    dni = request.args.get("dni")
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("SELECT * FROM clientes WHERE num_documento = %s", (dni,))
        cliente = cur.fetchone()

    # ✅ Asegura que no haya prints que rompan el encabezado
    if cliente:
        resp = jsonify(cliente)
    else:
        resp = jsonify({})
    resp.headers["Content-Type"] = "application/json; charset=utf-8"
    return resp


@reservas_admin_bp.route("/panel/clientes/registrar", methods=["POST"])
@requiere_login_rol({1, 2})
def registrar_cliente():
    data = request.get_json()
    nombres = data.get("nombres")
    apellidos = data.get("apellidos")
    dni = data.get("dni")
    telefono = data.get("telefono") or ""
    correo = data.get("correo") or ""
    direccion = data.get("direccion") or ""

    con = obtener_conexion()
    with con.cursor() as cur:
        # Crear usuario base
        cur.execute("""
            INSERT INTO usuarios (dni, nombres, apellidos, correo, password_hash, telefono, id_rol)
            VALUES (%s, %s, %s, %s, '', %s, 3)
        """, (dni, nombres, apellidos, correo, telefono))
        id_usuario = cur.lastrowid

        # Crear cliente vinculado
        cur.execute("""
            INSERT INTO clientes (tipo_documento, num_documento, nombres, apellidos, telefono, correo, direccion, id_usuario)
            VALUES ('DNI', %s, %s, %s, %s, %s, %s, %s)
        """, (dni, nombres, apellidos, telefono, correo, direccion, id_usuario))
        con.commit()
    return jsonify({"ok": True})




@reservas_admin_bp.route("/panel/habitaciones_disponibles")
@requiere_login_rol({1, 2})
def habitaciones_disponibles():
    id_tipo = request.args.get("tipo")
    entrada = request.args.get("entrada")
    salida = request.args.get("salida")

    print("🟦 Parámetros recibidos:", id_tipo, entrada, salida)

    con = obtener_conexion()
    with con.cursor() as cur:
        # Primero, asegurémonos de que las habitaciones tienen id_tipo asignado
        cur.execute("""
            SELECT h.id_habitacion, h.numero, t.nombre AS tipo, t.precio_base, h.estado
            FROM habitaciones h
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE t.id_tipo = %s
        """, (id_tipo,))
        todas = cur.fetchall()
        print("🔹 Habitaciones totales con ese tipo:", todas)

        # Ahora filtramos solo las disponibles en el rango
        cur.execute("""
            SELECT h.id_habitacion, h.numero, t.nombre AS tipo, t.precio_base
            FROM habitaciones h
            JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
            WHERE t.id_tipo = %s
              AND h.estado = 'Disponible'
              AND h.id_habitacion NOT IN (
                  SELECT r.id_habitacion
                  FROM reservas r
                  WHERE r.estado IN ('Activa', 'Confirmada', 'Pendiente')
                  AND (
                      (%s BETWEEN r.fecha_entrada AND r.fecha_salida)
                      OR (%s BETWEEN r.fecha_entrada AND r.fecha_salida)
                      OR (r.fecha_entrada BETWEEN %s AND %s)
                  )
              )
            ORDER BY h.numero ASC
        """, (id_tipo, entrada, salida, entrada, salida))
        disponibles = cur.fetchall()
        print("✅ Habitaciones disponibles encontradas:", disponibles)

    # Asegurar formato JSON válido
    for h in disponibles:
        if isinstance(h.get("precio_base"), Decimal):
            h["precio_base"] = float(h["precio_base"])

    return jsonify(disponibles)


@reservas_admin_bp.route("/api/tipos_habitacion")
@requiere_login_rol({1, 2})
def api_tipos_habitacion():
    con = obtener_conexion()
    with con.cursor() as cur:
        cur.execute("""
            SELECT id_tipo, nombre 
            FROM tipo_habitacion
            ORDER BY nombre ASC
        """)
        tipos = cur.fetchall()
    return jsonify(tipos) 