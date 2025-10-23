from flask import Blueprint, render_template, send_file, redirect, url_for, flash
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from pytz import timezone
import subprocess
import os

# ==============================================
# 🔹 BLUEPRINT
# ==============================================
respaldo_bp = Blueprint("respaldo", __name__)

# ==============================================
# 📁 CONFIGURACIÓN GENERAL
# ==============================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ../static/backups
BACKUP_FOLDER = os.path.normpath(os.path.join(BASE_DIR, "..", "static", "backups"))
os.makedirs(BACKUP_FOLDER, exist_ok=True)

# 💾 CONFIGURACIÓN DE BASE DE DATOS (usa variables de entorno en producción)
DB_NAME = "bd_hotel_san_eduardo"
DB_USER = os.getenv("MYSQL_USER", "root")
DB_PASS = os.getenv("MYSQL_PASS", "admin")  # ✱ cámbiala / usa ENV

# 🕒 ZONA HORARIA (Lima)
TZ = timezone("America/Lima")

# ==============================================
# 🔎 Descubrimiento de binarios MySQL
# ==============================================
def _find_mysql_binaries():
    """Devuelve (mysql.exe, mysqldump.exe) o (None, None) si no los encuentra."""
    candidates = []

    # Prioriza variable de entorno
    mysql_home = os.getenv("MYSQL_HOME")
    if mysql_home:
        candidates.append(os.path.join(mysql_home, "bin"))

    # Rutas comunes Windows (MySQL, XAMPP, MariaDB)
    candidates += [
        r"C:\Program Files\MySQL\MySQL Server 8.0\bin",
        r"C:\Program Files\MySQL\MySQL Workbench 8.0 CE",
        r"C:\xampp\mysql\bin",
        r"C:\Program Files\MariaDB 10.6\bin",
        r"C:\Program Files\MariaDB 10.11\bin",
    ]

    mysql_path = None
    mysqldump_path = None
    for base in candidates:
        mp = os.path.join(base, "mysql.exe")
        md = os.path.join(base, "mysqldump.exe")
        if os.path.exists(mp) and os.path.exists(md):
            mysql_path, mysqldump_path = mp, md
            break

    return mysql_path, mysqldump_path


def _safe_filename(name: str) -> str:
    """Evita path traversal y fuerza extensión .sql."""
    if not name or os.path.basename(name) != name:
        return ""
    if not name.lower().endswith(".sql"):
        return ""
    return name


# ==============================================
# 🧠 FUNCIONES INTERNAS
# ==============================================
def listar_respaldo_historial():
    """Lista los archivos .sql existentes ordenados por fecha de creación (desc)."""
    items = []
    for fname in os.listdir(BACKUP_FOLDER):
        if not fname.lower().endswith(".sql"):
            continue
        path = os.path.join(BACKUP_FOLDER, fname)
        try:
            ctime = os.path.getctime(path)
            fecha = datetime.fromtimestamp(ctime, tz=TZ).strftime("%Y-%m-%d %H:%M:%S")
            tam_kb = round(os.path.getsize(path) / 1024.0, 2)
            items.append({"nombre": fname, "fecha": fecha, "tamaño": tam_kb, "ctime": ctime})
        except OSError:
            continue
    items.sort(key=lambda x: x["ctime"], reverse=True)
    for i in items:
        i.pop("ctime", None)
    return items


def _db_exists(mysql_path: str) -> bool:
    """Verifica la existencia exacta de la BD destino."""
    cmd = [mysql_path, "-u", DB_USER, f"-p{DB_PASS}", "-N", "-e",
           f"SHOW DATABASES LIKE '{DB_NAME}';"]
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    if p.returncode != 0:
        print("❌ Error verificando BD:", err.decode("utf-8", errors="ignore"))
        return False
    return out.decode("utf-8", errors="ignore").strip() == DB_NAME


