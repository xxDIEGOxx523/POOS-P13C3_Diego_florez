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



def mis_proyectos(sesion, proyecto_dao):
    """Lista solo los proyectos asociados al empleado autenticado."""
    exigir_sesion(sesion)
    return proyecto_dao.listar_por_empleado(sesion["empleado_id"])


def registrar_horas(sesion, proyecto_dao, registro_dao, id_proyecto,
                    fecha, horas, descripcion):
    """Registra horas propias únicamente en un proyecto asignado a la sesión."""
    from dominio.registrotiempo import RegistroTiempo

    exigir_sesion(sesion)
    if type(id_proyecto) is not int or id_proyecto <= 0:
        raise ValueError("El proyecto seleccionado no es válido.")
    if not proyecto_dao.tiene_asignacion(id_proyecto, sesion["empleado_id"]):
        raise PermissionError("Solo puede registrar horas en proyectos que tenga asignados.")
    registro = RegistroTiempo(
        fecha=fecha,
        horas_trabajadas=horas,
        descripcion_trabajo=descripcion,
        id_empleado=sesion["empleado_id"],
        id_proyecto=id_proyecto,
    )
    registro.validar_registro()
    return registro_dao.insertar(registro)
