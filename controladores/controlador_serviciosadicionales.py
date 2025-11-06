from flask import Blueprint, render_template, request, jsonify
from datetime import date
from bd import obtener_conexion
import json, decimal

servicios = Blueprint('servicios', __name__)

# ================================
# LISTAR SERVICIOS DISPONIBLES
# ================================
@servicios.route('/servicios')
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
@servicios.route('/servicios/disponibles', methods=['POST'])
def filtrar_servicios():
    data = request.get_json()
    fecha = data.get('fecha')
    hora = data.get('hora')

    if not fecha or not hora:
        return jsonify({'ok': False, 'msg': 'Seleccione una fecha y hora válidas.'})

    conexion = obtener_conexion()
    with conexion.cursor() as cursor:
        cursor.execute("""
            SELECT s.id_servicio, s.nombre, s.descripcion, s.precio
            FROM servicios s
            WHERE s.estado = 1
            AND s.id_servicio NOT IN (
                SELECT rs.id_servicio
                FROM reserva_servicio rs
                WHERE rs.fecha = %s AND rs.hora = %s
            )
        """, (fecha, hora))
        servicios = cursor.fetchall()
    conexion.close()

    return jsonify({'ok': True, 'servicios': servicios})


# ================================
# RESERVAR SERVICIOS
# ================================
@servicios.route('/servicios/reservar', methods=['POST'])
def reservar_servicios():
    data = request.get_json()
    id_cliente = data.get('id_cliente')
    fecha = data.get('fecha')
    hora = data.get('hora')
    servicios_seleccionados = data.get('servicios')

    if not id_cliente or not fecha or not hora or not servicios_seleccionados:
        return jsonify({'ok': False, 'msg': 'Datos incompletos para la reserva.'})

    if not ("06:00" <= hora <= "21:00"):
        return jsonify({'ok': False, 'msg': 'Horario no disponible (06:00 - 21:00).'}), 400

    conexion = obtener_conexion()
    try:
        with conexion.cursor() as cursor:
            for s in servicios_seleccionados:
                id_servicio = int(s.get('id'))
                cantidad = int(s.get('qty', 1))
                precio = float(s.get('precio', 0))
                subtotal = precio * cantidad

                # Validar disponibilidad antes de registrar
                cursor.execute("""
                    SELECT COUNT(*) FROM reserva_servicio
                    WHERE id_servicio=%s AND fecha=%s AND hora=%s
                """, (id_servicio, fecha, hora))
                ocupado = cursor.fetchone()[0]

                if ocupado > 0:
                    conexion.rollback()
                    return jsonify({'ok': False, 'msg': f'El servicio {s.get("nombre")} ya está reservado a esa hora.'})

                cursor.execute("""
                    INSERT INTO reserva_servicio (id_reserva, id_cliente, id_servicio, cantidad, subtotal, fecha, hora)
                    VALUES (NULL, %s, %s, %s, %s, %s, %s)
                """, (id_cliente, id_servicio, cantidad, subtotal, fecha, hora))

            conexion.commit()
    except Exception as e:
        conexion.rollback()
        return jsonify({'ok': False, 'msg': f'Error al registrar servicios: {e}'})
    finally:
        conexion.close()

    return jsonify({'ok': True, 'msg': '✅ Servicios reservados correctamente.'})
