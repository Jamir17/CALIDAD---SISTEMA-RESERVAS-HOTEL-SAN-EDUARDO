# controlador_habitaciones.py
from flask import Blueprint, render_template, request, current_app
from bd import obtener_conexion
import os

habitaciones_bp = Blueprint('habitaciones', __name__)

DEFAULT_REL = 'img/habitaciones/img1.jpg'   # fallback seguro en /static/

def _to_static_rel(path: str) -> str:
    """
    Normaliza rutas que vengan como:
    - "static/..."  -> "..."
    - "/static/..." -> "..."
    - "img/..."     -> "img/..."
    - None/''       -> DEFAULT_REL
    """
    if not path:
        return DEFAULT_REL
    p = str(path).replace('\\', '/').strip()
    if '?' in p:
        p = p.split('?', 1)[0]
    if p.startswith('/'):
        p = p[1:]
    if p.startswith('static/'):
        p = p[7:]
    return p or DEFAULT_REL


@habitaciones_bp.route("/habitaciones_cliente", methods=["GET"])
def habitaciones_cliente():
    # Filtros (persisten)
    tipo = (request.args.get("tipo") or "").strip()
    fecha_entrada = request.args.get("fecha_entrada") or ""
    fecha_salida  = request.args.get("fecha_salida") or ""
    huespedes = request.args.get("huespedes", type=int) or 1

    con = obtener_conexion()
    habitaciones = []
    tipos_unicos = []
    servicios = []

    try:
        with con.cursor() as cur:
            # Tipos para el select (orden por precio)
            cur.execute("""
                SELECT t.id_tipo, t.nombre
                FROM tipo_habitacion t
                ORDER BY t.precio_base ASC
            """)
            tipos_unicos = cur.fetchall()

            # Servicios activos para el modal
            cur.execute("""
                SELECT id_servicio, nombre, descripcion, precio
                FROM servicios
                WHERE estado = 1
                ORDER BY nombre ASC
            """)
            servicios = cur.fetchall()

            # Habitaciones disponibles + join con tipo y comodidades
            query = """
                SELECT
                    h.id_habitacion,
                    h.numero,
                    h.estado,
                    h.imagen,
                    t.id_tipo,
                    t.nombre AS tipo,
                    t.descripcion,
                    t.capacidad,
                    t.precio_base,
                    t.comodidades
                FROM habitaciones h
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                WHERE h.estado = 'Disponible'
            """
            params = []

            if tipo:
                query += " AND t.nombre = %s"
                params.append(tipo)

            # Orden principal por precio
            query += " ORDER BY t.precio_base ASC, h.numero ASC"

            cur.execute(query, params)
            raw = cur.fetchall()

            # Post-procesar (capacidad, imágenes, comodidades)
            for row in raw:
                # Filtrar por capacidad
                if (row.get("capacidad") or 0) < huespedes:
                    continue

                # Portada desde habitaciones.imagen (o default)
                portada = _to_static_rel(row.get("imagen") or DEFAULT_REL)

                # Galería por imagenes_habitacion
                cur.execute("""
                    SELECT ruta_imagen
                    FROM imagenes_habitacion
                    WHERE id_habitacion = %s
                    ORDER BY id_imagen ASC
                """, (row["id_habitacion"],))
                gal = []
                for g in cur.fetchall():
                    r = _to_static_rel(g["ruta_imagen"])
                    # Verificación opcional en disco (logging)
                    abs_path = os.path.join(current_app.static_folder, r)
                    if not os.path.exists(abs_path):
                        print(f"[WARN] No existe en disco: /static/{r}")
                    gal.append(r)
                if not gal:
                    # añade portada si no hay galería
                    gal = [portada]

                # Comodidades como lista
                amenities = []
                cstr = (row.get("comodidades") or "").strip()
                if cstr:
                    amenities = [x.strip() for x in cstr.split(",") if x.strip()]

                habitaciones.append({
                    "id_habitacion": row["id_habitacion"],
                    "numero": row["numero"],
                    "estado": row["estado"],
                    "id_tipo": row["id_tipo"],
                    "tipo": row["tipo"],
                    "descripcion": row["descripcion"],
                    "capacidad": row["capacidad"],
                    "precio_base": row["precio_base"],
                    "portada": portada,
                    "galeria": gal,
                    "comodidades": amenities
                })

    except Exception as e:
        print("❌ Error cargando habitaciones:", e)
    finally:
        con.close()

    # Render
    return render_template(
        "habitaciones_cliente.html",
        habitaciones=habitaciones,
        tipos_unicos=tipos_unicos,
        servicios=servicios,
        # filtros persistentes
        tipo=tipo,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        huespedes=huespedes,
    )
