"""Prueba de consulta y validación de la API del dólar observado en Chile."""
import math
import requests

URL = "https://mindicador.cl/api/dolar"


def obtener_datos():
    respuesta = requests.get(URL, timeout=(3, 5))
    respuesta.raise_for_status()
    return respuesta.json()


def extraer_primero(datos):
    if not isinstance(datos, dict):
        raise ValueError("La respuesta de la API no es un objeto JSON válido.")
    serie = datos.get("serie")
    if not isinstance(serie, list) or not serie:
        raise ValueError("La API no entregó valores en la serie.")
    primero = serie[0]
    if not isinstance(primero, dict):
        raise ValueError("El primer registro de la serie no es válido.")
    valor = primero.get("valor")
    if type(valor) not in (int, float) or not math.isfinite(valor) or valor <= 0:
        raise ValueError("El valor del dólar es inválido.")
    return primero.get("fecha", "Fecha no informada"), float(valor)


if __name__ == "__main__":
    try:
        fecha, valor = extraer_primero(obtener_datos())
        print("=" * 48)
        print("ECOTECH SOLUTIONS | DÓLAR OBSERVADO")
        print(f"Valor: ${valor:,.2f} CLP por USD")
        print(f"Fecha: {fecha}")
        print("=" * 48)
    except requests.exceptions.RequestException as error:
        print(f"No se pudo conectar con la API: {error}")
    except (ValueError, TypeError, KeyError) as error:
        print(f"La respuesta de la API no es válida: {error}")
