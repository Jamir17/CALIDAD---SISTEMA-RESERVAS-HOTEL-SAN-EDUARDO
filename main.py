from flask import Flask, render_template, session, request, redirect, url_for
from datetime import timedelta
from bd import obtener_conexion
import openpyxl
from openpyxl.styles import Font, PatternFill
from controladores.controlador_usuarios import usuarios_bp
from controladores.controlador_reservas import reservas_bp
from controladores.controlador_administrador import admin_bp
from controladores.controlador_perfil import perfil_bp 
from controladores.controlador_habitaciones import habitaciones_bp
from controladores.controlador_gestion_habitaciones import gestion_habitaciones_bp
from controladores.controlador_reservas_admin import reservas_admin_bp
from controladores.controlador_notificaciones import notificaciones_bp
from controladores.controlador_checkinout import checkinout_bp
from controladores.controlador_respaldo import respaldo_bp
from controladores.controlador_gestion_roles import gestion_roles_bp
from controladores.controlador_gestion_usuarios_roles import gestion_usuarios_roles_bp
from controladores.controlador_reservas_cliente import reservas_cliente_bp
from controladores.controlador_serviciosadicionales import servicios
from controladores.controlador_incidencias import incidencias_bp
from controladores.controlador_chatbot import webchat_bp
from controladores.controlador_valoraciones import valoraciones_bp
from controladores.controlador_seguridad import seguridad_bp
from controladores.controlador_mantenimiento import mantenimiento_bp
from controladores.controlador_reportes import reportes_bp

app = Flask(__name__)
app.secret_key = "clave-super-segura"

# ====== REGISTRO DE BLUEPRINTS ======
app.permanent_session_lifetime = timedelta(days=30)

app.config['SESSION_COOKIE_HTTPONLY'] = True

# Registrar los Blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(reservas_bp, url_prefix="/reservas")
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(habitaciones_bp)
app.register_blueprint(gestion_habitaciones_bp)
app.register_blueprint(reservas_admin_bp) 
app.register_blueprint(notificaciones_bp, url_prefix="/notificaciones")
app.register_blueprint(checkinout_bp)
app.register_blueprint(respaldo_bp, url_prefix="/")
app.register_blueprint(gestion_roles_bp)
app.register_blueprint(gestion_usuarios_roles_bp)
app.register_blueprint(reservas_cliente_bp)
app.register_blueprint(servicios)
app.register_blueprint(incidencias_bp)
app.register_blueprint(webchat_bp, url_prefix="/webchat")
app.register_blueprint(valoraciones_bp, url_prefix="/valoraciones")
app.register_blueprint(seguridad_bp)
app.register_blueprint(mantenimiento_bp)
app.register_blueprint(reportes_bp)


# ====== RUTA PRINCIPAL ======
@app.route("/")
def index():
    valoraciones = []
    try:
        with obtener_conexion() as conexion:
            with conexion.cursor() as cursor:
                cursor.execute("""
                    SELECT 
                        v.puntuacion, 
                        v.comentario, 
                        c.nombres, 
                        c.apellidos
                    FROM valoraciones v
                    JOIN clientes c ON v.id_cliente = c.id_cliente
                    WHERE v.puntuacion >= 3 AND v.comentario IS NOT NULL AND v.comentario != ''
                    ORDER BY v.fecha_valoracion DESC
                    LIMIT 3
                """)
                valoraciones = cursor.fetchall()
    except Exception as e:
        print(f"Error al obtener valoraciones para el index: {e}")

    return render_template("index.html", nombre=session.get("nombre"), valoraciones=valoraciones)

@app.route("/habitaciones-principales")
def habitaciones_principales():
    """Muestra la página estática con todas las habitaciones."""
    return render_template("habitacionprincipal.html")

@app.route("/nosotros")
def nosotros():
    """Muestra la página 'Acerca de Nosotros'."""
    return render_template("nosotros.html")

# ====== ARRANQUE ======
if __name__ == "__main__":
    app.run(debug=True)
