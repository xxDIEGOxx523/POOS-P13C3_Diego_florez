
from datetime import datetime

from dominio.empleado import Empleado
from dominio.departamento import Departamento
from dominio.proyecto import Proyecto
from dominio.registrotiempo import RegistroTiempo


class TerminalInterface:
    def __init__(self, registro_dao, empleado_dao, proyecto_dao, departamento_dao):
        self.registro_dao = registro_dao
        self.empleado_dao = empleado_dao
        self.proyecto_dao = proyecto_dao
        self.departamento_dao = departamento_dao

    def mostrar_menu(self):
        print("\n=== ECOTECH SOLUTIONS ===")
        print("1. Registrar empleado")
        print("2. Listar empleados")
        print("3. Registrar departamento")
        print("4. Listar departamentos")
        print("5. Registrar proyecto")
        print("6. Listar proyectos")
        print("7. Registrar tiempo")
        print("8. Listar registros de tiempo")
        print("9. Actualizar empleado")
        print("10. Eliminar empleado")
        print("11. Salir")

    def iniciar(self):
        while True:
            self.mostrar_menu()
            opcion = input("Seleccione una opción: ").strip()

            try:
                acciones = {
                    "1": self._registrar_empleado,
                    "2": lambda: self._listar(
                        self.empleado_dao, "EMPLEADOS"
                    ),
                    "3": self._registrar_departamento,
                    "4": lambda: self._listar(
                        self.departamento_dao, "DEPARTAMENTOS"
                    ),
                    "5": self._registrar_proyecto,
                    "6": lambda: self._listar(
                        self.proyecto_dao, "PROYECTOS"
                    ),
                    "7": self._registrar_tiempo,
                    "8": self._mostrar_listado_tiempos,
                    "9": self._actualizar_empleado,
                    "10": self._eliminar_empleado,
                }

                if opcion == "11":
                    print("Sistema finalizado.")
                    return

                accion = acciones.get(opcion)

                if accion:
                    accion()
                else:
                    print("Opción no válida.")

            except Exception as e:
                print(f"Error: {e}")

    def _registrar_empleado(self):
        print("\n--- NUEVO EMPLEADO ---")
        empleado = Empleado(
            input("Nombre: ").strip(),
            input("Dirección: ").strip(),
            input("Teléfono: ").strip(),
            input("Correo: ").strip(),
            self._pedir_fecha("Fecha de inicio (YYYY-MM-DD): "),
            self._pedir_float("Salario: "),
        )

        self.empleado_dao.insertar(empleado)
        print(f"Empleado registrado con ID {empleado.id_empleado}.")

    def _registrar_departamento(self):
        departamento = Departamento(
            input("Nombre del departamento: ").strip()
        )

        self.departamento_dao.insertar(departamento)
        print(
            f"Departamento registrado con ID "
            f"{departamento.id_departamento}."
        )

    def _registrar_proyecto(self):
        proyecto = Proyecto(
            input("Nombre: ").strip(),
            input("Descripción: ").strip(),
            self._pedir_fecha("Fecha de inicio (YYYY-MM-DD): "),
        )

        self.proyecto_dao.insertar(proyecto)
        print(f"Proyecto registrado con ID {proyecto.id_proyecto}.")

    def _registrar_tiempo(self):
        registro = RegistroTiempo(
            self._pedir_fecha("Fecha (YYYY-MM-DD): "),
            self._pedir_float("Horas trabajadas: "),
            input("Descripción del trabajo: ").strip(),
            self._pedir_int("ID empleado: "),
            self._pedir_int("ID proyecto: "),
        )

        self.registro_dao.insertar(registro)
        print(f"Registro de tiempo guardado con ID {registro.id_registro}.")

    def _listar(self, dao, titulo):
        print(f"\n--- {titulo} ---")
        datos = dao.obtener_todos()

        if not datos:
            print("No hay registros.")
            return

        for dato in datos:
            print(dato)

    def _mostrar_listado_tiempos(self):
        print("\n--- REGISTROS DE TIEMPO ---")
        registros = self.registro_dao.obtener_todos_con_detalles()

        if not registros:
            print("No hay registros.")
            return

        for registro in registros:
            print(
                f"ID: {registro['id_registro']} | "
                f"Fecha: {registro['fecha']} | "
                f"Empleado: {registro['empleado']} | "
                f"Proyecto: {registro['proyecto']} | "
                f"Horas: {registro['horas']} | "
                f"Descripción: {registro['descripcion']}"
            )

    def _actualizar_empleado(self):
        print("\n--- ACTUALIZAR EMPLEADO ---")
        id_empleado = self._pedir_int("ID del empleado: ")

        actual = self.empleado_dao.obtener_por_id(id_empleado)

        if actual is None:
            print("Empleado no encontrado.")
            return

        print(f"Empleado seleccionado: {actual['nombre']}")
        print("Introduce los nuevos datos del empleado.")

        empleado = Empleado(
            input("Nombre: ").strip(),
            input("Dirección: ").strip(),
            input("Teléfono: ").strip(),
            input("Correo: ").strip(),
            self._pedir_fecha("Fecha de inicio (YYYY-MM-DD): "),
            self._pedir_float("Salario: "),
            id_empleado=id_empleado,
            id_departamento=actual["id_departamento"],
        )

        confirmar = input(
            "¿Guardar los cambios? (s/n): "
        ).strip().lower()

        if confirmar == "s":
            actualizado = self.empleado_dao.actualizar(
                id_empleado, empleado
            )

            if actualizado:
                print("Empleado actualizado correctamente.")
            else:
                print("No se realizaron cambios.")
        else:
            print("Actualización cancelada.")

    def _eliminar_empleado(self):
        print("\n--- ELIMINAR EMPLEADO ---")
        id_empleado = self._pedir_int("ID del empleado: ")

        actual = self.empleado_dao.obtener_por_id(id_empleado)

        if actual is None:
            print("Empleado no encontrado.")
            return

        print(f"ID: {actual['id_empleado']}")
        print(f"Nombre: {actual['nombre']}")
        print(f"Correo: {actual['correo']}")

        confirmar = input(
            "¿Eliminar este empleado? (s/n): "
        ).strip().lower()

        if confirmar == "s":
            eliminado = self.empleado_dao.eliminar(id_empleado)

            if eliminado:
                print("Empleado eliminado correctamente.")
            else:
                print("No se pudo eliminar el empleado.")
        else:
            print("Operación cancelada.")

    @staticmethod
    def _pedir_int(mensaje):
        while True:
            try:
                return int(input(mensaje).strip())
            except ValueError:
                print("Ingrese un número entero válido.")

    @staticmethod
    def _pedir_float(mensaje):
        while True:
            try:
                valor = float(input(mensaje).strip())

                if valor < 0:
                    raise ValueError

                return valor

            except ValueError:
                print("Ingrese un número válido mayor o igual a 0.")

    @staticmethod
    def _pedir_fecha(mensaje):
        while True:
            try:
                return datetime.strptime(
                    input(mensaje).strip(), "%Y-%m-%d"
                ).date()
            except ValueError:
                print("Formato inválido. Use YYYY-MM-DD.")

