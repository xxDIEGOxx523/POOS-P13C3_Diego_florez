"""Pantalla de login. El alta de cuentas se reserva a operaciones administrativas."""
from getpass import getpass


class MenuUsuario:
    def __init__(self, autenticacion, empleado_dao=None):
        self.autenticacion = autenticacion
        self.empleado_dao = empleado_dao

    def iniciar_sesion(self):
        print("\n" + "=" * 62)
        print("                 ECOTECH SOLUTIONS")
        print("                    ACCESO SEGURO")
        print("=" * 62)
        print("1. Iniciar sesión")
        print("0. Salir")
        while True:
            try:
                opcion = input("Seleccione una opción: ").strip()
            except EOFError:
                return None
            if opcion == "1":
                try:
                    nombre_usuario = input("Nombre de usuario: ").strip()
                    password = getpass("Contraseña (entrada oculta): ")
                except EOFError:
                    return None
                usuario = self.autenticacion.autenticar(nombre_usuario, password)
                if usuario:
                    print(
                        f"\nAcceso correcto. Sesión iniciada: "
                        f"{usuario['nombre_usuario']} ({usuario['rol']})."
                    )
                    return usuario
                print("Usuario o contraseña incorrectos, o cuenta inactiva. Intente nuevamente.")
            elif opcion == "0":
                return None
            else:
                print("Seleccione 1 o 0.")
