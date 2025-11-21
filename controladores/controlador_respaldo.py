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


def crear_respaldo_manual(subir_a_nube=True) -> bool:
    """
    Genera un .sql con este orden:
    1) Cabecera de SETs
    2) ESQUEMA completo (CREATE DATABASE/TABLE/…)
    3) Bloque 'seguro' para datos (desactiva checks)
    4) DATOS (INSERTs de todas las tablas, sin creates)
    5) Restaura SETs
    Si subir_a_nube=True, también lo sube automáticamente a Dropbox.
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
    header = [
        "/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;",
        "/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;",
        "/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;",
        "/*!50503 SET NAMES utf8mb4 */;",
        "/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;",
        "/*!40103 SET TIME_ZONE='+00:00' */;",
        "/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;",
        "/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;",
        "/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;",
        "/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;"
    ]
    header_bytes = ("\n".join(header) + "\n\n").encode("utf-8")

    # ---------------------------------------------------
    # 2) Dump de ESQUEMA (sin datos)
    # ---------------------------------------------------
    schema_cmd = [
        mysqldump_path,
        "-u", DB_USER, f"-p{DB_PASS}",
        "--databases", DB_NAME,
        "--single-transaction",
        "--quick",
        "--routines",
        "--events",
        "--triggers",
        "--no-tablespaces",
        "--set-gtid-purged=OFF",
        "--skip-comments",
        "--add-drop-table",
        "--no-data",
    ]
    ok_schema, schema_bytes, schema_err = _popen_to_bytes(schema_cmd)
    if not ok_schema:
        print("❌ Error al volcar ESQUEMA:", schema_err)
        return False

    # ------------------------------------------------------
    # 3) Bloque seguro para datos
    # ------------------------------------------------------
    data_preamble = [
        "\n-- =========================",
        "--  DATA SECTION (INSERTs)",
        "-- =========================\n",
        "/*!40014 SET FOREIGN_KEY_CHECKS=0 */;",
        "/*!40014 SET UNIQUE_CHECKS=0 */;",
        "/*!40101 SET SQL_NOTES=0 */;",
        f"USE `{DB_NAME}`;"
    ]
    data_preamble_bytes = ("\n".join(data_preamble) + "\n\n").encode("utf-8")

    # --------------------------------------------
    # 4) Dump de DATOS (sin create)
    # --------------------------------------------
    data_cmd = [
        mysqldump_path,
        "-u", DB_USER, f"-p{DB_PASS}",
        DB_NAME,
        "--single-transaction",
        "--quick",
        "--order-by-primary",
        "--no-tablespaces",
        "--set-gtid-purged=OFF",
        "--skip-comments",
        "--lock-tables=FALSE",
        "--skip-add-locks",
        "--no-create-info",
        "--skip-triggers",
    ]
    ok_data, data_bytes, data_err = _popen_to_bytes(data_cmd)
    if not ok_data:
        print("❌ Error al volcar DATOS:", data_err)
        return False

    # -------------------------
    # 5) Footer: restaurar SETs
    # -------------------------
    footer = [
        "\n-- =========================",
        "--  END DATA SECTION",
        "-- =========================\n",
        "/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;",
        "/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;",
        "/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;",
        "/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;",
        "/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;",
        "/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;",
        "/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;",
        "/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;"
    ]
    footer_bytes = ("\n".join(footer) + "\n").encode("utf-8")

    # --------------------------------
    # Ensamblar el archivo final .sql
    # --------------------------------
    try:
        with open(ruta_backup, "wb") as f:
            f.write(header_bytes)
            f.write(schema_bytes)
            f.write(data_preamble_bytes)
            f.write(data_bytes)
            f.write(footer_bytes)

        print(f"✅ Respaldo generado correctamente: {nombre_archivo}")

        # Subir respaldo automáticamente a Dropbox (solo si está habilitado)
        if subir_a_nube:
            subido = subir_a_dropbox(ruta_backup, nombre_archivo)
            if subido:
                print("✅ Copia del respaldo almacenada en Dropbox correctamente.")
            else:
                print("⚠️ No se pudo subir el respaldo a Dropbox (revisar token o conexión).")

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
# 🔄 TAREA AUTOMÁTICA (local diario + nube cada 2 días)
# ==============================================
_scheduler = BackgroundScheduler(timezone=TZ)

def respaldo_automatico_programado():
    """
    Se ejecuta todos los días a las 02:00 AM.
    - Siempre genera respaldo local.
    - Cada 2 días también lo sube a Dropbox.
    """
    hoy = datetime.now(tz=TZ).date()
    subir_nube = (hoy.toordinal() % 2 == 0)

    if subir_nube:
        print("☁️ Hoy toca respaldo local + Dropbox")
        crear_respaldo_manual(subir_a_nube=True)
    else:
        print("💾 Hoy toca solo respaldo local")
        crear_respaldo_manual(subir_a_nube=False)


def programar_respaldo_automatico():
    # Evita doble scheduler con el reloader de Flask
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        return

    if not _scheduler.running:
        _scheduler.add_job(
            respaldo_automatico_programado,
            trigger="cron",
            id="respaldo_automatico_02am",
            hour=2,
            minute=0,
            replace_existing=True,
            misfire_grace_time=3600,
            coalesce=True,
        )
        _scheduler.start()
        print("🕑 Respaldo automático programado: local diario 02:00, nube cada 2 días 02:00.")

programar_respaldo_automatico()

import dropbox

# ==============================================
# ☁️ CONFIGURACIÓN DROPBOX
# ==============================================
#DROPBOX_TOKEN = os.getenv("DROPBOX_TOKEN", "sl.u.AGFcwwBn1x45ENarhhf3mk3Rrm53gss95JX44aJ9EyZyYaRDkBZ-JnPHzm4xGpB4EtIVsCwdYrtco_YC917ypWTSMgY9FBkjI1zZB3gkJWR5jl_1UzDUIyUADaySUj58WoOzpHd-ggVgv2s_pGInGofqCuLbh4bBFLI2GKt8TZH4OrunhPnvmrB-q4pxJc2agj7gr_u_ZHTooRPUjoJ_RWYjAYDVOFo8Na2FuwPWKA5ysXsnTStbu5ECmrWxzxzThW5bfQSuT3HyTyfxVBI4qBqyx1ScW5_exfJC8L0wFsSGLMZm0gkogZJm2CUDQG-z4XWvLOZTAgVkkajwl2AwJlHEaWCBjVSlYODJSMG14yHjcBDfHYkQMTIQVHT8WjV4O9fFNswBokOeDfFHHUajoxytojQW0EXxQw-0I8ofeu_n9xXoVWVrDm2gtu9BXKqWb0jrV52ULkPwLovrqg2L-Neo4Y1a6KntVneL6xN6Sft66KosEDMhT9k5tUyJH43jESzjrELmqbrvCi-gEK3xkx81TE95ck4Wn2UaOTcs8zgWMl89ZLG_tFOEDfm8xJuwNQRhWTDeJxaXZUUNU8gRfyjnif1n803TLZND8dnB65QTELBPP2xVM5ssQJVL0MjXCKE-q99FxREZfaKWq40v3a5ZBWnpxjsUBg5V9bssjbk8NYLtdo8qk6loqQcFbcAAvb8xx9wbqQwfLDKkFhy6JWnjbRjxJebslfGmrSqEIgQilII1ZFn-VtSAEpmoMMRPNP-YybK-Hgm8VA12gNJcNDDztR77397IPhi_D3REtdtDhkF2Y1MLR0g1uV2MPkSFpU-XCoBNDqEJ3gnmmSGkAlisa3IZzRhZ0K8y4PVQXW4KjI2T2g07CgQpFtvlvmOOcjNULqhHkBijNA7f095ml8ZgpFOuV9yrUXZ15RhDqLlsYP0M0thy3_IDvLvB-L8pxrj-H9eqcMVIv_2DuxzdHB3wgTr1NOWVcmTyNYissF2fSWVs4QLlqr5YIIrt6YI4RjJ9qnq0bncbLk9uF05xnX6okvRV9mo6iRqGbLOGuk1Lu6b7B1I0CsayE8MQJcKUmihfF_JDbjMQ5zsn1YHVNsNFZuW_acacL8zhdqSQdwJhJDJlva3YVCsStVXkb1ICGB0zoOVkqFxmUWf1ArxN5UF5dE_VXSYcvzxkKYsfAjxBapDDn_aN0ObdpCM8f_YoTF-E8C51ou8cfNuK7vrE5_JRyzySba7D5BwaTeo0SOdMjI7ANMYb_2J-sW2PZiVnZfvr86kZXN_AwSlNCwpALBK6e0feggBBNB-V-Pz2tgVfwygY46mwhD8wdg1JKClcb8Fq5lXXJSQMY9aAOn5zrGaKnymozUMO9BK6b--BVCTGXi4Azok5jNuQHOPQB3esWGXAcRB1dmAAU18V0grvRg5-V7TpXBjFtPszLLshm6oEew")

def subir_a_dropbox(ruta_local, nombre_archivo):
    """Sube archivo usando refresh token (token oficial que NO expira)."""
    try:
        dbx = dropbox.Dropbox(
            oauth2_refresh_token=os.getenv("DROPBOX_REFRESH_TOKEN"),
            app_key=os.getenv("DROPBOX_APP_KEY"),
            app_secret=os.getenv("DROPBOX_APP_SECRET")
        )

        destino = f"/backups/{nombre_archivo}"

        with open(ruta_local, "rb") as f:
            dbx.files_upload(
                f.read(),
                destino,
                mode=dropbox.files.WriteMode("overwrite")
            )

        print(f"☁️ Respaldo subido a Dropbox: {destino}")
        return True

    except Exception as e:
        print(f"❌ Error al subir a Dropbox: {e}")
        return False
