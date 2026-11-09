"""Prueba independiente de Mindicador usando el mismo servicio de la aplicación."""
from servicios.api_dolar import consultar_dolar


if __name__ == "__main__":
    # La función de servicio exige sesión: esta sesión de prueba solo habilita
    # la comprobación local del módulo; no se utiliza para iniciar la aplicación.
    sesion_prueba = {
        "id": 1, "id_usuario": 1, "empleado_id": 1,
        "nombre_usuario": "prueba_api", "rol": "empleado"
    }
    try:
        indicador = consultar_dolar(sesion_prueba)
        print("ECOTECH SOLUTIONS | DÓLAR OBSERVADO")
        print(f"Valor: ${indicador.valor:,.2f} {indicador.unidad}")
        print(f"Fecha: {indicador.fecha.isoformat()}")
        print(f"Fuente: {indicador.fuente}")
    except (PermissionError, ValueError, ConnectionError, RuntimeError) as error:
        print(f"No fue posible completar la prueba: {error}")
