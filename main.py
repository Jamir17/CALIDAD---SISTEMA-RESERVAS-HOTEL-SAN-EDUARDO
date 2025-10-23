from flask import Flask, render_template, session, request, redirect, url_for
from datetime import timedelta
from controladores.controlador_usuarios import usuarios_bp
from controladores.controlador_reservas import reservas_bp
from controladores.controlador_administrador import admin_bp
from controladores.controlador_perfil import perfil_bp
from controladores.controlador_habitaciones import habitaciones_bp
from controladores.controlador_reservas_admin import reservas_admin_bp
from controladores.controlador_notificaciones import notificaciones_bp
from controladores.controlador_checkinout import checkinout_bp
from controladores.controlador_respaldo import respaldo_bp
from controladores.controlador_gestion_roles import gestion_roles_bp
from controladores.controlador_gestion_usuarios_roles import gestion_usuarios_roles_bp

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
app.register_blueprint(habitaciones_bp, url_prefix="/habitaciones")
app.register_blueprint(reservas_admin_bp) 
app.register_blueprint(notificaciones_bp, url_prefix="/notificaciones")
app.register_blueprint(checkinout_bp)
app.register_blueprint(respaldo_bp, url_prefix="/")
app.register_blueprint(gestion_roles_bp)
app.register_blueprint(gestion_usuarios_roles_bp)

# ====== RUTA PRINCIPAL ======
@app.route("/")
def index():
    return render_template("index.html", nombre=session.get("nombre"))

# ====== ARRANQUE ======
if __name__ == "__main__":
    app.run(debug=True)
