"""Prueba manual del cliente HTTP y del procesamiento JSON de Mindicador."""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = Path(__file__).resolve().parent
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import requests
from servicios.api_dolar import obtener_datos
from servicios.deserializador_indicador import DeserializadorIndicador


if __name__ == "__main__":
    try:
        indicador = DeserializadorIndicador.desde_api(obtener_datos())
        print("=" * 52)
        print("ECOTECH SOLUTIONS | DÓLAR OBSERVADO")
        print(f"Valor: ${indicador.valor:,.2f} {indicador.unidad}")
        print(f"Fecha del dato: {indicador.fecha}")
        print(f"Fuente: {indicador.fuente}")
        print("=" * 52)
    except requests.exceptions.RequestException:
        print("No se pudo conectar con el servicio externo. Compruebe Internet e intente nuevamente.")
    except (ValueError, TypeError, KeyError):
        print("La API respondió, pero sus datos no tienen el formato esperado.")
