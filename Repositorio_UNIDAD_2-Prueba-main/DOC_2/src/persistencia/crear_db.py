"""Creación de esquema para el motor seleccionado en .env (MySQL o SQLite)."""
from persistencia.conexion import abrir_conexion, abrir_conexion_servidor, obtener_configuracion, obtener_motor


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
                correo TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                activo INTEGER NOT NULL DEFAULT 1,
                fecha_creacion TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (id_empleado) REFERENCES empleado(id_empleado)
                    ON UPDATE CASCADE ON DELETE CASCADE
            )""",
        ]
        for sql in sentencias:
            cursor.execute(sql)
        conexion.commit()
    except Exception:
        conexion.rollback()
        raise
    finally:
        cursor.close()
        conexion.close()


def crear_base_y_tablas():
    if obtener_motor() == "sqlite":
        _crear_sqlite()
        return

    config = obtener_configuracion()
    nombre_bd = config["database"]
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
            correo VARCHAR(150) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            activo TINYINT(1) NOT NULL DEFAULT 1,
            fecha_creacion TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
            CONSTRAINT fk_usuario_empleado FOREIGN KEY (id_empleado)
                REFERENCES empleado(id_empleado) ON UPDATE CASCADE ON DELETE CASCADE
        ) ENGINE=InnoDB""")

        # Migraciones compatibles con bases existentes creadas por versiones previas.
        cursor.execute("""SELECT COUNT(*) FROM information_schema.COLUMNS
            WHERE TABLE_SCHEMA=%s AND TABLE_NAME='departamento' AND COLUMN_NAME='id_gerente'""", (nombre_bd,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("ALTER TABLE departamento ADD COLUMN id_gerente INT NULL")
        cursor.execute("""SELECT COUNT(*) FROM information_schema.TABLE_CONSTRAINTS
            WHERE CONSTRAINT_SCHEMA=%s AND TABLE_NAME='departamento'
            AND CONSTRAINT_NAME='fk_departamento_gerente'""", (nombre_bd,))
        if cursor.fetchone()[0] == 0:
            cursor.execute("""ALTER TABLE departamento ADD CONSTRAINT fk_departamento_gerente
                FOREIGN KEY (id_gerente) REFERENCES empleado(id_empleado)
                ON UPDATE CASCADE ON DELETE SET NULL""")
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
