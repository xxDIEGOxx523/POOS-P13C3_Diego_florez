"""Creación y migración del esquema para MySQL o SQLite."""
import re

from persistencia.conexion import (
    abrir_conexion, abrir_conexion_servidor, obtener_configuracion, obtener_motor
)


def _nombre_usuario_desde_correo(correo, usado):
    base = (correo or "usuario").split("@", 1)[0].strip().lower()
    base = re.sub(r"[^a-z0-9_]", "_", base)
    base = re.sub(r"_+", "_", base).strip("_") or "usuario"
    base = base[:40]
    if len(base) < 3:
        base = (base + "_usr")[:40]
    candidato = base
    contador = 2
    while candidato in usado:
        sufijo = f"_{contador}"
        candidato = base[:40 - len(sufijo)] + sufijo
        contador += 1
    usado.add(candidato)
    return candidato


def _migrar_usuario_sqlite(cursor):
    cursor.execute("PRAGMA table_info(usuario)")
    columnas = {fila[1] for fila in cursor.fetchall()}
    agrego_rol = False

    if "nombre_usuario" not in columnas:
        cursor.execute("ALTER TABLE usuario ADD COLUMN nombre_usuario TEXT")
    if "rol" not in columnas:
        cursor.execute(
            "ALTER TABLE usuario ADD COLUMN rol TEXT NOT NULL DEFAULT 'empleado' "
            "CHECK (rol IN ('admin', 'empleado'))"
        )
        agrego_rol = True

    cursor.execute("SELECT id_usuario, correo, nombre_usuario FROM usuario ORDER BY id_usuario")
    filas = cursor.fetchall()
    usados = set()
    for fila in filas:
        nombre = fila[2]
        if not nombre:
            nombre = _nombre_usuario_desde_correo(fila[1], usados)
            cursor.execute(
                "UPDATE usuario SET nombre_usuario=%s WHERE id_usuario=%s",
                (nombre, fila[0]),
            )
        else:
            nombre = str(nombre).strip().lower()
            usados.add(nombre)
    cursor.execute("PRAGMA index_list(usuario)")
    indices = cursor.fetchall()
    existe_indice_usuario = False
    for indice in indices:
        if indice[2]:
            cursor.execute(f"PRAGMA index_info('{indice[1]}')")
            columnas_indice = [fila[2] for fila in cursor.fetchall()]
            if columnas_indice == ["nombre_usuario"]:
                existe_indice_usuario = True
                break
    if not existe_indice_usuario:
        cursor.execute(
            "CREATE UNIQUE INDEX idx_usuario_nombre_usuario "
            "ON usuario(nombre_usuario)"
        )
    # Migración puntual de la cuenta demo histórica. La semilla normal no cambia roles.
    if agrego_rol:
        cursor.execute(
            "UPDATE usuario SET rol='admin' WHERE correo='admin@ecotech.local'"
        )


