# controlador_reportes.py (versión corregida y robusta)
# ============================================================
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from bd import obtener_conexion
from datetime import datetime
import traceback

reportes_bp = Blueprint("reportes", __name__, url_prefix="/admin/reportes")

# helpers para filas dict/tupla
def _is_dict_row(r): return isinstance(r, dict)
def _get(r, key, default=None):
    if r is None: return default
    if _is_dict_row(r): return r.get(key, default)
    try: return r[key]
    except Exception: return default

# función que obtiene todos los datos del reporte (reutilizable)
def get_report_data(mes_str=None):
    """
    mes_str: 'YYYY-MM' o None
    devuelve dict con: kpis, ingresos_mensuales, reservas_estado, top_habitaciones, servicios, ingresos_por_pago,
                       reservas_por_dia, notificaciones_por_dia, cancelaciones_por_dia, valoracion_promedio
    """
    anio = mes = None
    if mes_str:
        try:
            anio, mes = map(int, mes_str.split("-"))
        except Exception:
            raise ValueError("Formato de mes inválido (esperado YYYY-MM)")

    resultados = {
        "kpis": {},
        "ingresos_mensuales": [],
        "reservas_estado": [],
        "top_habitaciones": [],
        "servicios": [],
        "ingresos_por_pago": [],
        "reservas_por_dia": [],
        "notificaciones_por_dia": [],
        "cancelaciones_por_dia": [],
        "valoracion_promedio": 0.0
    }

    con = None
    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            # KPIs básicos (reservas: se filtra por mes si aplica)
            if anio and mes:
                cur.execute("SELECT COUNT(*) AS cnt FROM reservas WHERE YEAR(fecha_reserva)=%s AND MONTH(fecha_reserva)=%s", (anio, mes))
            else:
                cur.execute("SELECT COUNT(*) AS cnt FROM reservas")
            row = cur.fetchone()
            resultados["kpis"]["total_reservas"] = int(_get(row,"cnt", _get(row,0,0)) or 0)

            # clientes: total global (normalmente queremos total de clientes registrados)
            cur.execute("SELECT COUNT(*) AS cnt FROM clientes")
            row = cur.fetchone()
            resultados["kpis"]["total_clientes"] = int(_get(row,"cnt", _get(row,0,0)) or 0)

            # ingresos hospedaje (facturacion) solo 'Pagado' (filtrar por mes si aplica)
            if anio and mes:
                cur.execute("SELECT IFNULL(SUM(total),0) AS total FROM facturacion WHERE estado='Pagado' AND YEAR(fecha_emision)=%s AND MONTH(fecha_emision)=%s", (anio, mes))
            else:
                cur.execute("SELECT IFNULL(SUM(total),0) AS total FROM facturacion WHERE estado='Pagado'")
            row = cur.fetchone()
            ingresos_hosp = float(_get(row,"total", _get(row,0,0)) or 0)
            resultados["kpis"]["ingresos_hospedaje"] = ingresos_hosp

            # ingresos servicios: sumar subtotal desde reserva_servicio
            # Usamos columna 'fecha' de reserva_servicio para filtrar por mes cuando exista
            if anio and mes:
                cur.execute("SELECT IFNULL(SUM(subtotal),0) AS total FROM reserva_servicio WHERE fecha IS NOT NULL AND YEAR(fecha)=%s AND MONTH(fecha)=%s", (anio, mes))
            else:
                cur.execute("SELECT IFNULL(SUM(subtotal),0) AS total FROM reserva_servicio")
            row = cur.fetchone()
            ingresos_serv = float(_get(row,"total", _get(row,0,0)) or 0)
            resultados["kpis"]["ingresos_servicios"] = ingresos_serv

            # KPI nuevo: ganancias totales
            resultados["kpis"]["ganancias_totales"] = ingresos_hosp + ingresos_serv

            # ingresos mensuales (combina facturacion + reserva_servicio)
            if anio and mes:
                cur.execute("""
                    SELECT DATE_FORMAT(MIN(fecha_emision),'%%b %%Y') AS mes_label,
                           IFNULL(SUM(total),0) AS total,
                           YEAR(fecha_emision) AS yy, MONTH(fecha_emision) AS mm
                    FROM facturacion
                    WHERE estado='Pagado' AND YEAR(fecha_emision)=%s AND MONTH(fecha_emision)=%s
                    GROUP BY YEAR(fecha_emision), MONTH(fecha_emision)
                    ORDER BY yy, mm
                """, (anio, mes))
                fact = cur.fetchall()

                cur.execute("""
                    SELECT DATE_FORMAT(MIN(fecha),'%%b %%Y') AS mes_label,
                           IFNULL(SUM(subtotal),0) AS total,
                           YEAR(fecha) AS yy, MONTH(fecha) AS mm
                    FROM reserva_servicio
                    WHERE fecha IS NOT NULL AND YEAR(fecha)=%s AND MONTH(fecha)=%s
                    GROUP BY YEAR(fecha), MONTH(fecha)
                    ORDER BY yy, mm
                """, (anio, mes))
                serv = cur.fetchall()
            else:
                cur.execute("""
                    SELECT DATE_FORMAT(MIN(fecha_emision),'%%b %%Y') AS mes_label,
                           IFNULL(SUM(total),0) AS total,
                           YEAR(fecha_emision) AS yy, MONTH(fecha_emision) AS mm
                    FROM facturacion
                    WHERE estado='Pagado' AND fecha_emision >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                    GROUP BY YEAR(fecha_emision), MONTH(fecha_emision)
                    ORDER BY yy, mm
                """)
                fact = cur.fetchall()

                cur.execute("""
                    SELECT DATE_FORMAT(MIN(fecha),'%%b %%Y') AS mes_label,
                           IFNULL(SUM(subtotal),0) AS total,
                           YEAR(fecha) AS yy, MONTH(fecha) AS mm
                    FROM reserva_servicio
                    WHERE fecha IS NOT NULL AND fecha >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                    GROUP BY YEAR(fecha), MONTH(fecha)
                    ORDER BY yy, mm
                """)
                serv = cur.fetchall()

            meses = {}
            for r in (fact or []):
                key = ( _get(r,"yy", _get(r,2,"")), _get(r,"mm", _get(r,3,"")), _get(r,"mes_label", _get(r,0,"")) )
                meses[key] = meses.get(key, 0) + float(_get(r,"total", _get(r,1,0)) or 0)
            for r in (serv or []):
                key = ( _get(r,"yy", _get(r,2,"")), _get(r,"mm", _get(r,3,"")), _get(r,"mes_label", _get(r,0,"")) )
                meses[key] = meses.get(key, 0) + float(_get(r,"total", _get(r,1,0)) or 0)

            resultados["ingresos_mensuales"] = [{"mes": k[2], "total": meses[k]} for k in sorted(meses.keys())]

            # reservas por estado (filtrar por mes si aplica)
            if anio and mes:
                cur.execute("""
                    SELECT estado, COUNT(*) AS cantidad
                    FROM reservas
                    WHERE YEAR(fecha_reserva)=%s AND MONTH(fecha_reserva)=%s
                    GROUP BY estado
                """, (anio, mes))
            else:
                cur.execute("SELECT estado, COUNT(*) AS cantidad FROM reservas GROUP BY estado")
            filas = cur.fetchall()
            resultados["reservas_estado"] = [ {"estado": _get(r,"estado", _get(r,0,"")), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or []) ]

            # top habitaciones por ingresos (filtrar por mes si aplica)
            if anio and mes:
                cur.execute("""
                    SELECT h.numero, IFNULL(SUM(f.total),0) AS total
                    FROM facturacion f
                    LEFT JOIN reservas r ON f.id_reserva = r.id_reserva
                    LEFT JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
                    WHERE f.estado='Pagado' AND YEAR(f.fecha_emision)=%s AND MONTH(f.fecha_emision)=%s
                    GROUP BY h.id_habitacion, h.numero
                    ORDER BY total DESC
                    LIMIT 8
                """, (anio, mes))
            else:
                cur.execute("""
                    SELECT h.numero, IFNULL(SUM(f.total),0) AS total
                    FROM facturacion f
                    LEFT JOIN reservas r ON f.id_reserva = r.id_reserva
                    LEFT JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
                    WHERE f.estado='Pagado'
                    GROUP BY h.id_habitacion, h.numero
                    ORDER BY total DESC
                    LIMIT 8
                """)
            filas = cur.fetchall()
            resultados["top_habitaciones"] = [ {"numero": _get(r,"numero", _get(r,0,"—")), "total": float(_get(r,"total", _get(r,1,0)) or 0)} for r in (filas or []) ]

            # servicios (cantidad + total) — filtrar por mes si aplica (usando rs.fecha)
            if anio and mes:
                cur.execute("""
                    SELECT s.nombre, COUNT(rs.id_reserva_servicio) AS cantidad, IFNULL(SUM(rs.subtotal),0) AS total
                    FROM reserva_servicio rs
                    LEFT JOIN servicios s ON rs.id_servicio = s.id_servicio
                    WHERE rs.fecha IS NOT NULL AND YEAR(rs.fecha)=%s AND MONTH(rs.fecha)=%s
                    GROUP BY rs.id_servicio, s.nombre
                    ORDER BY cantidad DESC
                """, (anio, mes))
            else:
                cur.execute("""
                    SELECT s.nombre, COUNT(rs.id_reserva_servicio) AS cantidad, IFNULL(SUM(rs.subtotal),0) AS total
                    FROM reserva_servicio rs
                    LEFT JOIN servicios s ON rs.id_servicio = s.id_servicio
                    GROUP BY rs.id_servicio, s.nombre
                    ORDER BY cantidad DESC
                """)
            filas = cur.fetchall()
            resultados["servicios"] = [ {"nombre": _get(r,"nombre", _get(r,0,"")), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0), "total": float(_get(r,"total", _get(r,2,0)) or 0)} for r in (filas or []) ]

            # ingresos por tipo de pago (desde facturacion) — filtrar por mes si aplica
            if anio and mes:
                cur.execute("""
                    SELECT tp.descripcion AS metodo, IFNULL(SUM(f.total),0) AS total
                    FROM facturacion f
                    LEFT JOIN tipo_pago tp ON f.id_tipo_pago = tp.id_tipo_pago
                    WHERE YEAR(f.fecha_emision)=%s AND MONTH(f.fecha_emision)=%s
                    GROUP BY f.id_tipo_pago, tp.descripcion
                """, (anio, mes))
            else:
                cur.execute("""
                    SELECT tp.descripcion AS metodo, IFNULL(SUM(f.total),0) AS total
                    FROM facturacion f
                    LEFT JOIN tipo_pago tp ON f.id_tipo_pago = tp.id_tipo_pago
                    GROUP BY f.id_tipo_pago, tp.descripcion
                """)
            filas = cur.fetchall()
            resultados["ingresos_por_pago"] = [ {"metodo": _get(r,"metodo", _get(r,0,"")), "total": float(_get(r,"total", _get(r,1,0)) or 0)} for r in (filas or []) ]

            # reservas por día (últimos 30 o por mes)
            if anio and mes:
                cur.execute("""
                    SELECT DATE(r.fecha_reserva) AS fecha, COUNT(*) AS cantidad
                    FROM reservas r
                    WHERE YEAR(r.fecha_reserva)=%s AND MONTH(r.fecha_reserva)=%s
                    GROUP BY DATE(r.fecha_reserva)
                    ORDER BY DATE(r.fecha_reserva)
                """, (anio, mes))
            else:
                cur.execute("""
                    SELECT DATE(r.fecha_reserva) AS fecha, COUNT(*) AS cantidad
                    FROM reservas r
                    WHERE r.fecha_reserva >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(r.fecha_reserva)
                    ORDER BY DATE(r.fecha_reserva)
                """)
            filas = cur.fetchall()
            resultados["reservas_por_dia"] = [ {"fecha": str(_get(r,"fecha", _get(r,0,""))), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or []) ]

            # notificaciones por dia (últimos 30 o por mes)
            if anio and mes:
                cur.execute("""
                    SELECT DATE(fecha_envio) AS fecha, COUNT(*) AS cantidad
                    FROM historial_notificaciones
                    WHERE YEAR(fecha_envio)=%s AND MONTH(fecha_envio)=%s
                    GROUP BY DATE(fecha_envio)
                    ORDER BY DATE(fecha_envio)
                """, (anio, mes))
            else:
                cur.execute("""
                    SELECT DATE(fecha_envio) AS fecha, COUNT(*) AS cantidad
                    FROM historial_notificaciones
                    WHERE fecha_envio >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(fecha_envio)
                    ORDER BY DATE(fecha_envio)
                """)
            filas = cur.fetchall()
            resultados["notificaciones_por_dia"] = [ {"fecha": str(_get(r,"fecha", _get(r,0,""))), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or []) ]

            # cancelaciones por dia (filtrar por mes si aplica)
            if anio and mes:
                cur.execute("""
                    SELECT DATE(fecha_cancelacion) AS fecha, COUNT(*) AS cantidad
                    FROM reservas
                    WHERE estado='Cancelada' AND YEAR(fecha_cancelacion)=%s AND MONTH(fecha_cancelacion)=%s
                    GROUP BY DATE(fecha_cancelacion)
                    ORDER BY DATE(fecha_cancelacion)
                """, (anio, mes))
            else:
                cur.execute("""
                    SELECT DATE(fecha_cancelacion) AS fecha, COUNT(*) AS cantidad
                    FROM reservas
                    WHERE estado='Cancelada' AND fecha_cancelacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                    GROUP BY DATE(fecha_cancelacion)
                    ORDER BY DATE(fecha_cancelacion)
                """)
            filas = cur.fetchall()
            resultados["cancelaciones_por_dia"] = [ {"fecha": str(_get(r,"fecha", _get(r,0,""))), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or []) ]

            # valoracion promedio (filtrar por mes si aplica)
            if anio and mes:
                cur.execute("SELECT IFNULL(AVG(puntuacion),0) AS avg_p FROM valoraciones WHERE YEAR(fecha_valoracion)=%s AND MONTH(fecha_valoracion)=%s", (anio, mes))
            else:
                cur.execute("SELECT IFNULL(AVG(puntuacion),0) AS avg_p FROM valoraciones")
            row = cur.fetchone()
            resultados["valoracion_promedio"] = float(_get(row,"avg_p", _get(row,0,0)) or 0)

    except Exception as e:
        # reenviar excepción para que el caller la maneje (o loguearla)
        raise
    finally:
        if con:
            con.close()

    return resultados

