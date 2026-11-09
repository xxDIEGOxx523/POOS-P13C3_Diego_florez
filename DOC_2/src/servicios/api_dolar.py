"""Consumo seguro de Mindicador para obtener el dólar observado.

La URL es fija y no se construye con datos del usuario. La operación exige
una sesión válida antes de efectuar la solicitud HTTP.
"""
from dataclasses import dataclass
from datetime import datetime
import math
import requests

from servicios.permisos import exigir_sesion

URL_DOLAR = "https://mindicador.cl/api/dolar"
TIMEOUT = (3, 7)
USER_AGENT = "EcoTech-Solutions/1.0 (consulta educativa)"


@dataclass(frozen=True)
class IndicadorDolar:
    codigo: str
    nombre: str
    unidad: str
    valor: float
    fecha: datetime
    fuente: str


def deserializar_indicador(payload):
    """Valida el JSON y extrae solo los campos requeridos."""
    if not isinstance(payload, dict):
        raise ValueError("La respuesta de la API debe ser un objeto JSON.")
    codigo = payload.get("codigo")
    nombre = payload.get("nombre")
    unidad = payload.get("unidad_medida")
    serie = payload.get("serie")
    if codigo != "dolar" or not isinstance(nombre, str) or not isinstance(unidad, str):
        raise ValueError("La API devolvió metadatos inesperados.")
    if not isinstance(serie, list) or not serie:
        raise ValueError("La API no entregó una serie de valores.")
    registro = serie[0]
    if not isinstance(registro, dict):
        raise ValueError("El registro del indicador no tiene el formato esperado.")
    valor = registro.get("valor")
    fecha_raw = registro.get("fecha")
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValueError("El valor del indicador no es numérico.")
    valor = float(valor)
    if not math.isfinite(valor) or valor <= 0:
        raise ValueError("El valor del indicador debe ser positivo y finito.")
    if not isinstance(fecha_raw, str):
        raise ValueError("La fecha del indicador no es válida.")
    try:
        fecha = datetime.fromisoformat(fecha_raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("La fecha del indicador tiene un formato inválido.") from exc
    return IndicadorDolar(
        codigo=codigo, nombre=nombre.strip()[:100], unidad=unidad.strip()[:30],
        valor=valor, fecha=fecha, fuente="Mindicador"
    )


def consultar_dolar(sesion):
    """Consulta el dólar para una sesión autenticada y devuelve datos validados."""
    exigir_sesion(sesion)
    try:
        respuesta = requests.get(
            URL_DOLAR,
            timeout=TIMEOUT,
            headers={"Accept": "application/json", "User-Agent": USER_AGENT},
        )
        respuesta.raise_for_status()
        try:
            payload = respuesta.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise ValueError("El servicio respondió, pero el contenido no es JSON válido.") from exc
        return deserializar_indicador(payload)
    except requests.exceptions.Timeout as exc:
        raise ConnectionError("La consulta a Mindicador superó el tiempo de espera.") from exc
    except requests.exceptions.HTTPError as exc:
        codigo = exc.response.status_code if exc.response is not None else "desconocido"
        raise RuntimeError(f"Mindicador respondió con un error HTTP ({codigo}).") from exc
    except requests.exceptions.ConnectionError as exc:
        raise ConnectionError("No fue posible establecer conexión con Mindicador.") from exc
    except requests.exceptions.RequestException as exc:
        raise RuntimeError("Ocurrió un error de red al consultar Mindicador.") from exc
