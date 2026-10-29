"""Registro, hash de contraseñas y autenticación con bcrypt."""
import re
import bcrypt


class Autenticacion:
    def __init__(self, usuario_dao):
        self.usuario_dao = usuario_dao

    @staticmethod
    def validar_password(password):
        if len(password) < 10:
            raise ValueError("La contraseña debe tener al menos 10 caracteres.")
        if not re.search(r"[A-Za-z]", password) or not re.search(r"[0-9]", password):
            raise ValueError("La contraseña debe incluir letras y números.")
        if len(password.encode("utf-8")) > 72:
            raise ValueError("La contraseña supera el máximo admitido por bcrypt (72 bytes).")

    @staticmethod
    def crear_hash(password):
        return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

    def registrar(self, id_empleado, correo, password):
        self.validar_password(password)
        correo = correo.strip().lower()
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", correo):
            raise ValueError("El correo no tiene un formato válido.")
        if self.usuario_dao.buscar_por_correo(correo):
            raise ValueError("Ya existe una cuenta con ese correo.")
        if self.usuario_dao.existe_para_empleado(id_empleado):
            raise ValueError("Este empleado ya tiene una cuenta.")
        return self.usuario_dao.crear(id_empleado, correo, self.crear_hash(password))

    def cambiar_password(self, usuario_id, password_actual, password_nueva):
        """Verifica la contraseña actual antes de guardar un nuevo hash."""
        usuario = self.usuario_dao.buscar_por_id(usuario_id)
        if not usuario or not bcrypt.checkpw(
            password_actual.encode("utf-8"), usuario["password_hash"].encode("utf-8")
        ):
            raise ValueError("La contraseña actual es incorrecta.")
        self.validar_password(password_nueva)
        return self.usuario_dao.actualizar_hash(usuario_id, self.crear_hash(password_nueva))

    def autenticar(self, correo, password):
        usuario = self.usuario_dao.buscar_por_correo(correo.strip().lower())
        if not usuario or not usuario.get("activo"):
            return None
        try:
            valido = bcrypt.checkpw(password.encode("utf-8"), usuario["password_hash"].encode("utf-8"))
        except (ValueError, TypeError):
            return None
        if not valido:
            return None
        return {"id_usuario": usuario["id_usuario"], "id_empleado": usuario["id_empleado"], "correo": usuario["correo"]}
