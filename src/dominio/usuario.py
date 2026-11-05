"""Entidad Usuario: cuenta de acceso vinculada obligatoriamente a un empleado."""


class Usuario:
    MIN_USUARIO = 3
    MAX_USUARIO = 40
    MIN_CLAVE = 6
    ROLES = ("admin", "empleado")

    def __init__(self, nombre_usuario, password_hash, empleado_id, id=None, rol="empleado"):
        if type(empleado_id) is not int or empleado_id <= 0:
            raise ValueError("El ID del empleado debe ser un entero positivo.")
        if not isinstance(password_hash, str) or not password_hash.strip():
            raise ValueError("La cuenta debe contener un hash de contraseña válido.")
        self.id = id
        self.empleado_id = empleado_id
        self.nombre_usuario = self.normalizar_usuario(nombre_usuario)
        self.password_hash = password_hash
        self.rol = self.validar_rol(rol)

    @classmethod
    def normalizar_usuario(cls, nombre):
        if not isinstance(nombre, str):
            raise TypeError("El nombre de usuario debe ser texto.")
        nombre = nombre.strip().lower()
        if not cls.MIN_USUARIO <= len(nombre) <= cls.MAX_USUARIO:
            raise ValueError(
                f"El nombre de usuario debe tener entre {cls.MIN_USUARIO} y {cls.MAX_USUARIO} caracteres."
            )
        if not all(c.isascii() and (c.isalnum() or c == "_") for c in nombre):
            raise ValueError("Use solo letras ASCII, números o guion bajo en el usuario.")
        return nombre

    @classmethod
    def validar_clave(cls, clave):
        """Valida una contraseña nueva sin alterar espacios ni mayúsculas."""
        if not isinstance(clave, str):
            raise TypeError("La contraseña debe ser texto.")
        if len(clave) < cls.MIN_CLAVE:
            raise ValueError(f"Use al menos {cls.MIN_CLAVE} caracteres.")
        return clave

    @classmethod
    def validar_rol(cls, rol):
        if not isinstance(rol, str) or rol not in cls.ROLES:
            raise ValueError("Rol no permitido. Use 'admin' o 'empleado'.")
        return rol
