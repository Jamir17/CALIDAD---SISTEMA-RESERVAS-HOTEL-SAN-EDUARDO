# controlador_reportes.py
# =========================
# Controlador de reportes - Hotel San Eduardo
# =========================

from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, flash
from bd import obtener_conexion
from datetime import datetime
import traceback

reportes_bp = Blueprint("reportes", __name__, url_prefix="/admin/reportes")

# --- utilidades para soportar cursores que devuelven tuplas o dicts ---
def _is_dict_row(r): 
    return isinstance(r, dict)
def _get(r, key, default=None):
    if r is None: return default
    if _is_dict_row(r): return r.get(key, default)
    try:
        return r[key]
    except Exception:
        return default

# --- función central que obtiene TODOS los datos del reporte ---
def get_report_data(mes_str=None):
    """
    Retorna un dict con la misma estructura que /data necesita.
    mes_str: 'YYYY-MM' o None (para últimos 12 meses)
    """
    anio = mes = None
    if mes_str:
        try:
            anio, mes = map(int, mes_str.split("-"))
        except Exception:
            # formato inválido -> ignoramos y devolvemos último año
            anio = mes = None

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
            # KPIs básicos
            cur.execute("SELECT COUNT(*) AS cnt FROM reservas")
            row = cur.fetchone()
            resultados["kpis"]["total_reservas"] = int(_get(row,"cnt", _get(row,0,0)) or 0)

            cur.execute("SELECT COUNT(*) AS cnt FROM clientes")
            row = cur.fetchone()
            resultados["kpis"]["total_clientes"] = int(_get(row,"cnt", _get(row,0,0)) or 0)

            # Ingresos hospedaje (facturacion) solo 'Pagado'
            cur.execute("SELECT IFNULL(SUM(total),0) AS total FROM facturacion WHERE estado='Pagado'")
            row = cur.fetchone()
            resultados["kpis"]["ingresos_hospedaje"] = float(_get(row,"total", _get(row,0,0)) or 0)

            # Ingresos servicios: sumar reserva_servicio.subtotal excluyendo 'Cancelado'
            # Ajusta este filtro si tu lógica de "pagado" es distinta.
            cur.execute("SELECT IFNULL(SUM(subtotal),0) AS total FROM reserva_servicio WHERE estado <> 'Cancelado'")
            row = cur.fetchone()
            resultados["kpis"]["ingresos_servicios"] = float(_get(row,"total", _get(row,0,0)) or 0)

            resultados["kpis"]["ganancias_totales"] = round(resultados["kpis"]["ingresos_hospedaje"] + resultados["kpis"]["ingresos_servicios"], 2)

            # ingresos mensuales combinados (hospedaje + servicios)
            if anio and mes:
                # consultas por mes específico
                cur.execute("""
                    SELECT DATE_FORMAT(fecha_emision, '%%b %%Y') AS mes, IFNULL(SUM(total),0) AS total
                    FROM facturacion
                    WHERE estado='Pagado' AND YEAR(fecha_emision)=%s AND MONTH(fecha_emision)=%s
                    GROUP BY YEAR(fecha_emision), MONTH(fecha_emision)
                """, (anio, mes))
                fact = cur.fetchall()

                cur.execute("""
                    SELECT DATE_FORMAT(fecha, '%%b %%Y') AS mes, IFNULL(SUM(subtotal),0) AS total
                    FROM reserva_servicio
                    WHERE estado <> 'Cancelado' AND fecha IS NOT NULL AND YEAR(fecha)=%s AND MONTH(fecha)=%s
                    GROUP BY YEAR(fecha), MONTH(fecha)
                """, (anio, mes))
                serv = cur.fetchall()
            else:
                # últimos 12 meses (para mostrar histórico)
                cur.execute("""
                    SELECT DATE_FORMAT(fecha_emision, '%%b %%Y') AS mes, IFNULL(SUM(total),0) AS total,
                           YEAR(fecha_emision) AS yy, MONTH(fecha_emision) AS mm
                    FROM facturacion
                    WHERE estado='Pagado' AND fecha_emision >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                    GROUP BY YEAR(fecha_emision), MONTH(fecha_emision)
                    ORDER BY YEAR(fecha_emision), MONTH(fecha_emision)
                """)
                fact = cur.fetchall()

                cur.execute("""
                    SELECT DATE_FORMAT(fecha, '%%b %%Y') AS mes, IFNULL(SUM(subtotal),0) AS total,
                           YEAR(fecha) AS yy, MONTH(fecha) AS mm
                    FROM reserva_servicio
                    WHERE fecha IS NOT NULL AND estado <> 'Cancelado' AND fecha >= DATE_SUB(CURDATE(), INTERVAL 12 MONTH)
                    GROUP BY YEAR(fecha), MONTH(fecha)
                    ORDER BY YEAR(fecha), MONTH(fecha)
                """)
                serv = cur.fetchall()

            # combinar por par (yy,mm) -> mes label + suma total
            meses = {}
            if fact:
                for r in fact:
                    yy = _get(r,"yy", _get(r,2, None))
                    mm = _get(r,"mm", _get(r,3, None))
                    label = _get(r,"mes", _get(r,0, ""))
                    key = (yy, mm, label)
                    meses[key] = meses.get(key, 0) + float(_get(r,"total", _get(r,1,0)) or 0)
            if serv:
                for r in serv:
                    yy = _get(r,"yy", _get(r,2, None))
                    mm = _get(r,"mm", _get(r,3, None))
                    label = _get(r,"mes", _get(r,0, ""))
                    key = (yy, mm, label)
                    meses[key] = meses.get(key, 0) + float(_get(r,"total", _get(r,1,0)) or 0)

            resultados["ingresos_mensuales"] = [{"mes": k[2], "total": meses[k]} for k in sorted(meses.keys())]

            # reservas por estado
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
            resultados["reservas_estado"] = [{"estado": _get(r,"estado", _get(r,0,"")), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or [])]

            # top habitaciones por ingresos (facturacion -> reservas -> habitaciones)
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
            resultados["top_habitaciones"] = [{"numero": _get(r,"numero", _get(r,0,"—")), "total": float(_get(r,"total", _get(r,1,0)) or 0)} for r in (filas or [])]

            # servicios: cantidad (veces reservadas) + total (suma subtotal)
            cur.execute("""
                SELECT s.nombre, COUNT(rs.id_reserva_servicio) AS cantidad, IFNULL(SUM(rs.subtotal),0) AS total
                FROM reserva_servicio rs
                LEFT JOIN servicios s ON rs.id_servicio = s.id_servicio
                WHERE rs.estado <> 'Cancelado'
                GROUP BY rs.id_servicio, s.nombre
                ORDER BY cantidad DESC
            """)
            filas = cur.fetchall()
            resultados["servicios"] = [{"nombre": _get(r,"nombre", _get(r,0,"")), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0), "total": float(_get(r,"total", _get(r,2,0)) or 0)} for r in (filas or [])]

            # ingresos por tipo de pago (facturacion)
            cur.execute("""
                SELECT tp.descripcion AS metodo, IFNULL(SUM(f.total),0) AS total
                FROM facturacion f
                LEFT JOIN tipo_pago tp ON f.id_tipo_pago = tp.id_tipo_pago
                WHERE f.estado='Pagado'
                GROUP BY f.id_tipo_pago, tp.descripcion
            """)
            filas = cur.fetchall()
            resultados["ingresos_por_pago"] = [{"metodo": _get(r,"metodo", _get(r,0,"")), "total": float(_get(r,"total", _get(r,1,0)) or 0)} for r in (filas or [])]

            # reservas por dia (últimos 30 días)
            cur.execute("""
                SELECT DATE(fecha_reserva) AS fecha, COUNT(*) AS cantidad
                FROM reservas
                WHERE fecha_reserva >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(fecha_reserva)
                ORDER BY DATE(fecha_reserva)
            """)
            filas = cur.fetchall()
            resultados["reservas_por_dia"] = [{"fecha": str(_get(r,"fecha", _get(r,0,""))), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or [])]

            # notificaciones por dia
            cur.execute("""
                SELECT DATE(fecha_envio) AS fecha, COUNT(*) AS cantidad
                FROM historial_notificaciones
                WHERE fecha_envio >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(fecha_envio)
                ORDER BY DATE(fecha_envio)
            """)
            filas = cur.fetchall()
            resultados["notificaciones_por_dia"] = [{"fecha": str(_get(r,"fecha", _get(r,0,""))), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or [])]

            # cancelaciones por dia (últimos 30 días)
            cur.execute("""
                SELECT DATE(fecha_cancelacion) AS fecha, COUNT(*) AS cantidad
                FROM reservas
                WHERE estado='Cancelada' AND fecha_cancelacion >= DATE_SUB(CURDATE(), INTERVAL 30 DAY)
                GROUP BY DATE(fecha_cancelacion)
                ORDER BY DATE(fecha_cancelacion)
            """)
            filas = cur.fetchall()
            resultados["cancelaciones_por_dia"] = [{"fecha": str(_get(r,"fecha", _get(r,0,""))), "cantidad": int(_get(r,"cantidad", _get(r,1,0)) or 0)} for r in (filas or [])]

            # valoracion promedio
            cur.execute("SELECT IFNULL(AVG(puntuacion),0) AS avg_p FROM valoraciones")
            row = cur.fetchone()
            resultados["valoracion_promedio"] = float(_get(row,"avg_p", _get(row,0,0)) or 0)

    except Exception as e:
        # imprimimos traza para debugging (en dev), devolveremos error en endpoint si corresponde
        print("ERROR get_report_data:", e)
        traceback.print_exc()
        raise
    finally:
        if con:
            con.close()

    return resultados


