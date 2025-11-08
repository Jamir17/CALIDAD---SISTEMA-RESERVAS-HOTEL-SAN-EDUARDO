# controlador_habitaciones.py
from flask import Blueprint, render_template, request, redirect, url_for, current_app
from bd import obtener_conexion
import os

habitaciones_bp = Blueprint('habitaciones', __name__)

DEFAULT_REL = 'img/habitaciones/img1.jpg'  # Imagen por defecto en /static/


def _to_static_rel(path: str) -> str:
    """Normaliza rutas de imágenes evitando errores."""
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
    """
    Página de búsqueda y visualización de habitaciones disponibles.
    Carga todo automáticamente si no hay parámetros.
    """
    # ✅ Redirigir con parámetros iniciales si la URL está vacía
    if not request.args:
        return redirect(url_for("habitaciones.habitaciones_cliente",
                                fecha_entrada="",
                                fecha_salida="",
                                tipo="",
                                huespedes=1))

    tipo = (request.args.get("tipo") or "").strip()
    fecha_entrada = request.args.get("fecha_entrada") or ""
    fecha_salida = request.args.get("fecha_salida") or ""
    huespedes = request.args.get("huespedes", type=int) or 1

    habitaciones = []
    tipos_unicos = []
    servicios = []

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            # 🔹 Tipos de habitación
            cur.execute("""
                SELECT id_tipo, nombre
                FROM tipo_habitacion
                ORDER BY precio_base ASC
            """)
            tipos_unicos = cur.fetchall()

            # 🔹 Servicios activos
            cur.execute("""
                SELECT id_servicio, nombre, descripcion, precio
                FROM servicios
                WHERE estado = 1
                ORDER BY nombre ASC
            """)
            servicios = cur.fetchall()

            # 🔹 Habitaciones base
            query = """
                SELECT
                    h.id_habitacion,
                    h.numero,
                    h.estado,
                    COALESCE(h.imagen, %s) AS imagen,
                    t.id_tipo,
                    t.nombre AS tipo,
                    COALESCE(t.descripcion, '') AS descripcion,
                    COALESCE(t.capacidad, 1) AS capacidad,
                    COALESCE(t.precio_base, 0) AS precio_base,
                    COALESCE(t.comodidades, '') AS comodidades
                FROM habitaciones h
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                WHERE h.estado = 'Disponible'
            """
            params = [DEFAULT_REL]

            # 🔹 Filtro por tipo
            if tipo:
                query += " AND t.nombre = %s"
                params.append(tipo)

            # 🔹 Filtro de disponibilidad por fechas
            if fecha_entrada and fecha_salida:
                query += """
                    AND h.id_habitacion NOT IN (
                        SELECT r.id_habitacion
                        FROM reservas r
                        WHERE r.id_habitacion IS NOT NULL
                          AND r.estado IN ('Activa', 'Pendiente')
                          AND (
                              (r.fecha_entrada < %s AND r.fecha_salida > %s)
                              OR (r.fecha_entrada BETWEEN %s AND %s)
                              OR (r.fecha_salida BETWEEN %s AND %s)
                          )
                    )
                """
                params += [
                    fecha_salida, fecha_entrada,
                    fecha_entrada, fecha_salida,
                    fecha_entrada, fecha_salida
                ]

            query += " ORDER BY t.precio_base ASC, h.numero ASC"
            cur.execute(query, params)
            raw = cur.fetchall()

            for row in raw:
                # Filtrar por capacidad
                if (row.get("capacidad") or 0) < huespedes:
                    continue

                portada = _to_static_rel(row.get("imagen") or DEFAULT_REL)

                # Galería
                cur.execute("""
                    SELECT ruta_imagen
                    FROM imagenes_habitacion
                    WHERE id_habitacion = (
                        SELECT id_habitacion
                        FROM imagenes_habitacion
                        WHERE id_habitacion IN (SELECT id_habitacion FROM habitaciones WHERE id_tipo = %s)
                        LIMIT 1
                    )
                    ORDER BY id_imagen ASC
                """, (row["id_tipo"],))
                gal = [_to_static_rel(g["ruta_imagen"]) for g in cur.fetchall()] or [portada]

                cstr = (row.get("comodidades") or "").strip()
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


    return render_template(
        "habitaciones_cliente.html",
        habitaciones=habitaciones,
        tipos_unicos=tipos_unicos,
        servicios=servicios,
        tipo=tipo,
        fecha_entrada=fecha_entrada,
        fecha_salida=fecha_salida,
        huespedes=huespedes,
    )


