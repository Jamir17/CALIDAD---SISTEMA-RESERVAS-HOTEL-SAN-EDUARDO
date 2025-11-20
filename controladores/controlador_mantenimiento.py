from flask import Blueprint, render_template, session, redirect, url_for, flash, jsonify, request
from bd import obtener_conexion
from controladores.controlador_respaldo import crear_respaldo_manual, listar_respaldo_historial
import psutil # Necesitarás instalarlo: pip install psutil
import pymysql
import subprocess
import sys
import os

mantenimiento_bp = Blueprint('mantenimiento', __name__, url_prefix='/mantenimiento')

@mantenimiento_bp.route('/panel')
def panel_mantenimiento():
    """
    Muestra el panel principal de mantenimiento con datos dinámicos del sistema y la BD.
    """
    if session.get('rol') != 4:
        return redirect(url_for('index'))

    # --- KPIs y Salud del Sistema ---
    try:
        cpu_usage = psutil.cpu_percent(interval=1)
        memory_info = psutil.virtual_memory()
        mem_usage = memory_info.percent
    except Exception as e:
        print(f"Error obteniendo métricas del sistema: {e}")
        cpu_usage = 0
        mem_usage = 0

    # --- Último Respaldo ---
    ultimo_respaldo_info = listar_respaldo_historial()
    ultimo_respaldo = ultimo_respaldo_info[0]['fecha'] if ultimo_respaldo_info else "No disponible"

    # --- Tamaño de la Base de Datos ---
    db_size_mb = 0
    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            cur.execute("""
                SELECT table_schema AS 'Database',
                ROUND(SUM(data_length + index_length) / 1024 / 1024, 2) AS 'Size (MB)'
                FROM information_schema.TABLES
                WHERE table_schema = %s
                GROUP BY table_schema;
            """, ("bd_hotel_san_eduardo",))
            result = cur.fetchone()
            if result:
                db_size_mb = result['Size (MB)']

            # --- Registro de Mantenimiento (Actividad) ---
            cur.execute("""
                SELECT 
                    a.id_actividad, a.accion, a.nuevo_estado_hab, a.fecha_hora,
                    h.numero as habitacion_numero,
                    c.nombres as cliente_nombres
                FROM actividad a
                LEFT JOIN habitaciones h ON a.id_habitacion = h.id_habitacion
                LEFT JOIN reservas r ON a.id_reserva = r.id_reserva
                LEFT JOIN clientes c ON r.id_cliente = c.id_cliente
                ORDER BY a.fecha_hora DESC
                LIMIT 10
            """)
            actividades = cur.fetchall()

    except Exception as e:
        print(f"Error de base de datos en panel de mantenimiento: {e}")
        actividades = []
    finally:
        if 'con' in locals() and con.open:
            con.close()

    # --- Datos para la plantilla ---
    system_health = {
        "cpu": cpu_usage,
        "mem": mem_usage,
        "db_size": db_size_mb
    }

    return render_template(
        'mantenimiento.html',
        ultimo_respaldo=ultimo_respaldo,
        system_health=system_health,
        actividades=actividades
    )

@mantenimiento_bp.route('/log/<int:id_actividad>')
def detalle_log(id_actividad):
    """Muestra los detalles de un registro de actividad específico."""
    if session.get('rol') != 4:
        return redirect(url_for('index'))

    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            cur.execute("""
                SELECT 
                    a.id_actividad, a.accion, a.nuevo_estado_hab, a.fecha_hora,
                    h.id_habitacion, h.numero as habitacion_numero,
                    r.id_reserva,
                    c.nombres as cliente_nombres, c.apellidos as cliente_apellidos
                FROM actividad a
                LEFT JOIN habitaciones h ON a.id_habitacion = h.id_habitacion
                LEFT JOIN reservas r ON a.id_reserva = r.id_reserva
                LEFT JOIN clientes c ON r.id_cliente = c.id_cliente
                WHERE a.id_actividad = %s
            """, (id_actividad,))
            log = cur.fetchone()
    except Exception as e:
        flash(f"Error al obtener detalles del log: {e}", "error")
        return redirect(url_for('mantenimiento.panel_mantenimiento'))
    finally:
        if 'con' in locals() and con.open:
            con.close()

    if not log:
        flash("Registro de actividad no encontrado.", "error")
        return redirect(url_for('mantenimiento.panel_mantenimiento'))

    return render_template('detalle_log_mantenimiento.html', log=log)

@mantenimiento_bp.route('/ejecutar-respaldo', methods=['POST'])
def ejecutar_respaldo_mantenimiento():
    """Ejecuta la creación de un respaldo desde el panel de mantenimiento."""
    ok = crear_respaldo_manual(subir_a_nube=False) # No subir a la nube desde aquí para una respuesta rápida
    if ok:
        return jsonify({'ok': True, 'message': 'Respaldo de base de datos iniciado correctamente.'})
    else:
        return jsonify({'ok': False, 'message': 'Error al iniciar el respaldo.'}), 500

