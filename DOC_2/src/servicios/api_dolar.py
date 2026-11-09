"""Consumo seguro y validación de Mindicador para obtener el dólar observado.

El endpoint es constante: la aplicación no acepta URLs ni parámetros arbitrarios
provenientes del usuario. Se usa HTTPS, timeout explícito y reintento acotado
solo ante saturación o errores temporales del proveedor.
"""
from dataclasses import dataclass
from datetime import datetime
import math
import time

import requests

from servicios.permisos import exigir_sesion

URL_DOLAR = "https://mindicador.cl/api/dolar"
TIMEOUT = (3, 7)  # conexión y lectura, respectivamente
USER_AGENT = "EcoTech-Solutions/1.1 (consulta educativa)"
MAX_INTENTOS = 2
CODIGOS_REINTENTABLES = {429, 500, 502, 503, 504}


class ErrorHTTPDolar(RuntimeError):
    """Error HTTP con el código de estado disponible para diagnóstico interno."""

    def __init__(self, codigo, mensaje):
        self.codigo = codigo
        super().__init__(mensaje)


@dataclass(frozen=True)
class IndicadorDolar:
    codigo: str
    nombre: str
    unidad: str
    valor: float
    fecha: datetime
    fuente: str


def deserializar_indicador(payload):
    """Convierte el JSON externo en un objeto validado y mínimo del dominio."""
    if not isinstance(payload, dict):
        raise ValueError("La respuesta de la API debe ser un objeto JSON.")

    codigo = payload.get("codigo")
    nombre = payload.get("nombre")
    unidad = payload.get("unidad_medida")
    serie = payload.get("serie")
    if codigo != "dolar" or not isinstance(nombre, str) or not isinstance(unidad, str):
        raise ValueError("La API devolvió metadatos inesperados.")
    if not nombre.strip() or not unidad.strip():
        raise ValueError("La API devolvió metadatos vacíos.")
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
    if not isinstance(fecha_raw, str) or not fecha_raw.strip():
        raise ValueError("La fecha del indicador no es válida.")
    try:
        fecha = datetime.fromisoformat(fecha_raw.strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("La fecha del indicador tiene un formato inválido.") from exc

    return IndicadorDolar(
        codigo="dolar",
        nombre=nombre.strip()[:100],
        unidad=unidad.strip()[:30],
        valor=valor,
        fecha=fecha,
        fuente="Mindicador",
    )


def _solicitar_json():
    """Hace HTTP con un único reintento acotado para errores temporales."""
    for intento in range(1, MAX_INTENTOS + 1):
        try:
            respuesta = requests.get(
                URL_DOLAR,
                timeout=TIMEOUT,
                headers={"Accept": "application/json", "User-Agent": USER_AGENT},
            )
        except requests.exceptions.Timeout as exc:
            if intento < MAX_INTENTOS:
                time.sleep(0.2 * intento)
                continue
            raise ConnectionError(
                "La consulta a Mindicador superó el tiempo de espera."
            ) from exc
        except requests.exceptions.ConnectionError as exc:
            if intento < MAX_INTENTOS:
                time.sleep(0.2 * intento)
                continue
            raise ConnectionError(
                "No fue posible establecer conexión con Mindicador."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                "Ocurrió un error de red al consultar Mindicador."
            ) from exc

        codigo = getattr(respuesta, "status_code", 200)
        if codigo in CODIGOS_REINTENTABLES and intento < MAX_INTENTOS:
            time.sleep(0.2 * intento)
            continue
        if not 200 <= codigo < 300:
            if 400 <= codigo < 500:
                raise ErrorHTTPDolar(
                    codigo, f"Mindicador rechazó la solicitud (HTTP {codigo})."
                )
            if 300 <= codigo < 400:
                raise ErrorHTTPDolar(
                    codigo, f"Mindicador devolvió una redirección no resuelta (HTTP {codigo})."
                )
            raise ErrorHTTPDolar(
                codigo, f"Mindicador no está disponible (HTTP {codigo})."
            )

        try:
            respuesta.raise_for_status()
            return respuesta.json()
        except requests.exceptions.JSONDecodeError as exc:
            raise ValueError(
                "El servicio respondió, pero el contenido no es JSON válido."
            ) from exc
        except requests.exceptions.HTTPError as exc:
            codigo_error = exc.response.status_code if exc.response is not None else codigo
            raise ErrorHTTPDolar(
                codigo_error, f"Mindicador respondió con un error HTTP ({codigo_error})."
            ) from exc
        except requests.exceptions.RequestException as exc:
            raise RuntimeError(
                "Ocurrió un error al recibir la respuesta de Mindicador."
            ) from exc

    raise RuntimeError("No fue posible obtener una respuesta válida de Mindicador.")


def consultar_dolar(sesion):
    """Consulta el dólar observado para una sesión autenticada."""
    exigir_sesion(sesion)
    payload = _solicitar_json()
    return deserializar_indicador(payload)
