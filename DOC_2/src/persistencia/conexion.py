"""Conexiones seleccionables para MySQL o SQLite (un motor por ejecución)."""
import os
import sqlite3
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def obtener_motor():
    motor = os.getenv("DB_BACKEND", "mysql").strip().lower()
    if motor not in {"mysql", "sqlite"}:
        raise ValueError("DB_BACKEND debe ser 'mysql' o 'sqlite'.")
    return motor


def obtener_configuracion():
    """Conserva la configuración MySQL anterior por compatibilidad."""
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3307")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "ecotech_db"),
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
    }


class CursorSQLite:
    """Adapta los placeholders %s y cursor(dictionary=True) usados por los DAO."""
    def __init__(self, cursor, dictionary=False):
        self._cursor = cursor
        self._dictionary = dictionary

    def execute(self, sql, params=None):
        sql = sql.replace("%s", "?")
        valores = tuple(_adaptar_valor(v) for v in (params or ()))
        self._cursor.execute(sql, valores)
        return self

    def executemany(self, sql, seq_of_params):
        self._cursor.executemany(sql.replace("%s", "?"), [tuple(_adaptar_valor(v) for v in row) for row in seq_of_params])
        return self

    def fetchone(self):
        fila = self._cursor.fetchone()
        if fila is not None and self._dictionary:
            return dict(fila)
        return fila

    def fetchall(self):
        filas = self._cursor.fetchall()
        if self._dictionary:
            return [dict(f) for f in filas]
        return filas

    @property
    def lastrowid(self):
        return self._cursor.lastrowid

    @property
    def rowcount(self):
        return self._cursor.rowcount

    def close(self):
        self._cursor.close()


def _adaptar_valor(valor):
    if isinstance(valor, (date, datetime)):
        return valor.isoformat(sep=" ") if isinstance(valor, datetime) else valor.isoformat()
    if isinstance(valor, Decimal):
        return str(valor)
    return valor


class ConexionSQLite:
    def __init__(self, conexion):
        self._conexion = conexion

    def cursor(self, dictionary=False):
        return CursorSQLite(self._conexion.cursor(), dictionary=dictionary)

    def commit(self):
        self._conexion.commit()

    def rollback(self):
        self._conexion.rollback()

    def close(self):
        self._conexion.close()


def _ruta_sqlite():
    ruta = os.getenv("SQLITE_PATH", "ecotech.db")
    ruta = Path(ruta).expanduser()
    if not ruta.is_absolute():
        # Estable y predecible: archivo en la raíz del repositorio, independiente
        # de la carpeta desde la que se ejecute main.py.
        raiz = Path(__file__).resolve().parents[3]
        ruta = raiz / ruta
    ruta.parent.mkdir(parents=True, exist_ok=True)
    return ruta


def abrir_conexion():
    motor = obtener_motor()
    if motor == "sqlite":
        try:
            raw = sqlite3.connect(str(_ruta_sqlite()))
            raw.row_factory = sqlite3.Row
            raw.execute("PRAGMA foreign_keys = ON")
            return ConexionSQLite(raw)
        except sqlite3.Error as e:
            raise ConnectionError(f"No fue posible abrir la base SQLite: {e}") from e

    try:
        import mysql.connector
        return mysql.connector.connect(**obtener_configuracion())
    except ImportError as e:
        raise ConnectionError("Falta mysql-connector-python. Instale requirements.txt o seleccione DB_BACKEND=sqlite.") from e
    except Exception as e:
        raise ConnectionError(f"No fue posible conectar con MySQL: {e}") from e


def abrir_conexion_servidor():
    if obtener_motor() == "sqlite":
        # SQLite es un archivo local y no necesita conexión a un servidor.
        return abrir_conexion()
    config = obtener_configuracion()
    config.pop("database", None)
    try:
        import mysql.connector
        return mysql.connector.connect(**config)
    except ImportError as e:
        raise ConnectionError("Falta mysql-connector-python para usar MySQL.") from e
    except Exception as e:
        raise ConnectionError(f"No fue posible conectar con el servidor MySQL: {e}") from e
