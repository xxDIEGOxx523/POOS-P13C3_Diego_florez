"""Pantalla de acceso y alta de usuarios en terminal."""
from getpass import getpass


class MenuUsuario:
    def __init__(self, autenticacion, empleado_dao):
        self.autenticacion = autenticacion
        self.empleado_dao = empleado_dao

    def iniciar_sesion(self):
        print("\n" + "=" * 62)
        print("                 ECOTECH SOLUTIONS")
        print("                    ACCESO SEGURO")
        print("=" * 62)
        print("1. Iniciar sesión")
        print("2. Crear cuenta para un empleado existente")
        print("0. Salir")
        while True:
            opcion = input("Seleccione una opción: ").strip()
            if opcion == "1":
                correo = input("Correo: ").strip().lower()
                password = getpass("Contraseña (entrada oculta): ")
                usuario = self.autenticacion.autenticar(correo, password)
                if usuario:
                    print(f"\nAcceso correcto. Sesión iniciada: {usuario['correo']}")
                    return usuario
                print("Credenciales incorrectas o cuenta inactiva. Intente nuevamente.")
            elif opcion == "2":
                self._registrar()
            elif opcion == "0":
                return None
            else:
                print("Seleccione 1, 2 o 0.")

    def _registrar(self):
        print("\nCREAR CUENTA")
        try:
            id_empleado = int(input("ID del empleado existente: ").strip())
            empleado = self.empleado_dao.obtener_por_id(id_empleado)
            if not empleado:
                print("No existe un empleado con ese ID.")
                return
            correo = input("Correo para iniciar sesión: ").strip().lower()
            password = getpass("Nueva contraseña (no se mostrará): ")
            confirmacion = getpass("Repita la contraseña: ")
            if password != confirmacion:
                print("Las contraseñas no coinciden.")
                return
            self.autenticacion.registrar(id_empleado, correo, password)
            print("Cuenta creada. Ya puede iniciar sesión.")
        except ValueError as error:
            print(f"No se pudo crear la cuenta: {error}")
        except Exception as error:
            print(f"No se pudo crear la cuenta. Revise el correo y los datos: {error}")
