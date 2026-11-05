"""Cliente HTTP para la API pública de dólar observado de Mindicador."""
from datetime import date
import math
import requests

API_DOLAR_URL = "https://mindicador.cl/api/dolar"
TIMEOUT = (3, 8)


def obtener_datos():
    """Solicita JSON a una URL fija y valida primero el estado HTTP."""
    respuesta = requests.get(
        API_DOLAR_URL,
        timeout=TIMEOUT,
        headers={"Accept": "application/json", "User-Agent": "EcoTech-Solutions/1.0"},
    )
    respuesta.raise_for_status()
    datos = respuesta.json()
    if not isinstance(datos, dict):
        raise ValueError("La respuesta de la API no es un objeto JSON.")
    return datos


def extraer_primero(datos):
    """Extrae fecha y valor del registro más reciente con validación de estructura."""
    if not isinstance(datos, dict):
        raise ValueError("La respuesta de la API tiene una estructura inesperada.")
    serie = datos.get("serie")
    if not isinstance(serie, list) or not serie:
        raise ValueError("La API no contiene observaciones disponibles.")
    registro = serie[0]
    if not isinstance(registro, dict):
        raise ValueError("El registro del indicador no tiene el formato esperado.")
    fecha = registro.get("fecha")
    valor = registro.get("valor")
    if not isinstance(fecha, str):
        raise ValueError("La API no entregó una fecha válida.")
    try:
        fecha = date.fromisoformat(fecha[:10]).isoformat()
    except ValueError as error:
        raise ValueError("La API entregó una fecha con formato inválido.") from error
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError("La API no entregó un valor numérico.")
    valor = float(valor)
    if not math.isfinite(valor) or valor <= 0:
        raise ValueError("El valor del indicador debe ser finito y positivo.")
    return fecha, valor
