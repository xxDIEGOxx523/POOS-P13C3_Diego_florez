"""Servicios administrativos. Cada operación valida el rol antes de usar el DAO."""

from servicios.permisos import exigir_admin


def listar_todos(sesion, empleado_dao):
    exigir_admin(sesion)
    return empleado_dao.obtener_todos()


def registrar(sesion, empleado_dao, empleado):
    exigir_admin(sesion)
    return empleado_dao.insertar(empleado)


def actualizar(sesion, empleado_dao, empleado_id, empleado):
    exigir_admin(sesion)
    return empleado_dao.actualizar(empleado_id, empleado)


def eliminar(sesion, empleado_dao, empleado_id):
    exigir_admin(sesion)
    return empleado_dao.eliminar(empleado_id)


def listar_registros_laborales(sesion, registro_dao):
    exigir_admin(sesion)
    return registro_dao.obtener_todos_con_detalles()


def registrar_cuenta(sesion, autenticacion, empleado_id, nombre_usuario, password):
    exigir_admin(sesion)
    return autenticacion.registrar(sesion, empleado_id, nombre_usuario, password)