def _popen_to_bytes(cmd):
    """Ejecuta un comando y devuelve (ok, stdout_bytes, stderr_text)."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return (p.returncode == 0, out, err.decode("utf-8", errors="ignore"))


def crear_respaldo_manual() -> bool:
    """
    Genera un .sql con este orden:
    1) Cabecera de SETs
    2) ESQUEMA completo (CREATE DATABASE/TABLE/…)
    3) Bloque 'seguro' para datos (desactiva checks)
    4) DATOS (INSERTs de todas las tablas, sin creates)
    5) Restaura SETs
    """
    mysql_path, mysqldump_path = _find_mysql_binaries()
    if not mysql_path or not mysqldump_path:
        print("❌ No se encontraron mysql.exe / mysqldump.exe.")
        return False

    if not _db_exists(mysql_path):
        print(f"❌ La base de datos '{DB_NAME}' no existe.")
        return False

    fecha = datetime.now(tz=TZ).strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"respaldo_{DB_NAME}_{fecha}.sql"
    ruta_backup = os.path.join(BACKUP_FOLDER, nombre_archivo)

    # -----------------------------
    # 1) Cabecera: SETs iniciales
    # -----------------------------
    header = []
    header.append("/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;")
    header.append("/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;")
    header.append("/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;")
    header.append("/*!50503 SET NAMES utf8mb4 */;")
    header.append("/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;")
    header.append("/*!40103 SET TIME_ZONE='+00:00' */;")
    header.append("/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;")
    header.append("/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;")
    header.append("/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;")
    header.append("/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;")
    header_bytes = ("\n".join(header) + "\n\n").encode("utf-8")

    # ---------------------------------------------------
    # 2) Dump de ESQUEMA (sin datos): --no-data
    #    Incluimos DROP TABLE si quieres restauros limpios.
    # ---------------------------------------------------
    schema_cmd = [
        mysqldump_path,
        "-u", DB_USER, f"-p{DB_PASS}",
        "--databases", DB_NAME,
        "--single-transaction",
        "--quick",
        "--routines",
        "--events",
        "--triggers",               # incluye triggers en esquema
        "--no-tablespaces",
        "--set-gtid-purged=OFF",
        "--skip-comments",
        "--add-drop-table",
        "--no-data",                # <--- SOLO ESQUEMA
    ]
    ok_schema, schema_bytes, schema_err = _popen_to_bytes(schema_cmd)
    if not ok_schema:
        print("❌ Error al volcar ESQUEMA:", schema_err)
        return False

    # ------------------------------------------------------
    # 3) Bloque seguro para datos: desactiva restricciones
    # ------------------------------------------------------
    data_preamble = []
    data_preamble.append("\n-- =========================")
    data_preamble.append("--  DATA SECTION (INSERTs)")
    data_preamble.append("-- =========================\n")
    data_preamble.append("/*!40014 SET FOREIGN_KEY_CHECKS=0 */;")
    data_preamble.append("/*!40014 SET UNIQUE_CHECKS=0 */;")
    data_preamble.append("/*!40101 SET SQL_NOTES=0 */;")
    data_preamble.append("USE `{}`;".format(DB_NAME))
    data_preamble_bytes = ("\n".join(data_preamble) + "\n\n").encode("utf-8")

    # --------------------------------------------
    # 4) Dump de DATOS (sin create): --no-create-info
    #    Ordenamos por PK para consistencia.
    #    No incluimos triggers aquí.
    # --------------------------------------------
    data_cmd = [
        mysqldump_path,
        "-u", DB_USER, f"-p{DB_PASS}",
        DB_NAME,                      # SIN --databases: así no repite el CREATE DATABASE
        "--single-transaction",
        "--quick",
        "--order-by-primary",
        "--no-tablespaces",
        "--set-gtid-purged=OFF",
        "--skip-comments",
        "--lock-tables=FALSE",        # evita locks explícitos
        "--skip-add-locks",
        "--no-create-info",           # <--- SOLO DATOS
        "--skip-triggers",            # no queremos triggers en sección de datos
    ]
    ok_data, data_bytes, data_err = _popen_to_bytes(data_cmd)
    if not ok_data:
        print("❌ Error al volcar DATOS:", data_err)
        return False

    # -------------------------
    # 5) Footer: restaurar SETs
    # -------------------------
    footer = []
    footer.append("\n-- =========================")
    footer.append("--  END DATA SECTION")
    footer.append("-- =========================\n")
    footer.append("/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;")
    footer.append("/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;")
    footer.append("/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;")
    footer.append("/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;")
    footer.append("/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;")
    footer.append("/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;")
    footer.append("/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;")
    footer.append("/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;")
    footer_bytes = ("\n".join(footer) + "\n").encode("utf-8")

    # --------------------------------
    # Ensamblar el archivo final .sql
    # --------------------------------
    try:
        with open(ruta_backup, "wb") as f:
            f.write(header_bytes)        # SETs iniciales
            f.write(schema_bytes)        # ESQUEMA completo
            f.write(data_preamble_bytes) # preámbulo de datos
            f.write(data_bytes)          # INSERTs de todas las tablas
            f.write(footer_bytes)        # restaura SETs
        print(f"✅ Respaldo (esquema → datos) generado: {nombre_archivo}")
        return True
    except Exception as e:
        print("⚠️ Error escribiendo el respaldo:", e)
        try:
            os.remove(ruta_backup)
        except OSError:
            pass
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
    ok = crear_respaldo_manual()
    flash("✅ Respaldo creado exitosamente." if ok else "❌ No se pudo crear el respaldo.",
          "success" if ok else "danger")
    return redirect(url_for("respaldo.panel_respaldo"))


@respaldo_bp.route("/admin/respaldo/descargar/<nombre>")
def descargar_respaldo(nombre):
    safe = _safe_filename(nombre)
    if not safe:
        flash("Nombre de archivo inválido.", "danger")
        return redirect(url_for("respaldo.panel_respaldo"))

    ruta = os.path.join(BACKUP_FOLDER, safe)
    if not os.path.exists(ruta):
        flash("Archivo no encontrado.", "danger")
        return redirect(url_for("respaldo.panel_respaldo"))

    return send_file(ruta, as_attachment=True, mimetype="text/plain")


@respaldo_bp.route("/admin/respaldo/eliminar/<nombre>", methods=["POST"])
def eliminar_respaldo(nombre):
    safe = _safe_filename(nombre)
    if not safe:
        flash("Nombre de archivo inválido.", "danger")
        return redirect(url_for("respaldo.panel_respaldo"))

    ruta = os.path.join(BACKUP_FOLDER, safe)
    if os.path.exists(ruta):
        try:
            os.remove(ruta)
            flash("🗑️ Respaldo eliminado correctamente.", "success")
        except OSError as e:
            print("⚠️ Error al eliminar:", e)
            flash("❌ No se pudo eliminar el respaldo.", "danger")
    else:
        flash("Archivo no encontrado.", "danger")
    return redirect(url_for("respaldo.panel_respaldo"))

def _get_mysql_client():
    mysql_path, _ = _find_mysql_binaries()
    return mysql_path

@respaldo_bp.route("/admin/respaldo/restaurar/<nombre>", methods=["POST"])
def restaurar_respaldo(nombre):
    """Restaura la BD desde un .sql (usa mysql client vía stdin, sin redirecciones)."""
    safe = _safe_filename(nombre)
    if not safe:
        flash("Nombre de archivo inválido.", "danger")
        return redirect(url_for("respaldo.panel_respaldo"))

    ruta_sql = os.path.join(BACKUP_FOLDER, safe)
    if not os.path.exists(ruta_sql):
        flash("Archivo de respaldo no encontrado.", "danger")
        return redirect(url_for("respaldo.panel_respaldo"))

    mysql_path = _get_mysql_client()
    if not mysql_path:
        flash("❌ No se encontró mysql.exe en el sistema.", "danger")
        return redirect(url_for("respaldo.panel_respaldo"))

    # Asegura que la BD destino exista antes de restaurar
    if not _db_exists(mysql_path):
        # Crea la BD si no existe (para evitar errores de USE en el dump)
        create_cmd = [mysql_path, "-u", DB_USER, f"-p{DB_PASS}", "-e",
                      f"CREATE DATABASE IF NOT EXISTS `{DB_NAME}`;"]
        cp = subprocess.Popen(create_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        _, cerr = cp.communicate()
        if cp.returncode != 0:
            print("❌ Error creando BD antes de restaurar:", cerr.decode("utf-8", errors="ignore"))
            flash("❌ No se pudo preparar la base de datos destino.", "danger")
            return redirect(url_for("respaldo.panel_respaldo"))

    # mysql -u USER -pPASS BD_NAME  < archivo.sql (usamos stdin)
    cmd = [mysql_path, "-u", DB_USER, f"-p{DB_PASS}", DB_NAME]
    try:
        with open(ruta_sql, "rb") as entrada:
            p = subprocess.Popen(cmd, stdin=entrada, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            _, err = p.communicate()

        if p.returncode == 0:
            flash("✅ Base de datos restaurada correctamente.", "success")
        else:
            print("❌ Error al restaurar:", err.decode("utf-8", errors="ignore"))
            flash("❌ Error al restaurar la base de datos. Revisa la consola.", "danger")
    except Exception as e:
        print("⚠️ Excepción al restaurar:", e)
        flash(f"⚠️ Error inesperado: {e}", "danger")

    return redirect(url_for("respaldo.panel_respaldo"))


# ==============================================
# 🔄 TAREA AUTOMÁTICA DIARIA (evita doble arranque)
# ==============================================
_scheduler = BackgroundScheduler(timezone=TZ)

def programar_respaldo_automatico():
    """Programa un respaldo diario a las 02:00 America/Lima (una sola vez)."""
    # Evita doble scheduler con el reloader de Flask
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        # Ya es el proceso hijo (reloader) -> no inicializar de nuevo
        return

    if not _scheduler.running:
        _scheduler.add_job(
            crear_respaldo_manual,
            trigger="cron",
            id="respaldo_diario_02am",
            hour=2, minute=0,
            replace_existing=True,
            misfire_grace_time=3600,  # 1h de tolerancia
            coalesce=True
        )
        _scheduler.start()
        print("🕑 Tarea de respaldo automático programada (diaria 02:00).")


# Llama una vez al importar el blueprint (seguro con guardado anterior)
programar_respaldo_automatico()