def _crear_sqlite():
    conexion = abrir_conexion()
    cursor = conexion.cursor()
    try:
        sentencias = [
            """CREATE TABLE IF NOT EXISTS departamento (
                id_departamento INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL UNIQUE,
                id_gerente INTEGER NULL,
                FOREIGN KEY (id_gerente) REFERENCES empleado(id_empleado)
                    ON UPDATE CASCADE ON DELETE SET NULL
            )""",
            """CREATE TABLE IF NOT EXISTS empleado (
                id_empleado INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                direccion TEXT NOT NULL,
                telefono TEXT NOT NULL,
                correo TEXT NOT NULL UNIQUE,
                fecha_inicio_contrato TEXT NOT NULL,
                salario NUMERIC NOT NULL,
                id_departamento INTEGER NULL,
                FOREIGN KEY (id_departamento) REFERENCES departamento(id_departamento)
                    ON UPDATE CASCADE ON DELETE SET NULL
            )""",
            """CREATE TABLE IF NOT EXISTS proyecto (
                id_proyecto INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                fecha_inicio TEXT NOT NULL
            )""",
            """CREATE TABLE IF NOT EXISTS empleado_proyecto (
                id_empleado INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                PRIMARY KEY (id_empleado, id_proyecto),
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS registro_tiempo (
                id_registro INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL,
                id_proyecto INTEGER NOT NULL,
                fecha TEXT NOT NULL,
                horas_trabajadas NUMERIC NOT NULL,
                descripcion_trabajo TEXT NOT NULL,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
                FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS usuario (
                id_usuario INTEGER PRIMARY KEY AUTOINCREMENT,
                id_empleado INTEGER NOT NULL UNIQUE,
                nombre_usuario TEXT NOT NULL UNIQUE,
                correo TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                rol TEXT NOT NULL DEFAULT 'empleado'
                    CHECK (rol IN ('admin', 'empleado')),
                activo INTEGER NOT NULL DEFAULT 1,
                fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )""",
            """CREATE TABLE IF NOT EXISTS indicador_api (
                id_indicador INTEGER PRIMARY KEY AUTOINCREMENT,
                fuente TEXT NOT NULL,
                codigo TEXT NOT NULL,
                fecha TEXT NOT NULL,
                valor REAL NOT NULL,
                unidad TEXT NOT NULL,
                verificado_en TEXT NOT NULL,
                UNIQUE (fuente, codigo, fecha)
            )""",
        ]
        for sql in sentencias:
            cursor.execute(sql)
        _migrar_usuario_sqlite(cursor)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def _migrar_usuario_mysql(cursor, nombre_bd):
    cursor.execute("""SELECT COLUMN_NAME FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME='usuario'""", (nombre_bd,))
    columnas = {fila[0] for fila in cursor.fetchall()}
    agrego_rol = False

    if "nombre_usuario" not in columnas:
        cursor.execute("ALTER TABLE usuario ADD COLUMN nombre_usuario VARCHAR(40) NULL")
    if "rol" not in columnas:
        cursor.execute(
            "ALTER TABLE usuario ADD COLUMN rol ENUM('admin','empleado') "
            "NOT NULL DEFAULT 'empleado'"
        )
        agrego_rol = True

    cursor.execute(
        "SELECT id_usuario, correo, nombre_usuario FROM usuario ORDER BY id_usuario"
    )
    filas = cursor.fetchall()
    usados = set()
    for fila in filas:
        nombre = fila[2]
        if not nombre:
            nombre = _nombre_usuario_desde_correo(fila[1], usados)
            cursor.execute(
                "UPDATE usuario SET nombre_usuario=%s WHERE id_usuario=%s",
                (nombre, fila[0]),
            )
        else:
            usados.add(str(nombre).strip().lower())

    cursor.execute("""SELECT COUNT(*) FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA=%s AND TABLE_NAME='usuario'
          AND COLUMN_NAME='nombre_usuario' AND NON_UNIQUE=0""",
        (nombre_bd,))
    if cursor.fetchone()[0] == 0:
        cursor.execute(
            "ALTER TABLE usuario ADD UNIQUE INDEX uq_usuario_nombre_usuario (nombre_usuario)"
        )
    cursor.execute("ALTER TABLE usuario MODIFY nombre_usuario VARCHAR(40) NOT NULL")
    if agrego_rol:
        cursor.execute(
            "UPDATE usuario SET rol='admin' WHERE correo='admin@ecotech.local'"
        )


