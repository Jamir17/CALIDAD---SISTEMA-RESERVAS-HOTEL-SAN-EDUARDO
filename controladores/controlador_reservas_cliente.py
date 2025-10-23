from flask import Blueprint, render_template, request, jsonify
from bd import obtener_conexion
from datetime import datetime

reservas_cliente_bp = Blueprint('reservas_cliente', __name__)

# =========================================================
# 🔍 Función: Obtener clientes (con filtros, paginación)
# =========================================================
@reservas_cliente_bp.route('/admin/reservas-cliente/listar', methods=['GET'])
def listar_clientes():
    """Retorna lista de clientes para el buscador (AJAX)."""
    termino = request.args.get('q', '').strip()
    limite = int(request.args.get('limit', 25))
    con = obtener_conexion()
    with con.cursor(dictionary=True) as cur:
        sql = """
            SELECT id_cliente, CONCAT(nombres, ' ', apellidos) AS nombre_completo,
                   num_documento
            FROM clientes
            WHERE CONCAT(nombres, ' ', apellidos) LIKE %s OR num_documento LIKE %s
            ORDER BY nombres ASC
            LIMIT %s
        """
        cur.execute(sql, (f"%{termino}%", f"%{termino}%", limite))
        data = cur.fetchall()
    con.close()
    return jsonify(data)

# =========================================================
# 📊 Vista principal: historial de reservas
# =========================================================
@reservas_cliente_bp.route('/admin/reservas-cliente')
def historial_reservas_cliente():
    return render_template('reservas_cliente.html')

# =========================================================
# 🧾 Obtener historial de reservas (por cliente + filtros)
# =========================================================
@reservas_cliente_bp.route('/admin/reservas-cliente/historial', methods=['GET'])
def obtener_historial_cliente():
    id_cliente = request.args.get('id_cliente')
    fecha_inicio = request.args.get('fecha_inicio')
    fecha_fin = request.args.get('fecha_fin')
    estado = request.args.get('estado', 'Todos')

    con = obtener_conexion()
    with con.cursor(dictionary=True) as cur:
        query = """
            SELECT r.id_reserva, r.codigo_confirmacion, r.fecha_entrada, r.fecha_salida,
                   DATEDIFF(r.fecha_salida, r.fecha_entrada) AS noches,
                   r.estado, h.numero AS habitacion,
                   IFNULL(f.total, 0) AS monto
            FROM reservas r
            INNER JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
            LEFT JOIN facturacion f ON f.id_reserva = r.id_reserva
            WHERE r.id_cliente = %s
        """
        params = [id_cliente]

        if fecha_inicio and fecha_fin:
            query += " AND r.fecha_entrada BETWEEN %s AND %s"
            params += [fecha_inicio, fecha_fin]

        if estado != "Todos":
            query += " AND r.estado = %s"
            params.append(estado)

        query += " ORDER BY r.fecha_entrada DESC"
        cur.execute(query, params)
        reservas = cur.fetchall()
    con.close()

    # Calcular métricas resumidas
    total_reservas = len(reservas)
    total_noches = sum(r['noches'] for r in reservas)
    total_monto = sum(float(r['monto']) for r in reservas)
    promedio_ticket = round(total_monto / total_reservas, 2) if total_reservas > 0 else 0

    resumen = {
        "total_reservas": total_reservas,
        "total_noches": total_noches,
        "total_monto": total_monto,
        "promedio_ticket": promedio_ticket
    }

    return jsonify({"reservas": reservas, "resumen": resumen})
