"""Orquestación del indicador: API, persistencia, historial y respaldo local."""
from dataclasses import dataclass
from datetime import datetime

from persistencia.indicador_dao import IndicadorDAO, ErrorPersistenciaIndicador
from servicios.api_dolar import IndicadorDolar, consultar_dolar
from servicios.permisos import exigir_sesion


class IndicadorNoDisponible(RuntimeError):
    """No existe una respuesta de API ni un respaldo local utilizable."""


@dataclass(frozen=True)
class ResultadoIndicador:
    indicador: IndicadorDolar
    origen: str
    guardado: bool
    mensaje: str = ""


def _crear_objeto_desde_fila(fila):
    fecha = fila.get("fecha")
    if isinstance(fecha, str):
        fecha = datetime.fromisoformat(fecha.replace("Z", "+00:00"))
    if not isinstance(fecha, datetime):
        raise ValueError("El respaldo almacenado tiene una fecha inválida.")
    return IndicadorDolar(
        codigo=fila["codigo"],
        nombre="Dólar observado",
        unidad=fila["unidad"],
        valor=float(fila["valor"]),
        fecha=fecha,
        fuente=fila["fuente"],
    )


def consultar_y_conservar_dolar(sesion, dao=None):
    """Consulta la API; guarda el dato y recurre al último respaldo si falla."""
    exigir_sesion(sesion)
    dao = dao or IndicadorDAO()

    try:
        indicador = consultar_dolar(sesion)
    except (ConnectionError, RuntimeError, ValueError) as error_api:
        try:
            fila = dao.obtener_ultimo("dolar")
            if fila:
                indicador_respaldo = _crear_objeto_desde_fila(fila)
                return ResultadoIndicador(
                    indicador=indicador_respaldo,
                    origen="BD local (respaldo)",
                    guardado=False,
                    mensaje=(
                        "Mindicador no está disponible. Se muestra el último dato "
                        "conservado; no corresponde a una consulta actualizada."
                    ),
                )
        except (ErrorPersistenciaIndicador, ValueError, KeyError, TypeError):
            pass
        raise IndicadorNoDisponible(
            "No fue posible consultar Mindicador y no existe un respaldo local válido."
        ) from error_api

    try:
        dao.guardar_o_actualizar(indicador)
        return ResultadoIndicador(
            indicador=indicador,
            origen="API (Mindicador)",
            guardado=True,
            mensaje="Dato consultado, validado y conservado correctamente.",
        )
    except ErrorPersistenciaIndicador:
        return ResultadoIndicador(
            indicador=indicador,
            origen="API (Mindicador)",
            guardado=False,
            mensaje=(
                "El dato fue consultado y validado, pero no se pudo guardar. "
                "El historial no se actualizó."
            ),
        )


def obtener_historial_dolar(sesion, dao=None, limite=20):
    """Entrega historial local sin hacer una nueva solicitud HTTP."""
    exigir_sesion(sesion)
    dao = dao or IndicadorDAO()
    return dao.listar("dolar", limite)
