from flask import Flask, render_template, session
from controladores.controlador_usuarios import usuarios_bp
from controladores.controlador_reservas import reservas_bp   # << nuevo
from controladores.controlador_administrador import admin_bp
from controladores.controlador_perfil import perfil_bp
from controladores.controlador_habitaciones import habitaciones_bp
app = Flask(__name__)
app.secret_key = "clave-super-segura"

# Registrar los Blueprints
app.register_blueprint(usuarios_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(reservas_bp, url_prefix="/reservas") 
app.register_blueprint(admin_bp,    url_prefix="/admin")  
app.register_blueprint(habitaciones_bp, url_prefix="/habitaciones")

# Ruta principal
@app.route("/")
def index():
    return render_template("index.html", nombre=session.get("nombre"))

if __name__ == "__main__":
    app.run(debug=True)
