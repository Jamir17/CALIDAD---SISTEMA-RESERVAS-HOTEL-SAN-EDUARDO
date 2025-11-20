# ============================================================
# 📊 CONTROLADOR DE REPORTES ADMINISTRATIVOS - HOTEL SAN EDUARDO
# ============================================================

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from bd import obtener_conexion
from datetime import datetime

reportes_bp = Blueprint("reportes", __name__, url_prefix="/admin/reportes")

# ============================================================
# PANEL PRINCIPAL DE REPORTES
# ============================================================
@reportes_bp.route("/", endpoint="reportes_admin")
def panel_reportes():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    # === Valores base ===
    kpis = {
        "total_reservas": 0,
        "total_clientes": 0,
        "ingresos_hospedaje": 0.0,
        "ingresos_servicios": 0.0,
        "total_incidencias": 0
    }
    ocupacion = []
    ingresos_mensuales = []
    ult_actividades = []

    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            # === Total de Reservas ===
            cur.execute("SELECT COUNT(*) FROM reservas")
            kpis["total_reservas"] = cur.fetchone()[0] or 0

            # === Total de Clientes ===
            cur.execute("SELECT COUNT(*) FROM clientes")
            kpis["total_clientes"] = cur.fetchone()[0] or 0

            # === Ingresos por hospedaje ===
            cur.execute("SELECT IFNULL(SUM(total), 0) FROM facturacion WHERE estado='Pagado'")
            kpis["ingresos_hospedaje"] = float(cur.fetchone()[0] or 0)

            # === Ingresos por servicios ===
            cur.execute("SELECT IFNULL(SUM(subtotal), 0) FROM reserva_servicio WHERE estado='Pagado'")
            kpis["ingresos_servicios"] = float(cur.fetchone()[0] or 0)

            # === Total de Incidencias ===
            cur.execute("SELECT COUNT(*) FROM incidencias")
            kpis["total_incidencias"] = cur.fetchone()[0] or 0

            # === Ocupación general (todas las reservas) ===
            cur.execute("""
                SELECT estado, COUNT(*) AS cantidad
                FROM reservas
                GROUP BY estado
                ORDER BY cantidad DESC
            """)
            ocupacion = [{"estado": r[0], "cantidad": r[1]} for r in cur.fetchall()]

            # === Ingresos mensuales combinados (hospedaje + servicios) ===
            cur.execute("""
                SELECT DATE_FORMAT(fecha_emision, '%b') AS mes, SUM(total) AS total
                FROM facturacion
                WHERE estado='Pagado'
                GROUP BY MONTH(fecha_emision)
                ORDER BY MONTH(fecha_emision)
            """)
            ingresos_fact = cur.fetchall()

            cur.execute("""
                SELECT DATE_FORMAT(fecha, '%b') AS mes, SUM(subtotal) AS total
                FROM reserva_servicio
                WHERE estado='Pagado'
                GROUP BY MONTH(fecha)
                ORDER BY MONTH(fecha)
            """)
            ingresos_serv = cur.fetchall()

            # Combinar resultados mensuales
            meses = {}
            for m, total in ingresos_fact + ingresos_serv:
                meses[m] = meses.get(m, 0) + float(total or 0)
            ingresos_mensuales = [{"mes": m, "total": t} for m, t in meses.items()]

            # === Últimas Actividades ===
            cur.execute("""
                SELECT a.accion, h.numero AS habitacion, a.nuevo_estado_hab,
                       DATE_FORMAT(a.fecha_hora, '%d/%m/%Y %H:%i') AS fecha
                FROM actividad a
                LEFT JOIN habitaciones h ON a.id_habitacion = h.id_habitacion
                ORDER BY a.fecha_hora DESC
                LIMIT 8
            """)
            ult_actividades = [
                {"accion": a[0], "habitacion": a[1], "nuevo_estado": a[2], "fecha": a[3]}
                for a in cur.fetchall()
            ]

    except Exception as e:
        print(f"❌ Error al cargar reportes: {e}")
        flash("Error al cargar los reportes administrativos.", "error")

    finally:
        if 'con' in locals():
            con.close()

    return render_template(
        "reportes_adm.html",
        kpis=kpis,
        ocupacion=ocupacion,
        ingresos_mensuales=ingresos_mensuales,
        ult_actividades=ult_actividades
    )

