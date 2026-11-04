from pathlib import Path
import sys
from getpass import getpass

# El proyecto conserva la carpeta src bajo DOC_2; se agrega al path sin mover archivos.
SRC_DIR = Path(__file__).resolve().parent / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from persistencia.crear_db import crear_base_y_tablas
from persistencia.dao_factory import DAOFactory
from persistencia.usuario_dao import UsuarioDAO
from servicios.autenticacion import Autenticacion
from ux.menu_usuario import MenuUsuario
from ux.interfaz import TerminalInterface
from semilla import cargar_semilla, imprimir_resumen
from persistencia.conexion import obtener_motor


USUARIO_ADMIN_DEMO = "admin_ecotech"
CORREO_EMPLEADO_SEMILLA = "semilla.empleado01@example.com"


def asegurar_cuenta_demo(usuario_dao, empleado_dao, autenticacion):
    """Crea la cuenta admin inicial solo si el empleado semilla aún no tiene cuenta.

    No cambia el rol ni la contraseña de cuentas existentes al repetir la semilla.
    """
    empleado = next(
        (e for e in empleado_dao.obtener_todos()
         if e.get("correo") == CORREO_EMPLEADO_SEMILLA
         or e.get("telefono") == "+56970000001"),
        None,
    )
    if not empleado:
        return None

    existente = usuario_dao.buscar_por_empleado(empleado["id_empleado"])
    if existente:
        # Una cuenta existente nunca se eleva automáticamente.
        return {"creada": False, "usuario": existente.get("nombre_usuario"),
                "rol": existente.get("rol")}

    print("\nPreparación de la cuenta inicial de administrador.")
    print("La contraseña no se mostrará y se guardará únicamente como hash bcrypt.")
    while True:
        password = getpass("Defina la contraseña del administrador: ")
        confirmacion = getpass("Repita la contraseña: ")
        if password != confirmacion:
            print("Las contraseñas no coinciden. Intente nuevamente.")
            continue
        try:
            autenticacion.crear_cuenta_inicial(
                empleado["id_empleado"], USUARIO_ADMIN_DEMO, password
            )
            break
        except (TypeError, ValueError) as error:
            print(f"Contraseña no válida: {error}")
    return {"creada": True, "usuario": USUARIO_ADMIN_DEMO, "rol": "admin"}


def main():
    try:
        print(f"Preparando base de datos ({obtener_motor().upper()})...")
        crear_base_y_tablas()
        factory = DAOFactory()
        registro_dao = factory.get_registro_tiempo_dao()
        empleado_dao = factory.get_empleado_dao()
        proyecto_dao = factory.get_proyecto_dao()
        departamento_dao = factory.get_departamento_dao()

        print("Precargando datos iniciales (sin duplicar registros)...")
        resumen = cargar_semilla(
            registro_dao, empleado_dao, proyecto_dao, departamento_dao
        )
        imprimir_resumen(resumen)

        usuario_dao = UsuarioDAO()
        autenticacion = Autenticacion(usuario_dao, empleado_dao)
        cuenta_demo = asegurar_cuenta_demo(usuario_dao, empleado_dao, autenticacion)
        if cuenta_demo and cuenta_demo["creada"]:
            print("\nCuenta inicial de administrador creada correctamente:")
            print(f"  Usuario: {cuenta_demo['usuario']}")
            print("  Contraseña: la definida durante la configuración inicial.\n")
        elif cuenta_demo and cuenta_demo["rol"] == "admin":
            print(
                "\nYa existe una cuenta admin vinculada al empleado inicial. "
                f"Usuario: {cuenta_demo['usuario']}"
            )
        elif cuenta_demo:
            print(
                "\nEl empleado inicial ya tiene una cuenta de tipo empleado "
                f"({cuenta_demo['usuario']}). No se modificó su rol automáticamente. "
                "Para disponer de un administrador, revise la cuenta inicial desde la BD."
            )

        acceso = MenuUsuario(autenticacion, empleado_dao)
        while True:
            usuario = acceso.iniciar_sesion()
            if usuario is None:
                print("Sistema finalizado.")
                break

            app = TerminalInterface(
                registro_dao,
                empleado_dao,
                proyecto_dao,
                departamento_dao,
                usuario=usuario,
                autenticacion=autenticacion,
            )
            resultado = app.iniciar()
            if resultado == "salir":
                print("Sistema finalizado.")
                break
            print("\nSesión cerrada. Para continuar, vuelva a iniciar sesión.")
    except Exception as error:
        print(f"Error al iniciar el sistema: {error}")
        print(
            "Compruebe DB_BACKEND, la configuración del archivo .env "
            "y las dependencias de requirements.txt."
        )


if __name__ == "__main__":
    main()
