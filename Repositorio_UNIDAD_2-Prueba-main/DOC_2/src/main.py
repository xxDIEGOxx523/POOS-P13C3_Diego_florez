from persistencia.crear_db import crear_base_y_tablas
from persistencia.dao_factory import DAOFactory
from ux.interfaz import TerminalInterface

def pedir_dato(mensaje_solicitud: str, funcion_validadora):
    """Solicita un dato por consola de manera interactiva en un bucle.
    Si el validador lanza un ValueError, muestra el mensaje claro y permite reintentar 
    solo ese campo sin romper el programa.
    """
    while True:
        try:
            entrada = input(mensaje_solicitud)
            funcion_validadora(entrada)
            return entrada
        except ValueError as e:
            print(f"❌ Error de validación: {e} Intente nuevamente.")


def main():
    try:
        crear_base_y_tablas()
        factory = DAOFactory()
        app = TerminalInterface(
            factory.get_registro_tiempo_dao(),
            factory.get_empleado_dao(),
            factory.get_proyecto_dao(),
            factory.get_departamento_dao(),
        )
        app.iniciar()
    except Exception as e:
        print(f"Error al iniciar el sistema: {e}")


if __name__ == "__main__":
    main()

