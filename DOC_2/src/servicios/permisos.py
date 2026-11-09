"""Comprobaciones reutilizables de sesión y autorización."""

from dominio.usuario import Usuario


def exigir_sesion(sesion):
    if not isinstance(sesion, dict):
        raise PermissionError("Inicie sesión para realizar esta acción.")
    try:
        rol = Usuario.validar_rol(sesion.get("rol"))
    except (TypeError, ValueError):
        raise PermissionError("La sesión no contiene un rol válido.")

    empleado_id = sesion.get("empleado_id")
    if type(empleado_id) is not int or empleado_id <= 0:
        raise PermissionError("La sesión no contiene un empleado válido.")

    usuario_id = sesion.get("id_usuario", sesion.get("id"))
    if type(usuario_id) is not int or usuario_id <= 0:
        raise PermissionError("La sesión no contiene una cuenta válida.")

    return sesion


def exigir_admin(sesion):
    exigir_sesion(sesion)
    if sesion["rol"] != "admin":
        raise PermissionError("Acción permitida únicamente al administrador.")
    return sesion
