"""Operaciones administrativas sobre registros laborales."""
from servicios.permisos import exigir_admin


def registrar(sesion, registro_dao, registro):
    exigir_admin(sesion)
    registro.validar_registro()
    return registro_dao.insertar(registro)


def actualizar(sesion, registro_dao, id_registro, registro):
    exigir_admin(sesion)
    registro.validar_registro()
    return registro_dao.actualizar(id_registro, registro)


def eliminar(sesion, registro_dao, id_registro):
    exigir_admin(sesion)
    return registro_dao.eliminar(id_registro)
