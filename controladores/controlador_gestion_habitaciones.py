from flask import Blueprint, render_template, session, request, jsonify
from bd import obtener_conexion
import pymysql
import os
from werkzeug.utils import secure_filename
from collections import Counter

# Crear un Blueprint
gestion_habitaciones_bp = Blueprint('gestion_habitaciones', __name__, url_prefix='/habitaciones')

@gestion_habitaciones_bp.route('/panel')
def panel_habitaciones():
    """
    Muestra el panel de gestión de habitaciones con datos de la BD.
    """
    con = obtener_conexion()
    try:
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            # Obtener todas las habitaciones con el nombre de su tipo
            cur.execute("""
                SELECT h.id_habitacion, h.numero, t.nombre AS tipo, h.estado, t.precio_base, t.descripcion, h.imagen
                FROM habitaciones h
                JOIN tipo_habitacion t ON h.id_tipo = t.id_tipo
                ORDER BY h.numero ASC
            """)
            habitaciones = cur.fetchall()

            # Obtener todos los tipos de habitación para el modal
            cur.execute("SELECT id_tipo, nombre FROM tipo_habitacion ORDER BY nombre")
            tipos_habitacion = cur.fetchall()
            
            # Calcular KPIs (indicadores)
            estados = [h['estado'] for h in habitaciones]
            conteo_estados = Counter(estados)
            kpis = {
                'total': len(habitaciones),
                'disponibles': conteo_estados.get('Disponible', 0),
                'ocupadas': conteo_estados.get('Ocupada', 0),
                'mantenimiento': conteo_estados.get('Mantenimiento', 0) + conteo_estados.get('En Limpieza', 0)
            }

    except Exception as e:
        print(f"Error al consultar habitaciones: {e}")
        habitaciones = []
        tipos_habitacion = []
        kpis = {'total': 0, 'disponibles': 0, 'ocupadas': 0, 'mantenimiento': 0}
    finally:
        if 'con' in locals() and con.open:
            con.close()

    return render_template(
        "gestion_habitaciones.html",
        habitaciones=habitaciones,
        tipos_habitacion=tipos_habitacion,
        kpis=kpis
    )