# ================= render principal =================
@reportes_bp.route("/", endpoint="reportes_admin")
def panel_reportes():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    try:
        # pedimos datos iniciales (sin filtro de mes)
        report_data = get_report_data(None)
        kpis = report_data["kpis"]
        ocupacion = report_data.get("reservas_estado", [])
        ingresos_mensuales = report_data.get("ingresos_mensuales", [])
        ult_actividades = []
        ult_facturas = []

        # también traemos últimas actividades y facturas separadas (porque antes se mostraban)
        con = obtener_conexion()
        with con.cursor() as cur:
            cur.execute("""
                SELECT a.accion, h.numero AS habitacion, a.nuevo_estado_hab,
                       DATE_FORMAT(a.fecha_hora, '%%d/%%m/%%Y %%H:%%i') AS fecha
                FROM actividad a
                LEFT JOIN habitaciones h ON a.id_habitacion = h.id_habitacion
                ORDER BY a.fecha_hora DESC LIMIT 8
            """)
            filas = cur.fetchall()
            for a in filas:
                if _is_dict_row(a):
                    ult_actividades.append({"accion": _get(a,"accion"), "habitacion": _get(a,"habitacion"), "nuevo_estado": _get(a,"nuevo_estado_hab"), "fecha": _get(a,"fecha")})
                else:
                    ult_actividades.append({"accion": a[0], "habitacion": a[1], "nuevo_estado": a[2], "fecha": a[3]})

            cur.execute("SELECT id_factura, fecha_emision, total, estado FROM facturacion ORDER BY fecha_emision DESC LIMIT 20")
            filas = cur.fetchall()
            for f in filas:
                if _is_dict_row(f):
                    ult_facturas.append({"id_factura": _get(f,"id_factura"), "fecha_emision": _get(f,"fecha_emision"), "total": float(_get(f,"total") or 0), "estado": _get(f,"estado")})
                else:
                    ult_facturas.append({"id_factura": f[0], "fecha_emision": f[1], "total": float(f[2] or 0), "estado": f[3]})
    except Exception as e:
        print("❌ Error al cargar panel:", e)
        traceback.print_exc()
        flash("Error al cargar reportes", "error")
        # valores por defecto vacíos para que la vista cargue
        kpis = {"total_reservas": 0, "total_clientes": 0, "ingresos_hospedaje": 0.0, "ingresos_servicios": 0.0, "ganancias_totales": 0.0}
        ocupacion = []
        ingresos_mensuales = []
        ult_actividades = []
        ult_facturas = []
        report_data = {"kpis": kpis, "reservas_estado": ocupacion, "ingresos_mensuales": ingresos_mensuales}

    current_month = datetime.now().strftime("%Y-%m")

    return render_template("reportes_adm.html",
                           kpis=kpis,
                           ocupacion=ocupacion,
                           ingresos_mensuales=ingresos_mensuales,
                           ult_actividades=ult_actividades,
                           ult_facturas=ult_facturas,
                           report_data=report_data,
                           current_month=current_month)

# ================= endpoint /data =================
@reportes_bp.route("/data", methods=["POST"])
def data():
    payload = request.get_json() or {}
    mes_str = payload.get("mes")
    try:
        resultados = get_report_data(mes_str)
    except ValueError as ve:
        return jsonify({"error": str(ve)}), 400
    except Exception as e:
        print("❌ ERROR en /data:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

    return jsonify(resultados)
# ================== fin archivo ==================
