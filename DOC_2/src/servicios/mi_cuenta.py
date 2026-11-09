"""Operaciones de autoservicio: siempre se usa el empleado_id de la sesión."""

from dominio.empleado import Empleado
from servicios.permisos import exigir_sesion


def mi_ficha(sesion, empleado_dao):
    exigir_sesion(sesion)
    empleado = empleado_dao.obtener_por_id(sesion["empleado_id"])
    if empleado is None:
        raise ValueError("No se encontró la ficha del empleado asociado a la sesión.")
    return empleado


def mis_registros(sesion, registro_tiempo_dao):
    exigir_sesion(sesion)
    return registro_tiempo_dao.listar_por_empleado(sesion["empleado_id"])


def actualizar_mis_datos(sesion, empleado_dao, nombre, correo):
    exigir_sesion(sesion)
    nombre = Empleado.validar_nombre(nombre)
    correo = Empleado.validar_correo(correo)
    empleado = empleado_dao.obtener_por_id(sesion["empleado_id"])
    if empleado is None:
        raise ValueError("Empleado no encontrado.")
    return empleado_dao.actualizar_datos_basicos(sesion["empleado_id"], nombre, correo)