@gestion_habitaciones_bp.route('/crear', methods=['POST'])
def crear_habitacion():
    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            # Manejo de la imagen
            ruta_imagen = None
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file.filename != '':
                    filename = secure_filename(file.filename)
                    # Asegúrate de que la ruta base sea correcta
                    upload_path = os.path.join('static', 'img', 'habitaciones', filename)
                    file.save(upload_path)
                    ruta_imagen = os.path.join('img', 'habitaciones', filename).replace('\\', '/')

            cur.execute("""
                INSERT INTO habitaciones (numero, id_tipo, estado, imagen)
                VALUES (%s, %s, %s, %s)
            """, (request.form.get('numero'), request.form.get('id_tipo'), request.form.get('estado'), ruta_imagen))
        con.commit()
        return jsonify({'ok': True, 'message': 'Habitación creada con éxito.'})
    except pymysql.err.IntegrityError as e:
        # Error de integridad, como una clave duplicada (UNIQUE constraint)
        if e.args[0] == 1062: # Código de error para 'Duplicate entry'
            return jsonify({'ok': False, 'message': 'Ya existe una habitación con ese número. Por favor, elige otro.'}), 409 # 409 Conflict
        else:
            print(f"Error de integridad al crear habitación: {e}")
            return jsonify({'ok': False, 'message': 'Error de base de datos al crear la habitación.'}), 500
    except Exception as e:
        print(f"Error al crear habitación: {e}")
        return jsonify({'ok': False, 'message': 'Error al crear la habitación.'}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()

@gestion_habitaciones_bp.route('/obtener/<int:id_habitacion>')
def obtener_habitacion(id_habitacion):
    try:
        con = obtener_conexion()
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT * FROM habitaciones WHERE id_habitacion = %s", (id_habitacion,))
            habitacion = cur.fetchone()
        if habitacion:
            return jsonify(habitacion)
        return jsonify({'ok': False, 'message': 'Habitación no encontrada.'}), 404
    except Exception as e:
        print(f"Error al obtener habitación: {e}")
        return jsonify({'ok': False, 'message': 'Error interno del servidor.'}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()

@gestion_habitaciones_bp.route('/editar/<int:id_habitacion>', methods=['POST'])
def editar_habitacion(id_habitacion):
    try:
        con = obtener_conexion()
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            # Obtener ruta de imagen actual
            cur.execute("SELECT imagen FROM habitaciones WHERE id_habitacion = %s", (id_habitacion,))
            ruta_actual = cur.fetchone().get('imagen')

            ruta_imagen = ruta_actual
            if 'imagen' in request.files:
                file = request.files['imagen']
                if file.filename != '':
                    # Opcional: eliminar la imagen anterior si existe
                    # if ruta_actual and os.path.exists(os.path.join('static', ruta_actual)):
                    #     os.remove(os.path.join('static', ruta_actual))
                    filename = secure_filename(file.filename)
                    upload_path = os.path.join('static', 'img', 'habitaciones', filename)
                    file.save(upload_path)
                    ruta_imagen = os.path.join('img', 'habitaciones', filename).replace('\\', '/')

            cur.execute("""
                UPDATE habitaciones SET numero=%s, id_tipo=%s, estado=%s, imagen=%s
                WHERE id_habitacion=%s
            """, (request.form.get('numero'), request.form.get('id_tipo'), request.form.get('estado'), ruta_imagen, id_habitacion))
        con.commit()
        return jsonify({'ok': True, 'message': 'Habitación actualizada con éxito.'})
    except Exception as e:
        print(f"Error al editar habitación: {e}")
        return jsonify({'ok': False, 'message': 'Error al actualizar la habitación.'}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()

@gestion_habitaciones_bp.route('/eliminar/<int:id_habitacion>', methods=['POST'])
def eliminar_habitacion(id_habitacion):
    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            # Opcional: verificar si la habitación tiene reservas activas antes de eliminar
            # cur.execute("SELECT COUNT(*) FROM reservas WHERE id_habitacion = %s AND estado = 'Activa'", (id_habitacion,))
            # if cur.fetchone()[0] > 0:
            #     return jsonify({'ok': False, 'message': 'No se puede eliminar, la habitación tiene reservas activas.'}), 409
            
            cur.execute("DELETE FROM habitaciones WHERE id_habitacion = %s", (id_habitacion,))
        con.commit()
        return jsonify({'ok': True, 'message': 'Habitación eliminada con éxito.'})
    except pymysql.err.IntegrityError:
        return jsonify({'ok': False, 'message': 'No se puede eliminar. La habitación está siendo usada en reservas existentes.'}), 409
    except Exception as e:
        print(f"Error al eliminar habitación: {e}")
        return jsonify({'ok': False, 'message': 'Error al eliminar la habitación.'}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()

@gestion_habitaciones_bp.route('/api/tipos_habitacion')
def api_tipos_habitacion():
    """
    Devuelve una lista de tipos de habitación en formato JSON.
    """
    try:
        con = obtener_conexion()
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT id_tipo, nombre FROM tipo_habitacion ORDER BY nombre")
            tipos = cur.fetchall()
        return jsonify(tipos)
    except Exception as e:
        print(f"Error al obtener tipos de habitación: {e}")
        return jsonify([]), 500

@gestion_habitaciones_bp.route('/tipos/crear', methods=['POST'])
def crear_tipo_habitacion():
    """Crea un nuevo tipo de habitación y lo devuelve."""
    try:
        data = request.json
        con = obtener_conexion()
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("""
                INSERT INTO tipo_habitacion (nombre, descripcion, capacidad, precio_base, comodidades)
                VALUES (%s, %s, %s, %s, %s)
            """, (data['nombre'], data.get('descripcion', ''), data.get('capacidad', 1), data['precio_base'], data.get('comodidades', '')))
            con.commit()
            
            # Devolver el tipo recién creado
            cur.execute("SELECT id_tipo, nombre FROM tipo_habitacion WHERE id_tipo = LAST_INSERT_ID()")
            nuevo_tipo = cur.fetchone()
            
        return jsonify({'ok': True, 'message': 'Tipo de habitación creado.', 'tipo': nuevo_tipo})
    except pymysql.err.IntegrityError:
        return jsonify({'ok': False, 'message': 'Ya existe un tipo de habitación con ese nombre.'}), 409
    except Exception as e:
        print(f"Error al crear tipo de habitación: {e}")
        return jsonify({'ok': False, 'message': 'Error al crear el tipo de habitación.'}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()

@gestion_habitaciones_bp.route('/tipos/obtener/<int:id_tipo>')
def obtener_tipo_habitacion(id_tipo):
    """Obtiene los detalles de un tipo de habitación, incluyendo el precio."""
    try:
        con = obtener_conexion()
        with con.cursor(pymysql.cursors.DictCursor) as cur:
            cur.execute("SELECT precio_base FROM tipo_habitacion WHERE id_tipo = %s", (id_tipo,))
            tipo = cur.fetchone()
        return jsonify(tipo if tipo else {})
    finally:
        if 'con' in locals() and con.open:
            con.close()