@mantenimiento_bp.route('/ejecutar-actualizaciones', methods=['POST'])
def ejecutar_actualizaciones():
    """
    Ejecuta 'pip install --upgrade -r requirements.txt' para actualizar las dependencias.
    """
    if session.get('rol') != 4:
        return jsonify({'ok': False, 'message': 'No autorizado.'}), 403

    try:
        # Obtener la ruta al ejecutable de Python del entorno virtual actual
        python_executable = sys.executable
        # La ruta a pip está en el mismo directorio que el ejecutable de python
        pip_executable = os.path.join(os.path.dirname(python_executable), 'pip')

        # La ruta a requirements.txt en la raíz del proyecto
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        requirements_path = os.path.join(project_root, 'requirements.txt')

        if not os.path.exists(requirements_path):
            return jsonify({'ok': False, 'message': 'No se encontró el archivo requirements.txt.'}), 500

        # Ejecutar el comando de actualización
        result = subprocess.run(
            [pip_executable, 'install', '--upgrade', '-r', requirements_path],
            capture_output=True, text=True, check=True, encoding='utf-8'
        )
        return jsonify({'ok': True, 'message': 'Actualización de dependencias completada.', 'log': result.stdout})
    except subprocess.CalledProcessError as e:
        return jsonify({'ok': False, 'message': 'Error durante la actualización.', 'log': e.stderr}), 500
    except Exception as e:
        return jsonify({'ok': False, 'message': f'Error inesperado: {str(e)}'}), 500

@mantenimiento_bp.route('/ejecutar-sql', methods=['POST'])
def ejecutar_sql():
    """
    Ejecuta una consulta SQL cruda enviada desde la consola de mantenimiento.
    """
    if session.get('rol') != 4:
        return jsonify({'ok': False, 'error': 'No autorizado.'}), 403

    query = request.get_json().get('query', '').strip()
    if not query:
        return jsonify({'ok': False, 'error': 'La consulta no puede estar vacía.'}), 400

    # Medida de seguridad simple: no permitir múltiples sentencias en una sola ejecución.
    if ';' in query[:-1]:
        return jsonify({'ok': False, 'error': 'Solo se permite una consulta a la vez.'}), 400

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            rows_affected = cur.execute(query)
            
            # Si es un SELECT, devolvemos los resultados
            if query.lower().strip().startswith('select'):
                # Con DictCursor, fetchall() ya devuelve una lista de diccionarios.
                # No es necesario volver a construir los diccionarios.
                result = cur.fetchall()
                if not result:
                    return jsonify({'ok': True, 'result': [], 'columns': []})

                column_names = [desc[0] for desc in cur.description]
                con.commit() # Aunque sea SELECT, algunas BDs lo necesitan
                return jsonify({'ok': True, 'result': result, 'columns': column_names})
            
            # Si es INSERT, UPDATE, DELETE, devolvemos las filas afectadas
            else:
                con.commit()
                return jsonify({'ok': True, 'message': f'{rows_affected} fila(s) afectada(s).'})

    except pymysql.MySQLError as e:
        con.rollback()
        return jsonify({'ok': False, 'error': f'Error de SQL: {e}'}), 400
    except Exception as e:
        con.rollback()
        return jsonify({'ok': False, 'error': f'Error inesperado: {str(e)}'}), 500
    finally:
        if con.open:
            con.close()

@mantenimiento_bp.route('/api/contenido/<clave>', methods=['GET'])
def obtener_contenido(clave):
    """Obtiene un contenido dinámico desde la BD."""
    if session.get('rol') != 4:
        return jsonify({'ok': False, 'error': 'No autorizado.'}), 403
    
    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            cur.execute("SELECT titulo, contenido FROM contenido_dinamico WHERE clave = %s", (clave,))
            contenido = cur.fetchone()
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()

    return jsonify({'ok': True, 'data': contenido or {'titulo': '', 'contenido': ''}})

@mantenimiento_bp.route('/api/contenido/<clave>', methods=['POST'])
def guardar_contenido(clave):
    """Guarda o actualiza un contenido dinámico en la BD."""
    if session.get('rol') != 4:
        return jsonify({'ok': False, 'error': 'No autorizado.'}), 403

    data = request.get_json()
    titulo = data.get('titulo', '')
    contenido = data.get('contenido', '')

    try:
        con = obtener_conexion()
        with con.cursor() as cur:
            # UPSERT: Inserta si no existe, actualiza si ya existe.
            cur.execute("""
                INSERT INTO contenido_dinamico (clave, titulo, contenido, ultima_modificacion)
                VALUES (%s, %s, %s, NOW())
                ON DUPLICATE KEY UPDATE titulo = VALUES(titulo), contenido = VALUES(contenido), ultima_modificacion = NOW()
            """, (clave, titulo, contenido))
            con.commit()
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)}), 500
    finally:
        if 'con' in locals() and con.open:
            con.close()
            
    return jsonify({'ok': True, 'message': 'Anuncio guardado correctamente.'})