# === ruta principal: renderiza template con initialReportData pre-cargado ===
@reportes_bp.route("/", endpoint="reportes_admin")
def panel_reportes():
    if not session.get("usuario_id"):
        return redirect(url_for("usuarios.iniciosesion"))

    try:
        # usamos la misma función para obtener datos iniciales (últimos 12 meses)
        report_data = get_report_data(None)

        # Además queremos enviar algunos objetos para mostrar en servidor (ult_facturas)
        con = obtener_conexion()
        ult_facturas = []
        with con.cursor() as cur:
            cur.execute("SELECT id_factura, fecha_emision, total, estado FROM facturacion ORDER BY fecha_emision DESC LIMIT 20")
            filas = cur.fetchall()
            for f in filas:
                ult_facturas.append({
                    "id_factura": _get(f,"id_factura", _get(f,0)),
                    "fecha_emision": _get(f,"fecha_emision", _get(f,1)),
                    "total": float(_get(f,"total", _get(f,2,0)) or 0),
                    "estado": _get(f,"estado", _get(f,3,""))
                })
        con.close()

        current_month = datetime.now().strftime("%Y-%m")
        return render_template("reportes_adm.html",
                               kpis=report_data["kpis"],
                               ult_facturas=ult_facturas,
                               report_data=report_data,
                               current_month=current_month)
    except Exception as e:
        print("❌ Error al cargar panel:", e)
        traceback.print_exc()
        flash("Error al cargar reportes (ver consola)", "error")
        # renderizamos pero con datos vacíos para evitar 500 en producción
        return render_template("reportes_adm.html",
                               kpis={"total_reservas":0,"total_clientes":0,"ingresos_hospedaje":0,"ingresos_servicios":0,"ganancias_totales":0},
                               ult_facturas=[],
                               report_data={"kpis":{},"ingresos_mensuales":[], "reservas_estado":[], "top_habitaciones":[], "servicios":[], "ingresos_por_pago":[], "reservas_por_dia":[], "notificaciones_por_dia":[], "cancelaciones_por_dia":[], "valoracion_promedio":0},
                               current_month=datetime.now().strftime("%Y-%m")
                               )

# === endpoint que devuelve JSON usado por el JS (POST /admin/reportes/data) ===
@reportes_bp.route("/data", methods=["POST"])
def data():
    payload = request.get_json() or {}
    mes = payload.get("mes")
    try:
        resultados = get_report_data(mes)
        return jsonify(resultados)
    except Exception as e:
        print("❌ ERROR en /data:", e)
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
