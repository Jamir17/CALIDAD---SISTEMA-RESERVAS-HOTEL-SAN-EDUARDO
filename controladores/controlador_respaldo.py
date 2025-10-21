from flask import Blueprint, render_template, send_file, redirect, url_for, flash
from datetime import datetime
import os, subprocess
from apscheduler.schedulers.background import BackgroundScheduler

respaldo_bp = Blueprint("respaldo", __name__)

# ==============================================
# 📁 CONFIGURACIÓN GENERAL
# ==============================================
BACKUP_FOLDER = "static/backups"
if not os.path.exists(BACKUP_FOLDER):
    os.makedirs(BACKUP_FOLDER)

# 💾 CONFIGURACIÓN DE BASE DE DATOS
DB_NAME = "bd_hotel_san_eduardo"
DB_USER = "root"
DB_PASS = "admin"  # <-- cámbiala

# 🛠️ Ruta del ejecutable mysqldump
MYSQLDUMP_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
if not os.path.exists(MYSQLDUMP_PATH):
    MYSQLDUMP_PATH = r"C:\xampp\mysql\bin\mysqldump.exe"  # alternativa XAMPP


# ==============================================
# 🧠 FUNCIONES INTERNAS
# ==============================================
def listar_respaldo_historial():
    """Lista los archivos de respaldo existentes"""
    archivos = []
    for archivo in os.listdir(BACKUP_FOLDER):
        if archivo.endswith(".sql"):
            ruta = os.path.join(BACKUP_FOLDER, archivo)
            tamaño = round(os.path.getsize(ruta) / 1024, 2)
            fecha = datetime.fromtimestamp(os.path.getctime(ruta)).strftime("%Y-%m-%d %H:%M:%S")
            archivos.append({
                "nombre": archivo,
                "fecha": fecha,
                "tamaño": tamaño
            })
    archivos.sort(key=lambda x: x["fecha"], reverse=True)
    return archivos


def crear_respaldo_manual():
    """Genera un archivo .sql con la estructura y datos actuales (seguro y limpio)"""
    try:
        fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
        nombre_archivo = f"respaldo_{fecha}.sql"
        ruta_backup = os.path.join(BACKUP_FOLDER, nombre_archivo)

        # Comando mysqldump seguro
        cmd = [
            MYSQLDUMP_PATH,
            "-u", DB_USER,
            f"-p{DB_PASS}",
            "--skip-add-drop-table",      # ❌ Evita DROP TABLE
            "--add-drop-database=FALSE",  # ❌ Evita DROP DATABASE
            "--databases", DB_NAME,       # ✅ Incluye la creación de la base
            "--skip-comments",            # Limpia encabezados
            "--skip-add-locks",           # Sin bloqueos
            "--skip-disable-keys",        # Mantiene índices
            "--no-tablespaces"            # Evita warnings
        ]

        # Ejecutar mysqldump
        with open(ruta_backup, "wb") as salida:
            proceso = subprocess.Popen(cmd, stdout=salida, stderr=subprocess.PIPE)
            _, errores = proceso.communicate()

        if proceso.returncode == 0:
            # 🔧 Insertar "IF NOT EXISTS" en las tablas
            with open(ruta_backup, "r", encoding="utf-8", errors="ignore") as f:
                contenido = f.read()

            contenido = contenido.replace("CREATE TABLE `", "CREATE TABLE IF NOT EXISTS `")
            contenido = contenido.replace("CREATE DATABASE ", "CREATE DATABASE IF NOT EXISTS ")

            with open(ruta_backup, "w", encoding="utf-8") as f:
                f.write(contenido)

            print(f"✅ Respaldo generado correctamente: {nombre_archivo}")
            return True
        else:
            print("❌ Error en mysqldump:", errores.decode("utf-8"))
            return False

    except Exception as e:
        print("⚠️ Error general en crear_respaldo_manual:", e)
        return False

# ==============================================
# 🌐 RUTAS FLASK
# ==============================================
@respaldo_bp.route("/admin/respaldo")
def panel_respaldo():
    registros = listar_respaldo_historial()
    return render_template("respaldo.html", registros=registros)


@respaldo_bp.route("/admin/respaldo/ejecutar", methods=["POST"])
def ejecutar_respaldo():
    exito = crear_respaldo_manual()
    if exito:
        flash("✅ Respaldo creado exitosamente.", "success")
    else:
        flash("❌ No se pudo crear el respaldo.", "danger")
    return redirect(url_for("respaldo.panel_respaldo"))


@respaldo_bp.route("/admin/respaldo/descargar/<nombre>")
def descargar_respaldo(nombre):
    ruta = os.path.join(BACKUP_FOLDER, nombre)
    if os.path.exists(ruta):
        return send_file(ruta, as_attachment=True)
    flash("Archivo no encontrado.", "error")
    return redirect(url_for("respaldo.panel_respaldo"))


@respaldo_bp.route("/admin/respaldo/eliminar/<nombre>", methods=["POST"])
def eliminar_respaldo(nombre):
    ruta = os.path.join(BACKUP_FOLDER, nombre)
    if os.path.exists(ruta):
        os.remove(ruta)
        flash("🗑️ Respaldo eliminado correctamente.", "success")
    else:
        flash("Archivo no encontrado.", "error")
    return redirect(url_for("respaldo.panel_respaldo"))


# ==============================================
# 🔄 TAREA AUTOMÁTICA DIARIA
# ==============================================
def programar_respaldo_automatico():
    """Ejecuta un respaldo automáticamente a una hora definida"""
    scheduler = BackgroundScheduler()
    scheduler.add_job(crear_respaldo_manual, "cron",
                      hour=2, minute=0)  # <-- ⏰ EDITA AQUÍ la hora (ej: 2=02:00 a.m.)
    scheduler.start()
    print("🕑 Tarea de respaldo automático programada (diaria).")


# Iniciar el scheduler al cargar el Blueprint
programar_respaldo_automatico()


@respaldo_bp.route("/admin/respaldo/restaurar/<nombre>", methods=["POST"])
def restaurar_respaldo(nombre):
    """Restaura la BD desde un archivo .sql del directorio BACKUP_FOLDER"""
    try:
        # archivo a restaurar
        ruta_sql = os.path.join(BACKUP_FOLDER, nombre)
        if not os.path.exists(ruta_sql):
            flash("Archivo de respaldo no encontrado.", "danger")
            return redirect(url_for("respaldo.panel_respaldo"))

        # Localiza el mysql.exe (cliente) – ajusta si usas XAMPP
        MYSQL_PATH = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysql.exe"
        if not os.path.exists(MYSQL_PATH):
            MYSQL_PATH = r"C:\xampp\mysql\bin\mysql.exe"

        # Comando: mysql -u USER -pPASS BD < archivo.sql
        # Usamos stdin para evitar problemas con redirecciones en shell
        cmd = [MYSQL_PATH, "-u", DB_USER, f"-p{DB_PASS}", DB_NAME]

        with open(ruta_sql, "rb") as entrada:
            proc = subprocess.Popen(cmd, stdin=entrada,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = proc.communicate()

        if proc.returncode == 0:
            flash("✅ Base de datos restaurada correctamente.", "success")
        else:
            # Muestra el error de mysql en consola y alerta en UI
            print("❌ Error al restaurar:", err.decode("utf-8", errors="ignore"))
            flash("❌ Error al restaurar la base de datos. Revisa la consola.", "danger")

    except Exception as e:
        print("⚠️ Excepción al restaurar:", e)
        flash(f"⚠️ Error inesperado: {e}", "danger")

    return redirect(url_for("respaldo.panel_respaldo"))
