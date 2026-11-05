"""Casos de uso de consulta, persistencia, respaldo e historial de indicadores."""
import requests

from dominio.indicador import Indicador
from servicios.api_dolar import obtener_datos
from servicios.deserializador_indicador import DeserializadorIndicador
from servicios.permisos import exigir_sesion


MENSAJE_API_NO_DISPONIBLE = (
    "No se pudo actualizar el indicador desde la API. Se intentará usar el último dato local."
)


def consultar_indicador(sesion, indicador_dao):
    """Consulta con sesión, transforma, persiste y usa la BD como respaldo."""
    exigir_sesion(sesion)
    try:
        datos = obtener_datos()
        indicador = DeserializadorIndicador.desde_api(datos)
    except (requests.exceptions.RequestException, ValueError, KeyError, TypeError):
        try:
            respaldo = indicador_dao.buscar_ultimo()
        except Exception:
            return {
                "indicador": None, "origen": None, "guardado": False,
                "mensaje": "La API no está disponible y no se pudo consultar el respaldo local.",
            }
        if respaldo is None:
            return {
                "indicador": None, "origen": None, "guardado": False,
                "mensaje": MENSAJE_API_NO_DISPONIBLE + " No existe un dato de respaldo guardado.",
            }
        return {
            "indicador": respaldo, "origen": "BD local", "guardado": False,
            "mensaje": MENSAJE_API_NO_DISPONIBLE,
        }

    try:
        indicador_dao.guardar(indicador)
        return {
            "indicador": indicador, "origen": "API", "guardado": True,
            "mensaje": "Dato consultado y guardado/actualizado en la base local.",
        }
    except Exception:
        # El dato vigente de la API sigue siendo utilizable, pero no se afirma que quedó guardado.
        return {
            "indicador": indicador, "origen": "API", "guardado": False,
            "mensaje": "La API respondió correctamente, pero no fue posible guardar el dato local.",
        }


def obtener_historial(sesion, indicador_dao):
    """Lee únicamente la BD; no realiza ninguna solicitud HTTP."""
    exigir_sesion(sesion)
    return indicador_dao.listar()


# Alias semántico para llamadas desde interfaces antiguas si existieran.
consultar_dolar = consultar_indicador
