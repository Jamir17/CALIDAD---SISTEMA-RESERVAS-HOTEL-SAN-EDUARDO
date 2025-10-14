from flask import Blueprint, render_template, request, current_app
from bd import obtener_conexion
import os
from datetime import datetime

habitaciones_bp = Blueprint('habitaciones', __name__)

DEFAULT_REL = 'img/habitaciones/default_room.jpg'

def _to_static_rel(path: str) -> str:
    if not path:
        return DEFAULT_REL
    p = str(path).replace('\\', '/').strip()
    if '?' in p: p = p.split('?', 1)[0]
    if p.startswith('/'): p = p[1:]
    if p.startswith('static/'): p = p[7:]
    return p or DEFAULT_REL

@habitaciones_bp.route("/habitaciones_cliente", methods=["GET"])
def habitaciones_cliente():
    tipo = request.args.get("tipo", "").strip()
    fecha_entrada = request.args.get("fecha_entrada", "")
    fecha_salida = request.args.get("fecha_salida", "")
    huespedes = request.args.get("huespedes", 1, type=int)

    con = obtener_conexion()
    habitaciones = []

    try:
        with con.cursor() as cur:
            query = """
                SELECT 
                    h.id_habitacion,
                    h.numero,
                    h.estado,
                    t.nombre AS tipo,
                    t.descripcion,
                    t.capacidad,
                    t.precio_base
                FROM habitaciones h
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                WHERE h.estado = 'Disponible'
            """
            params = []

            if tipo:
                query += " AND t.nombre = %s"
                params.append(tipo)

            cur.execute(query, params)
            habitaciones = cur.fetchall()

            for h in habitaciones:
                # Filtra por capacidad
                if h["capacidad"] < huespedes:
                    continue

                cur.execute("""
                    SELECT ruta_imagen 
                    FROM imagenes_habitacion 
                    WHERE id_habitacion = %s
                """, (h["id_habitacion"],))
                imagenes = []
                for row in cur.fetchall():
                    ruta = _to_static_rel(row["ruta_imagen"])
                    abs_path = os.path.join(current_app.static_folder, ruta)
                    if not os.path.exists(abs_path):
                        print(f"[WARN] Imagen no encontrada: /static/{ruta}")
                    imagenes.append(ruta)
                if not imagenes:
                    imagenes = [DEFAULT_REL]

                h["galeria"] = imagenes
                h["portada"] = imagenes[0]

    except Exception as e:
        print("❌ Error cargando habitaciones:", e)
    finally:
        con.close()

    return render_template("habitaciones_cliente.html", habitaciones=habitaciones,
                           fecha_entrada=fecha_entrada, fecha_salida=fecha_salida, huespedes=huespedes)
