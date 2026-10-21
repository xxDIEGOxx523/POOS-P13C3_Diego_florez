import math
import requests

# 🛠️ CAMBIA ESTO A True PARA PROBAR LA SERIE VACÍA EXIGIDA EN LA EVALUACIÓN
PROBAR_SERIE_VACIA = False


# --- PASO 1: CONSULTA CON SIMULACIÓN DE RESPALDO (MOCK) ---
def obtener_datos():
    """Intenta conectar a internet.

    Si falla, simula respuestas exitosas o vacías según la prueba.
    """
    if PROBAR_SERIE_VACIA:
        print("\n[!] Simulando un caso de error: RESPUESTA DE API VACÍA...")
        # Simula una respuesta donde el diccionario de tasas viene en blanco
        return "Simulador (Serie Vacía)", {"rates": {}}

    cabeceras = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        print("Intentando conectar con la API externa...")
        respuesta = requests.get(
            "https://er-api.com",
            headers=cabeceras,
            timeout=3,
        )
        respuesta.raise_for_status()
        return "API Real (Online)", respuesta.json()

    except requests.exceptions.RequestException:
        print(
            "\n[!] Conexión bloqueada por la red. Activando Modo Simulación..."
        )
        json_simulado = {
            "result": "success",
            "time_last_update_utc": "Wed, 21 Oct 2026 00:00:00 +0000",
            "rates": {"CLP": 915.50},
        }
        return "Simulador (Local Mock)", json_simulado


# --- PASO 2: EXTRAER EL DATO Y COMPROBARLO (Slide 12) ---
def extraer_primero(origen, datos):
    """Aplica las validaciones estrictas requeridas por EcoTech."""
    if not isinstance(datos, dict):
        raise ValueError("Respuesta inesperada.")

    tasas = datos.get("rates", {})
    valor = tasas.get("CLP")
    fecha = datos.get("time_last_update_utc")

    # Si la serie o el valor no existen en el diccionario (Serie vacía o inválida)
    if (
        valor is None
        or type(valor) not in (int, float)
        or not math.isfinite(valor)
        or valor <= 0
    ):
        raise ValueError("No hay valores disponibles o el indicador es inválido.")

    return fecha, valor


# --- PASO 3: EJECUCIÓN DEL PROGRAMA ---
if __name__ == "__main__":
    try:
        # 1. Obtener la información
        origen, datos_api = obtener_datos()

        # 2. Extraer y aplicar filtros de seguridad
        fecha, valor_dolar = extraer_primero(origen, datos_api)

        # 3. Mostrar el resultado normal
        print(f"\n=========================================")
        print(f"¡ÉXITO! Origen utilizado: {origen}")
        print(f"Dólar observado: {valor_dolar:.2f} CLP por USD")
        print(f"Fecha de la referencia: {fecha}")
        print(f"=========================================")

    except (ValueError, KeyError, TypeError) as error:
        # Aquí se captura de forma segura la serie vacía o datos corruptos
        print(f"\n=========================================")
        print(f"[!] FALLO CONTROLADO CORECTAMENTE")
        print(f"Detalle: {error}")
        print(f"=========================================")




