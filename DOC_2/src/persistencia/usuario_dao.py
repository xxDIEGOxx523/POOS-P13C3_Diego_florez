"""Acceso a datos de las cuentas de usuario."""
from persistencia.conexion import abrir_conexion


class UsuarioDAO:
    CAMPOS = "id_usuario, id_empleado, nombre_usuario, correo, password_hash, activo, rol"

    def buscar_por_nombre(self, nombre_usuario):
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {self.CAMPOS} FROM usuario WHERE nombre_usuario=%s LIMIT 1",
                (nombre_usuario.strip().lower(),),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_correo(self, correo):
        """Compatibilidad con versiones anteriores del proyecto."""
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {self.CAMPOS} FROM usuario WHERE correo=%s LIMIT 1",
                (correo.strip().lower(),),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_id(self, id_usuario):
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {self.CAMPOS} FROM usuario WHERE id_usuario=%s LIMIT 1",
                (id_usuario,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def buscar_por_empleado(self, id_empleado):
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                f"SELECT {self.CAMPOS} FROM usuario WHERE id_empleado=%s LIMIT 1",
                (id_empleado,),
            )
            return cursor.fetchone()
        finally:
            cursor.close()
            conexion.close()

    def existe_para_empleado(self, id_empleado):
        return self.buscar_por_empleado(id_empleado) is not None

    def crear(self, id_empleado, nombre_usuario, correo, password_hash, rol="empleado"):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(
                """INSERT INTO usuario
                   (id_empleado, nombre_usuario, correo, password_hash, rol)
                   VALUES (%s, %s, %s, %s, %s)""",
                (id_empleado, nombre_usuario, correo.strip().lower(), password_hash, rol),
            )
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
            cursor.execute(
                "UPDATE usuario SET password_hash=%s WHERE id_usuario=%s",
                (password_hash, id_usuario),
            )
            conexion.commit()
            return cursor.rowcount > 0
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()
