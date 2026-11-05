"""Operaciones administrativas de proyectos y asignaciones."""
from servicios.permisos import exigir_admin


def listar(sesion, proyecto_dao):
    exigir_admin(sesion)
    return proyecto_dao.obtener_todos()


def registrar(sesion, proyecto_dao, proyecto):
    exigir_admin(sesion)
    return proyecto_dao.insertar(proyecto)


def asignar_empleado(sesion, proyecto_dao, empleado_dao, id_proyecto, id_empleado):
    exigir_admin(sesion)
    if proyecto_dao.obtener_por_id(id_proyecto) is None:
        raise ValueError("No existe el proyecto indicado.")
    if empleado_dao.obtener_por_id(id_empleado) is None:
        raise ValueError("No existe el empleado indicado.")
    if proyecto_dao.tiene_asignacion(id_proyecto, id_empleado):
        return False
    return proyecto_dao.asignar_empleado(id_proyecto, id_empleado)


def desasignar_empleado(sesion, proyecto_dao, id_proyecto, id_empleado):
    exigir_admin(sesion)
    return proyecto_dao.desasignar_empleado(id_proyecto, id_empleado)


def actualizar(sesion, proyecto_dao, id_proyecto, proyecto):
    exigir_admin(sesion)
    return proyecto_dao.actualizar(id_proyecto, proyecto)


def eliminar(sesion, proyecto_dao, id_proyecto):
    exigir_admin(sesion)
    return proyecto_dao.eliminar(id_proyecto)
