from flask import Flask, render_template, session
from controladores.controlador_usuarios import usuarios_bp

app = Flask(__name__)
app.secret_key = "clave-super-segura"

# Registrar los Blueprints
app.register_blueprint(usuarios_bp)

# Ruta principal
@app.route("/")
def index():
    return render_template("index.html", nombre=session.get("nombre"))

if __name__ == "__main__":
    app.run(debug=True)