# ============================================================
# 🔍 FILTRO DINÁMICO POR MES (AJAX)
# ============================================================
@reportes_bp.route("/filtrar_mes", methods=["POST"])
def filtrar_mes():
    data = request.get_json() or {}
    mes_str = data.get("mes")  # Formato YYYY-MM

    if not mes_str:
        return jsonify({"error": "Mes no especificado"}), 400

    try:
        anio, mes = map(int, mes_str.split("-"))
    except ValueError:
        return jsonify({"error": "Formato de mes inválido"}), 400

    resultados = {"ocupacion": [], "ingresos": []}

    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            # === Ocupación por estado (solo reservas válidas) ===
            # === Ocupación por estado (solo reservas válidas) ===
            cur.execute("""
                SELECT estado, COUNT(*) AS cantidad
                FROM reservas
                WHERE YEAR(fecha_reserva) = %s AND MONTH(fecha_reserva) = %s
                GROUP BY estado
            """, (anio, mes))
            resultados["ocupacion"] = [
                {"estado": r["estado"] or "Sin estado", "cantidad": r["cantidad"] or 0}
                for r in cur.fetchall()
            ]

            # === Ingresos hospedaje ===
            cur.execute("""
                SELECT IFNULL(SUM(total), 0) AS total
                FROM facturacion
                WHERE estado = 'Pagado'
                AND YEAR(fecha_emision) = %s
                AND MONTH(fecha_emision) = %s
            """, (anio, mes))
            ingresos_hospedaje = float(cur.fetchone()["total"] or 0)

            # === Ingresos servicios ===
            cur.execute("""
                SELECT IFNULL(SUM(subtotal), 0) AS total
                FROM reserva_servicio
                WHERE estado = 'Pagado'
                AND fecha IS NOT NULL
                AND YEAR(fecha) = %s
                AND MONTH(fecha) = %s
            """, (anio, mes))
            ingresos_servicios = float(cur.fetchone()["total"] or 0)


            resultados["ingresos"] = [
                {"categoria": "Hospedaje", "total": ingresos_hospedaje},
                {"categoria": "Servicios", "total": ingresos_servicios},
                {"categoria": "Total", "total": ingresos_hospedaje + ingresos_servicios},
            ]

    except Exception as e:
        import traceback
        print("❌ ERROR DETALLADO EN /filtrar_mes:")
        traceback.print_exc()  # muestra el error completo con línea exacta
        return jsonify({"error": str(e)}), 500
    
    finally:
        if 'con' in locals():
            con.close()

    return jsonify(resultados)


