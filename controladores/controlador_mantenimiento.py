from flask import Blueprint, render_template, session, redirect, url_for

mantenimiento_bp = Blueprint('mantenimiento', __name__, url_prefix='/mantenimiento')

@mantenimiento_bp.route('/panel')
def panel_mantenimiento():
    """
    Muestra el panel principal de mantenimiento.
    """
    if session.get('rol') != 1:  # Solo para administradores
        return redirect(url_for('index'))

    # Aquí iría la lógica para obtener datos reales. Por ahora, solo renderiza.
    return render_template('mantenimiento.html')