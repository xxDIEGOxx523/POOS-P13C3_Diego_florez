"""Registro, hash de contraseñas y autenticación con bcrypt."""
import re
import bcrypt

from dominio.usuario import Usuario
from servicios.permisos import exigir_admin


class Autenticacion:
    MAX_BYTES_BCRYPT = 72

    def __init__(self, usuario_dao, empleado_dao):
        self.usuario_dao = usuario_dao
        self.empleado_dao = empleado_dao

    @staticmethod
    def validar_password(password):
        password = Usuario.validar_clave(password)
        if len(password) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres.")
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise ValueError("La contraseña debe incluir letras y números.")
        if len(password.encode("utf-8")) > Autenticacion.MAX_BYTES_BCRYPT:
            raise ValueError("La contraseña supera el máximo admitido por bcrypt (72 bytes).")
        return password

    @classmethod
    def crear_hash(cls, password):
        password = cls.validar_password(password)
        return bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt(rounds=12)
        ).decode("utf-8")

    def _crear_cuenta(self, id_empleado, nombre_usuario, password, rol):
        if type(id_empleado) is not int or id_empleado <= 0:
            raise ValueError("El ID del empleado debe ser un entero positivo.")
        empleado = self.empleado_dao.obtener_por_id(id_empleado)
        if empleado is None:
            raise ValueError("No existe el empleado asociado a la cuenta.")

        nombre_usuario = Usuario.normalizar_usuario(nombre_usuario)
        if self.usuario_dao.buscar_por_nombre(nombre_usuario):
            raise ValueError("Ya existe una cuenta con ese nombre de usuario.")
        if self.usuario_dao.existe_para_empleado(id_empleado):
            raise ValueError("Este empleado ya tiene una cuenta.")

        rol = Usuario.validar_rol(rol)
        hash_guardado = self.crear_hash(password)
        cuenta = Usuario(nombre_usuario, hash_guardado, id_empleado, rol=rol)
        correo = empleado.get("correo")
        if not isinstance(correo, str) or not correo.strip():
            raise ValueError("El empleado debe tener un correo válido para registrar su cuenta.")
        return self.usuario_dao.crear(
            id_empleado, cuenta.nombre_usuario, correo.strip().lower(),
            cuenta.password_hash, cuenta.rol
        )

    def registrar(self, sesion, id_empleado, nombre_usuario, password):
        """Crea una cuenta habitual. Solo un administrador puede ejecutar esta operación."""
        exigir_admin(sesion)
        return self._crear_cuenta(id_empleado, nombre_usuario, password, "empleado")

    def crear_cuenta_inicial(self, id_empleado, nombre_usuario, password):
        """Prepara la cuenta admin inicial desde main/semilla, no desde el menú público."""
        return self._crear_cuenta(id_empleado, nombre_usuario, password, "admin")

    def cambiar_password(self, usuario_id, password_actual, password_nueva):
        """Verifica la contraseña actual antes de guardar un nuevo hash."""
        usuario = self.usuario_dao.buscar_por_id(usuario_id)
        if not usuario or not isinstance(password_actual, str):
            raise ValueError("La contraseña actual es incorrecta.")
        actual_bytes = password_actual.encode("utf-8")
        if not 0 < len(actual_bytes) <= self.MAX_BYTES_BCRYPT:
            raise ValueError("La contraseña actual es incorrecta.")
        try:
            coincide = bcrypt.checkpw(actual_bytes, usuario["password_hash"].encode("utf-8"))
        except (ValueError, TypeError):
            coincide = False
        if not coincide:
            raise ValueError("La contraseña actual es incorrecta.")
        nuevo_hash = self.crear_hash(password_nueva)
        return self.usuario_dao.actualizar_hash(usuario_id, nuevo_hash)

    def autenticar(self, nombre_usuario, password):
        """Devuelve la sesión autenticada o None, sin exponer password_hash."""
        if not isinstance(password, str):
            return None
        try:
            nombre_usuario = Usuario.normalizar_usuario(nombre_usuario)
        except (TypeError, ValueError):
            return None

        clave_bytes = password.encode("utf-8")
        if not 0 < len(clave_bytes) <= self.MAX_BYTES_BCRYPT:
            return None
        cuenta = self.usuario_dao.buscar_por_nombre(nombre_usuario)
        if not cuenta or not cuenta.get("activo"):
            return None
        try:
            Usuario.validar_rol(cuenta.get("rol"))
            valido = bcrypt.checkpw(clave_bytes, cuenta["password_hash"].encode("utf-8"))
        except (ValueError, TypeError, KeyError):
            return None
        if not valido:
            return None
        return {
            "id": cuenta["id_usuario"],
            "id_usuario": cuenta["id_usuario"],
            "empleado_id": cuenta["id_empleado"],
            "nombre_usuario": cuenta["nombre_usuario"],
            "rol": cuenta["rol"],
        }