# ============================================================
# 🔍 API: FILTRO GENERAL DE REPORTES
# ============================================================
@reportes_bp.route("/filtrar", methods=["POST"])
def filtrar_reportes():
    data = request.get_json() or {}
    tipo = data.get("tipo")
    estado = data.get("estado")
    fecha_inicio = data.get("fecha_inicio")
    fecha_fin = data.get("fecha_fin")

    resultados = []
    con = obtener_conexion()

    try:
        with con.cursor() as cur:
            if tipo == "reservas":
                query = """
                    SELECT r.id_reserva, c.nombres, h.numero, r.estado,
                           DATE(r.fecha_reserva), r.total
                    FROM reservas r
                    LEFT JOIN clientes c ON r.id_cliente = c.id_cliente
                    LEFT JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
                    WHERE 1=1
                """
                params = []
                if estado:
                    query += " AND r.estado=%s"
                    params.append(estado)
                if fecha_inicio and fecha_fin:
                    query += " AND DATE(r.fecha_reserva) BETWEEN %s AND %s"
                    params.extend([fecha_inicio, fecha_fin])
                cur.execute(query, tuple(params))
                reservas = [
                    {"ID": r[0], "Cliente": r[1], "Habitación": r[2], "Estado": r[3], "Fecha": str(r[4]), "Total": float(r[5])}
                    for r in cur.fetchall()
                ]

                # Incluir también servicios reservados
                cur.execute("""
                    SELECT rs.id_reserva_servicio, c.nombres, s.nombre, rs.estado,
                           rs.fecha, rs.subtotal
                    FROM reserva_servicio rs
                    LEFT JOIN clientes c ON rs.id_cliente = c.id_cliente
                    LEFT JOIN servicios s ON rs.id_servicio = s.id_servicio
                    WHERE 1=1
                """)
                servicios = [
                    {"ID": f"S-{r[0]}", "Cliente": r[1], "Servicio": r[2], "Estado": r[3], "Fecha": str(r[4]), "Total": float(r[5])}
                    for r in cur.fetchall()
                ]

                resultados = reservas + servicios

            elif tipo == "facturacion":
                query = """
                    SELECT f.id_factura, u.nombres, f.fecha_emision, f.total, f.estado
                    FROM facturacion f
                    LEFT JOIN usuarios u ON f.id_usuario = u.id_usuario
                    WHERE 1=1
                """
                params = []
                if estado:
                    query += " AND f.estado=%s"
                    params.append(estado)
                if fecha_inicio and fecha_fin:
                    query += " AND f.fecha_emision BETWEEN %s AND %s"
                    params.extend([fecha_inicio, fecha_fin])
                cur.execute(query, tuple(params))
                resultados = [
                    {"ID": r[0], "Usuario": r[1], "Fecha": str(r[2]), "Total": float(r[3]), "Estado": r[4]}
                    for r in cur.fetchall()
                ]

            elif tipo == "habitaciones":
                query = """
                    SELECT h.numero, t.nombre, t.precio_base, h.estado
                    FROM habitaciones h
                    LEFT JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                    WHERE 1=1
                """
                params = []
                if estado:
                    query += " AND h.estado=%s"
                    params.append(estado)
                cur.execute(query, tuple(params))
                resultados = [
                    {"Habitación": r[0], "Tipo": r[1], "Precio Base": float(r[2]), "Estado": r[3]}
                    for r in cur.fetchall()
                ]

            elif tipo == "clientes":
                cur.execute("SELECT id_cliente, nombres, apellidos, correo, telefono FROM clientes")
                resultados = [
                    {"ID": r[0], "Nombres": r[1], "Apellidos": r[2], "Correo": r[3], "Teléfono": r[4]}
                    for r in cur.fetchall()
                ]

            elif tipo == "incidencias":
                query = """
                    SELECT i.id_incidencia, h.numero, i.descripcion, i.estado, i.prioridad, i.fecha_reporte
                    FROM incidencias i
                    LEFT JOIN habitaciones h ON i.id_habitacion = h.id_habitacion
                    WHERE 1=1
                """
                params = []
                if estado:
                    query += " AND i.estado=%s"
                    params.append(estado)
                if fecha_inicio and fecha_fin:
                    query += " AND i.fecha_reporte BETWEEN %s AND %s"
                    params.extend([fecha_inicio, fecha_fin])
                cur.execute(query, tuple(params))
                resultados = [
                    {"ID": r[0], "Habitación": r[1], "Descripción": r[2], "Estado": r[3], "Prioridad": r[4], "Fecha": str(r[5])}
                    for r in cur.fetchall()
                ]

    except Exception as e:
        print(f"❌ Error en filtro de reportes: {e}")

    finally:
        con.close()

    return jsonify(resultados)
