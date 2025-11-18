from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from bd import obtener_conexion

valoraciones_bp = Blueprint('valoraciones', __name__, url_prefix='/valoraciones')

@valoraciones_bp.route('/nueva/<int:id_reserva>')
def nueva_valoracion(id_reserva):
    """
    Muestra el formulario para que un cliente deje su valoración.
    """
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para poder valorar tu estancia.', 'warning')
        return redirect(url_for('usuarios.iniciosesion'))

    id_usuario = session['usuario_id']
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Verificamos que la reserva exista, pertenezca al usuario y esté finalizada
                cursor.execute("""
                    SELECT 
                        r.id_reserva, r.fecha_entrada, r.fecha_salida,
                        c.nombres, c.apellidos
                    FROM reservas r
                    JOIN clientes c ON r.id_cliente = c.id_cliente
                    WHERE r.id_reserva = %s 
                      AND r.id_usuario = %s
                      AND r.estado = 'Finalizada'
                """, (id_reserva, id_usuario))
                reserva = cursor.fetchone()

                if not reserva:
                    flash('Esta reserva no se puede valorar o no te pertenece.', 'warning')
                    return redirect(url_for('reservas.mis_reservas'))

                # Verificar si ya fue valorada
                cursor.execute("SELECT id_valoracion FROM valoraciones WHERE id_reserva = %s", (id_reserva,))
                if cursor.fetchone():
                    flash('Esta estancia ya ha sido valorada.', 'info')
                    return redirect(url_for('reservas.mis_reservas'))

    except Exception as e:
        flash(f'Ocurrió un error al cargar la página de valoración: {e}', 'danger')
        return redirect(url_for('reservas.mis_reservas'))

    # Pasamos el objeto 'reserva' a la plantilla
    return render_template('nueva_valoracion.html', reserva=reserva)


@valoraciones_bp.route('/guardar/<int:id_reserva>', methods=['POST'])
def guardar_valoracion(id_reserva):
    """
    Guarda la valoración enviada por el cliente en la base de datos.
    """
    if 'usuario_id' not in session:
        flash('Acceso no autorizado.', 'danger')
        return redirect(url_for('usuarios.iniciosesion'))

    id_usuario = session['usuario_id']
    puntuacion = request.form.get('puntuacion')
    comentario = request.form.get('comentario')

    if not puntuacion:
        flash('Debes seleccionar una puntuación.', 'warning')
        return redirect(url_for('valoraciones.nueva_valoracion', id_reserva=id_reserva))

    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # Verificamos que la reserva pertenece al usuario para obtener el id_cliente
                cursor.execute("SELECT id_cliente FROM clientes WHERE id_usuario = %s", (id_usuario,))
                cliente = cursor.fetchone()

                if not cliente:
                    flash('No tienes permiso para valorar esta reserva.', 'danger')
                    return redirect(url_for('reservas.mis_reservas'))

                cursor.execute("INSERT INTO valoraciones (id_cliente, id_reserva, puntuacion, comentario) VALUES (%s, %s, %s, %s)",
                               (cliente['id_cliente'], id_reserva, int(puntuacion), comentario))
            conexion.commit()
        flash('¡Gracias por tu valoración! Tu opinión es muy importante para nosotros.', 'success')
        return redirect(url_for('reservas.mis_reservas'))
    except Exception as e:
        flash(f'Ocurrió un error al guardar tu valoración: {e}', 'danger')
        return redirect(url_for('valoraciones.nueva_valoracion', id_reserva=id_reserva))

@valoraciones_bp.route('/valoracion_usuario')
def mis_valoraciones():
    """
    Muestra el historial de valoraciones de un usuario.
    """
    if 'usuario_id' not in session:
        flash('Debes iniciar sesión para ver tus valoraciones.', 'warning')
        return redirect(url_for('usuarios.iniciosesion'))

    id_usuario = session['usuario_id']
    reserva_a_valorar = None
    valoraciones = []
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                # 1. Buscar la reserva más reciente finalizada y sin valorar
                cursor.execute("""
                    SELECT r.id_reserva, r.fecha_entrada, r.fecha_salida, c.nombres, c.apellidos
                    FROM reservas r
                    JOIN clientes c ON r.id_cliente = c.id_cliente
                    WHERE r.id_usuario = %s
                      AND r.estado = 'Finalizada'
                      AND r.id_reserva NOT IN (SELECT id_reserva FROM valoraciones WHERE id_reserva IS NOT NULL)
                    ORDER BY r.fecha_salida DESC
                    LIMIT 1
                """, (id_usuario,))
                reserva_a_valorar = cursor.fetchone()

                # 2. Buscar el historial de valoraciones ya hechas
                cursor.execute("""
                    SELECT v.id_reserva, v.puntuacion, v.comentario, v.fecha_valoracion
                    FROM valoraciones v
                    JOIN clientes c ON v.id_cliente = c.id_cliente
                    WHERE c.id_usuario = %s
                    ORDER BY v.fecha_valoracion DESC
                """, (id_usuario,))
                valoraciones = cursor.fetchall()
    except Exception as e:
        flash(f'Ocurrió un error al cargar tus valoraciones: {e}', 'danger')

    return render_template(
        'valoracion_usuario.html',
        valoraciones=valoraciones,
        reserva_a_valorar=reserva_a_valorar
    )