def crear_base_y_tablas():
    if obtener_motor() == "sqlite":
        _crear_sqlite()
        return

    config = obtener_configuracion()
    nombre_bd = config["database"]
    if not re.fullmatch(r"[A-Za-z0-9_]+", nombre_bd):
        raise ValueError("DB_NAME solo puede contener letras, números y guion bajo.")

    conexion = abrir_conexion_servidor()
    cursor = conexion.cursor()
    try:
        cursor.execute(
            f"CREATE DATABASE IF NOT EXISTS `{nombre_bd}` "
            "CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        )
        conexion.commit()
    finally:
        cursor.close()
        conexion.close()

    conexion = abrir_conexion()
    cursor = conexion.cursor()
    try:
        cursor.execute("""CREATE TABLE IF NOT EXISTS departamento (
            id_departamento INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL UNIQUE,
            id_gerente INT NULL
        ) ENGINE=InnoDB""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS empleado (
            id_empleado INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            direccion VARCHAR(200) NOT NULL,
            telefono VARCHAR(30) NOT NULL,
            correo VARCHAR(150) NOT NULL UNIQUE,
            fecha_inicio_contrato DATE NOT NULL,
            salario DECIMAL(12,2) NOT NULL,
            id_departamento INT NULL,
            CONSTRAINT fk_empleado_departamento FOREIGN KEY (id_departamento)
                REFERENCES departamento(id_departamento) ON UPDATE CASCADE ON DELETE SET NULL
        ) ENGINE=InnoDB""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS proyecto (
            id_proyecto INT AUTO_INCREMENT PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion VARCHAR(500) NOT NULL,
            fecha_inicio DATE NOT NULL
        ) ENGINE=InnoDB""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS empleado_proyecto (
            id_empleado INT NOT NULL, id_proyecto INT NOT NULL,
            PRIMARY KEY (id_empleado, id_proyecto),
            FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
            FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
        ) ENGINE=InnoDB""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS registro_tiempo (
            id_registro INT AUTO_INCREMENT PRIMARY KEY,
            id_empleado INT NOT NULL, id_proyecto INT NOT NULL,
            fecha DATE NOT NULL, horas_trabajadas DECIMAL(5,2) NOT NULL,
            descripcion_trabajo VARCHAR(500) NOT NULL,
            FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado) ON DELETE CASCADE,
            FOREIGN KEY (id_proyecto) REFERENCES proyecto(id_proyecto) ON DELETE CASCADE
        ) ENGINE=InnoDB""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS usuario (
            id_usuario INT AUTO_INCREMENT PRIMARY KEY,
            id_empleado INT NOT NULL UNIQUE,
            nombre_usuario VARCHAR(40) NOT NULL UNIQUE,
            correo VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            rol ENUM('admin','empleado') NOT NULL DEFAULT 'empleado',
            activo TINYINT(1) NOT NULL DEFAULT 1,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_usuario_empleado FOREIGN KEY (id_empleado)
                REFERENCES empleado(id_empleado) ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB""")
        cursor.execute("""CREATE TABLE IF NOT EXISTS indicador_api (
            id_indicador BIGINT AUTO_INCREMENT PRIMARY KEY,
            fuente VARCHAR(80) NOT NULL,
            codigo VARCHAR(40) NOT NULL,
            fecha DATE NOT NULL,
            valor DECIMAL(18,6) NOT NULL,
            unidad VARCHAR(30) NOT NULL,
            verificado_en VARCHAR(40) NOT NULL,
            UNIQUE KEY uq_indicador_observacion (fuente, codigo, fecha)
        ) ENGINE=InnoDB""")

        # Migraciones compatibles con esquemas de versiones previas.
        cursor.execute("""SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME='departamento' AND COLUMN_NAME='id_gerente'""",
            (nombre_bd,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE departamento ADD COLUMN id_gerente INT NULL")
        cursor.execute("""SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA=%s AND TABLE_NAME='departamento'
            AND CONSTRAINT_NAME='fk_departamento_gerente'""", (nombre_bd,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""ALTER TABLE departamento ADD CONSTRAINT fk_departamento_gerente
                FOREIGN KEY (id_gerente) REFERENCES empleado(id_empleado)
                ON UPDATE CASCADE ON DELETE SET NULL""")

        _migrar_usuario_mysql(cursor, nombre_bd)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    crear_base_y_tablas()
    print(f"Base de datos preparada correctamente para {obtener_motor()}.")
