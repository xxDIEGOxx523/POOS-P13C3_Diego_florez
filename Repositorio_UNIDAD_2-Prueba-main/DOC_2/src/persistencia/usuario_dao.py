"""Acceso a datos de usuarios de EcoTech Solutions (MySQL)."""
from persistencia.conexion import abrir_conexion


class UsuarioDAO:
    def buscar_por_correo(self, correo):
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("""SELECT id_usuario, id_empleado, correo, password_hash, activo
                              FROM usuario WHERE correo=%s LIMIT 1""", (correo.strip().lower(),))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_usuario):
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute("""SELECT id_usuario, id_empleado, correo, password_hash, activo
                              FROM usuario WHERE id_usuario=%s LIMIT 1""", (id_usuario,))
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def existe_para_empleado(self, id_empleado):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT id_usuario FROM usuario WHERE id_empleado=%s LIMIT 1", (id_empleado,))
            return cursor.fetchone() is not None
        finally:
            cursor.close()
            conexion.close()

    def crear(self, id_empleado, correo, password_hash):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""INSERT INTO usuario (id_empleado, correo, password_hash)
                              VALUES (%s, %s, %s)""",
                           (id_empleado, correo.strip().lower(), password_hash))
            conexion.commit()
            return cursor.lastrowid
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    def actualizar_hash(self, id_usuario, password_hash):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("UPDATE usuario SET password_hash=%s WHERE id_usuario=%s",
                           (password_hash, id_usuario))
            conexion.commit()
            return cursor.rowcount > 0
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()
