"""Operaciones administrativas de departamentos."""
from servicios.permisos import exigir_admin


def listar(sesion, departamento_dao):
    exigir_admin(sesion)
    return departamento_dao.obtener_todos()


def registrar(sesion, departamento_dao, departamento):
    exigir_admin(sesion)
    return departamento_dao.insertar(departamento)


def actualizar(sesion, departamento_dao, id_departamento, departamento):
    exigir_admin(sesion)
    return departamento_dao.actualizar(id_departamento, departamento)


def eliminar(sesion, departamento_dao, id_departamento):
    exigir_admin(sesion)
    return departamento_dao.eliminar(id_departamento)


def asignar_gerente(sesion, departamento_dao, empleado_dao, id_departamento, id_empleado):
    exigir_admin(sesion)
    if departamento_dao.obtener_por_id(id_departamento) is None:
        raise ValueError("No existe el departamento indicado.")
    if empleado_dao.obtener_por_id(id_empleado) is None:
        raise ValueError("No existe el empleado indicado.")
    return departamento_dao.asignar_gerente(id_departamento, id_empleado)
