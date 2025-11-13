from flask import Blueprint, render_template, request, flash, redirect, url_for, session
from bd import obtener_conexion
from datetime import datetime
from .controlador_administrador import requiere_login_rol

incidencias_bp = Blueprint('incidencias', __name__, url_prefix='/incidencias')

@incidencias_bp.route('/reportar', methods=['GET', 'POST'])
def reportar_incidencia_cliente():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para reportar una incidencia.', 'warning')
        return redirect(url_for('usuarios.iniciosesion'))

    id_usuario = session['usuario_id']
    con = obtener_conexion()
    
    try:
        with con.cursor() as cur:
            # Buscar la reserva activa del cliente para asociar la incidencia
            cur.execute("""
                SELECT r.id_reserva, h.numero as numero_habitacion
                FROM reservas r
                JOIN clientes c ON r.id_cliente = c.id_cliente
                JOIN habitaciones h ON r.id_habitacion = h.id_habitacion
                WHERE c.id_usuario = %s AND r.estado = 'Activa'
                LIMIT 1
            """, (id_usuario,))
            reserva_activa = cur.fetchone()

        if request.method == 'POST':
            if not reserva_activa:
                flash('No tienes una reserva activa para reportar una incidencia.', 'error')
                return redirect(url_for('index'))

            descripcion = request.form.get('descripcion')
            if not descripcion:
                flash('La descripción no puede estar vacía.', 'error')
                return redirect(url_for('incidencias.reportar_incidencia_cliente'))

            with con.cursor() as cur:
                cur.execute("""
                    INSERT INTO incidencias (id_reserva, id_habitacion, id_usuario, descripcion, fecha_reporte, estado)
                    VALUES (%s, (SELECT id_habitacion FROM reservas WHERE id_reserva = %s), %s, %s, %s, 'Pendiente')
                """, (reserva_activa['id_reserva'], reserva_activa['id_reserva'], id_usuario, descripcion, datetime.now()))
            con.commit()
            
            flash('Tu incidencia ha sido reportada con éxito. Nuestro equipo la atenderá a la brevedad.', 'success')
            return redirect(url_for('index'))

    except Exception as e:
        print(f"Error en incidencias: {e}")
        flash('Ocurrió un error al procesar tu solicitud.', 'error')
    finally:
        if con.open:
            con.close()

    return render_template('reportar_incidencia.html', reserva_activa=reserva_activa)

@incidencias_bp.route('/mis-incidencias')
def listar_mis_incidencias():
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para ver tus incidencias.', 'warning')
        return redirect(url_for('usuarios.iniciosesion'))

    id_usuario = session['usuario_id']
    con = obtener_conexion()
    
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT 
                    i.id_incidencia, i.descripcion, i.fecha_reporte, i.estado,
                    h.numero as numero_habitacion
                FROM incidencias i
                LEFT JOIN habitaciones h ON i.id_habitacion = h.id_habitacion
                WHERE i.id_usuario = %s
                ORDER BY i.fecha_reporte DESC
            """, (id_usuario,))
            incidencias = cur.fetchall()
    finally:
        con.close()

    return render_template('mis_incidencias.html', incidencias=incidencias)

@incidencias_bp.route('/panel')
@requiere_login_rol({1}) # Solo Admin
def panel_incidencias():
    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("""
                SELECT 
                    i.id_incidencia, i.descripcion, i.fecha_reporte, i.estado,
                    h.numero as numero_habitacion,
                    c.nombres, c.apellidos
                FROM incidencias i
                LEFT JOIN habitaciones h ON i.id_habitacion = h.id_habitacion
                LEFT JOIN clientes c ON i.id_usuario = c.id_usuario
                ORDER BY i.fecha_reporte DESC
            """)
            incidencias = cur.fetchall()
    finally:
        con.close()
    return render_template('incidencias_admin.html', incidencias=incidencias)

@incidencias_bp.route('/actualizar-estado', methods=['POST'])
@requiere_login_rol({1}) # Solo Admin
def actualizar_estado_incidencia():
    id_incidencia = request.form.get('id_incidencia')
    nuevo_estado = request.form.get('nuevo_estado')

    if not id_incidencia or not nuevo_estado:
        flash('Datos incompletos para actualizar la incidencia.', 'error')
        return redirect(url_for('incidencias.panel_incidencias'))

    con = obtener_conexion()
    try:
        with con.cursor() as cur:
            cur.execute("UPDATE incidencias SET estado = %s WHERE id_incidencia = %s", (nuevo_estado, id_incidencia))
        con.commit()
        flash(f'El estado de la incidencia #{id_incidencia} ha sido actualizado a "{nuevo_estado}".', 'success')
    except Exception as e:
        print(f"Error al actualizar estado de incidencia: {e}")
        flash('Ocurrió un error al actualizar el estado.', 'error')
    finally:
        con.close()

    return redirect(url_for('incidencias.panel_incidencias'))