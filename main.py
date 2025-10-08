from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "cambia-esto-por-uno-seguro"

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/iniciar-sesion", methods=["GET", "POST"], endpoint="iniciosesion")
def login():
    if request.method == "POST":
        # TODO: validar credenciales
        flash("Has iniciado sesión (demo).", "success")
        return redirect(url_for("index"))

    return render_template("iniciosesion.html")

@app.route("/registro", methods=["GET", "POST"], endpoint="registro")
def registro():
    if request.method == "POST":
        # TODO: registrar usuario
        flash("Registro enviado (demo).", "success")
        return redirect(url_for("index"))
    
    return render_template("registro.html")

if __name__ == "__main__":
    app.run(debug=True)
