
import os

import mysql.connector
from dotenv import load_dotenv

load_dotenv()


def obtener_configuracion():
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "user": os.getenv("DB_USER", "root"),
        "password": os.getenv("DB_PASSWORD", ""),
        "database": os.getenv("DB_NAME", "ecotech_db"),
        "charset": "utf8mb4",
        "collation": "utf8mb4_unicode_ci",
    }


def abrir_conexion():
    try:
        return mysql.connector.connect(**obtener_configuracion())
    except mysql.connector.Error as e:
        raise ConnectionError(
            f"No fue posible conectar con MySQL: {e}"
        ) from e


def abrir_conexion_servidor():
    config = obtener_configuracion()
    config.pop("database", None)

    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as e:
        raise ConnectionError(
            f"No fue posible conectar con el servidor MySQL: {e}"
        ) from e

