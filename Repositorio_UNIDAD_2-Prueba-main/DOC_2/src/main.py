from persistencia.crear_db import crear_base_y_tablas
from persistencia.dao_factory import DAOFactory
from persistencia.usuario_dao import UsuarioDAO
from servicios.autenticacion import Autenticacion
from ux.menu_usuario import MenuUsuario
from ux.interfaz import TerminalInterface
from semilla import cargar_semilla, imprimir_resumen
from persistencia.conexion import obtener_motor


CORREO_ADMIN_DEMO = "admin@ecotech.local"
PASSWORD_ADMIN_DEMO = "EcoTech2026!"


def asegurar_cuenta_demo(usuario_dao, empleado_dao, autenticacion):
    """Crea una cuenta demostrativa solo si aún no existe, vinculada a la semilla."""
    if usuario_dao.buscar_por_correo(CORREO_ADMIN_DEMO):
        return False
    empleado = next((e for e in empleado_dao.obtener_todos()
                     if e.get("correo") == "semilla.empleado01@example.com"), None)
    if not empleado:
        return False
    if usuario_dao.existe_para_empleado(empleado["id_empleado"]):
        return False
    usuario_dao.crear(empleado["id_empleado"], CORREO_ADMIN_DEMO,
                      autenticacion.crear_hash(PASSWORD_ADMIN_DEMO))
    return True


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
        resumen = cargar_semilla(registro_dao, empleado_dao, proyecto_dao, departamento_dao)
        imprimir_resumen(resumen)

        usuario_dao = UsuarioDAO()
        autenticacion = Autenticacion(usuario_dao)
        cuenta_creada = asegurar_cuenta_demo(usuario_dao, empleado_dao, autenticacion)
        if cuenta_creada:
            print("\nCuenta inicial de demostración creada:")
            print(f"  Usuario: {CORREO_ADMIN_DEMO}")
            print(f"  Contraseña temporal: {PASSWORD_ADMIN_DEMO}")
            print("  Cámbiela después de ingresar y no la reutilice en otros servicios.\n")

        acceso = MenuUsuario(autenticacion, empleado_dao)
        usuario = acceso.iniciar_sesion()
        if usuario is None:
            print("Sistema finalizado.")
            return

        while True:
            app = TerminalInterface(registro_dao, empleado_dao, proyecto_dao, departamento_dao,
                                    usuario=usuario, autenticacion=autenticacion)
            app.iniciar()
            # La opción 11 finaliza el menú actual. Para no dejar una sesión viva,
            # se cierra el proceso tras la salida explícita del menú.
            break
    except Exception as error:
        print(f"Error al iniciar el sistema: {error}")
        print("Compruebe DB_BACKEND, la configuración del archivo .env y las dependencias de requirements.txt.")


if __name__ == "__main__":
    main()
