import re
import sys
from datetime import datetime

from dominio.empleado import Empleado
from dominio.departamento import Departamento
from dominio.proyecto import Proyecto
from dominio.registrotiempo import RegistroTiempo
from semilla import cargar_semilla, imprimir_resumen


class TerminalInterface:
    ANCHO = 68

    def __init__(self, registro_dao, empleado_dao, proyecto_dao, departamento_dao):
        self.registro_dao = registro_dao
        self.empleado_dao = empleado_dao
        self.proyecto_dao = proyecto_dao
        self.departamento_dao = departamento_dao

    # -------------------- MENU E INTERACCION --------------------
    def mostrar_menu(self):
        linea = "=" * self.ANCHO
        print("\n" + linea)
        print("                 ECOTECH SOLUTIONS")
        print("             Sistema de gestion interna")
        print(linea)
        print("  EMPLEADOS")
        print("    [1] Registrar empleado")
        print("    [2] Listar empleados")
        print("    [9] Actualizar empleado")
        print("   [10] Eliminar empleado")
        print("  ORGANIZACION")
        print("    [3] Registrar departamento")
        print("    [4] Listar departamentos")
        print("  PROYECTOS Y TIEMPOS")
        print("    [5] Registrar proyecto")
        print("    [6] Listar proyectos")
        print("    [7] Registrar tiempo trabajado")
        print("    [8] Listar registros de tiempo")
        print("  SISTEMA")
        print("   [11] Salir")
        print("   [12] Cargar semilla de datos ficticios")
        print(linea)
        print("Los campos tienen limites de longitud y formato.")

    def iniciar(self):
        acciones = {
            "1": self._registrar_empleado,
            "2": lambda: self._listar(self.empleado_dao, "EMPLEADOS"),
            "3": self._registrar_departamento,
            "4": lambda: self._listar(self.departamento_dao, "DEPARTAMENTOS"),
            "5": self._registrar_proyecto,
            "6": lambda: self._listar(self.proyecto_dao, "PROYECTOS"),
            "7": self._registrar_tiempo,
            "8": self._mostrar_listado_tiempos,
            "9": self._actualizar_empleado,
            "10": self._eliminar_empleado,
            "12": self._cargar_semilla,
        }

        while True:
            self.mostrar_menu()
            try:
                opcion = self._pedir_texto("Seleccione una opcion: ", 2)
            except EOFError:
                print("\nEntrada finalizada. Sistema cerrado.")
                return

            if opcion == "11":
                print("\nSistema finalizado.")
                return

            accion = acciones.get(opcion)
            if accion is None:
                print("Opcion no valida. Seleccione un numero del menu.")
                self._pausar()
                continue

            try:
                accion()
            except EOFError:
                print("\nEntrada finalizada. Sistema cerrado.")
                return
            except Exception as error:
                print(f"\nNo se pudo completar la operacion: {error}")

            # Mantiene el resultado visible en pantalla hasta que la persona continue.
            self._pausar()

    @staticmethod
    def _titulo(texto):
        print("\n" + "-" * 68)
        print(f"  {texto}")
        print("-" * 68)

    def _pausar(self):
        while True:
            try:
                self._leer_linea_limitada(
                    "\nPresione Enter para volver al menu principal: ", 1
                )
                return
            except ValueError as error:
                print(error)
            except EOFError:
                return

    # -------------------- REGISTROS --------------------
    def _registrar_empleado(self):
        self._titulo("REGISTRAR EMPLEADO")
        empleado = Empleado(
            self._pedir_texto("Nombre", 100),
            self._pedir_texto("Direccion", 200),
            self._pedir_telefono(),
            self._pedir_correo(),
            self._pedir_fecha("Fecha de inicio (AAAA-MM-DD)"),
            self._pedir_float("Salario", minimo=0, maximo=9999999999.99),
        )
        self.empleado_dao.insertar(empleado)
        print(f"\nEmpleado registrado correctamente. ID asignado: {empleado.id_empleado}")

    def _registrar_departamento(self):
        self._titulo("REGISTRAR DEPARTAMENTO")
        departamento = Departamento(
            self._pedir_texto("Nombre del departamento", 100)
        )
        self.departamento_dao.insertar(departamento)
        print(f"\nDepartamento registrado. ID asignado: {departamento.id_departamento}")

    def _registrar_proyecto(self):
        self._titulo("REGISTRAR PROYECTO")
        proyecto = Proyecto(
            self._pedir_texto("Nombre del proyecto", 100),
            self._pedir_texto("Descripcion", 500),
            self._pedir_fecha("Fecha de inicio (AAAA-MM-DD)"),
        )
        self.proyecto_dao.insertar(proyecto)
        print(f"\nProyecto registrado correctamente. ID asignado: {proyecto.id_proyecto}")

    def _registrar_tiempo(self):
        self._titulo("REGISTRAR TIEMPO TRABAJADO")
        id_empleado = self._pedir_id_existente(self.empleado_dao, "empleado")
        id_proyecto = self._pedir_id_existente(self.proyecto_dao, "proyecto")
        registro = RegistroTiempo(
            self._pedir_fecha("Fecha trabajada (AAAA-MM-DD)"),
            self._pedir_float("Horas trabajadas (0.01 a 24)", minimo=0.01, maximo=24),
            self._pedir_texto("Descripcion del trabajo", 500),
            id_empleado,
            id_proyecto,
        )
        self.registro_dao.insertar(registro)
        print(f"\nRegistro de tiempo guardado. ID asignado: {registro.id_registro}")

    # -------------------- CONSULTAS Y TABLAS --------------------
    def _listar(self, dao, titulo):
        self._titulo("LISTADO DE " + titulo)
        datos = dao.obtener_todos()
        if not datos:
            print("No hay registros para mostrar.")
            return

        if titulo == "EMPLEADOS":
            print(f"{'ID':<6} {'NOMBRE':<22} {'CORREO':<28} {'TELEFONO':<13} {'SALARIO':>12}")
            print("-" * 84)
            for d in datos:
                print(
                    f"{str(d.get('id_empleado', '')):<6} "
                    f"{self._cortar(d.get('nombre', ''), 22):<22} "
                    f"{self._cortar(d.get('correo', ''), 28):<28} "
                    f"{self._cortar(d.get('telefono', ''), 13):<13} "
                    f"{str(d.get('salario', '')):>12}"
                )
        elif titulo == "DEPARTAMENTOS":
            print(f"{'ID':<8} {'NOMBRE':<38} {'ID GERENTE':>12}")
            print("-" * 62)
            for d in datos:
                print(
                    f"{str(d.get('id_departamento', '')):<8} "
                    f"{self._cortar(d.get('nombre', ''), 38):<38} "
                    f"{str(d.get('id_gerente') or '-'):>12}"
                )
        elif titulo == "PROYECTOS":
            print(f"{'ID':<6} {'NOMBRE':<22} {'FECHA INICIO':<14} DESCRIPCION")
            print("-" * 84)
            for d in datos:
                print(
                    f"{str(d.get('id_proyecto', '')):<6} "
                    f"{self._cortar(d.get('nombre', ''), 22):<22} "
                    f"{str(d.get('fecha_inicio', '')):<14} "
                    f"{self._cortar(d.get('descripcion', ''), 38)}"
                )
        else:
            for dato in datos:
                print(dato)
        print(f"\nTotal de registros: {len(datos)}")

    def _mostrar_listado_tiempos(self):
        self._titulo("REGISTROS DE TIEMPO")
        registros = self.registro_dao.obtener_todos_con_detalles()
        if not registros:
            print("No hay registros para mostrar.")
            return

        print(f"{'ID':<5} {'FECHA':<12} {'EMPLEADO':<20} {'PROYECTO':<20} {'HORAS':>7} DESCRIPCION")
        print("-" * 100)
        for r in registros:
            print(
                f"{str(r['id_registro']):<5} "
                f"{str(r['fecha']):<12} "
                f"{self._cortar(r['empleado'], 20):<20} "
                f"{self._cortar(r['proyecto'], 20):<20} "
                f"{str(r['horas']):>7} "
                f"{self._cortar(r['descripcion'], 32)}"
            )
        print(f"\nTotal de registros: {len(registros)}")

    # -------------------- ACTUALIZAR Y ELIMINAR --------------------
    def _actualizar_empleado(self):
        self._titulo("ACTUALIZAR EMPLEADO")
        id_empleado = self._pedir_int("ID del empleado")
        actual = self.empleado_dao.obtener_por_id(id_empleado)

        if actual is None:
            print("No existe un empleado con ese ID.")
            return

        print(f"Empleado seleccionado: {actual['nombre']}")
        print("Introduzca los nuevos datos. Todos los campos solicitados se reemplazaran.")
        empleado = Empleado(
            self._pedir_texto("Nombre", 100),
            self._pedir_texto("Direccion", 200),
            self._pedir_telefono(),
            self._pedir_correo(),
            self._pedir_fecha("Fecha de inicio (AAAA-MM-DD)"),
            self._pedir_float("Salario", minimo=0, maximo=9999999999.99),
            id_empleado=id_empleado,
            id_departamento=actual["id_departamento"],
        )

        if self._pedir_confirmacion("¿Guardar los cambios? (s/n)"):
            if self.empleado_dao.actualizar(id_empleado, empleado):
                print("Empleado actualizado correctamente.")
            else:
                print("No se detectaron cambios o no se actualizo el registro.")
        else:
            print("Actualizacion cancelada.")

    def _eliminar_empleado(self):
        self._titulo("ELIMINAR EMPLEADO")
        id_empleado = self._pedir_int("ID del empleado")
        actual = self.empleado_dao.obtener_por_id(id_empleado)

        if actual is None:
            print("No existe un empleado con ese ID.")
            return

        print(f"ID: {actual['id_empleado']}")
        print(f"Nombre: {actual['nombre']}")
        print(f"Correo: {actual['correo']}")
        print("Aviso: sus registros de tiempo relacionados pueden eliminarse tambien.")

        if self._pedir_confirmacion("¿Confirma la eliminacion? (s/n)"):
            if self.empleado_dao.eliminar(id_empleado):
                print("Empleado eliminado correctamente.")
            else:
                print("No se pudo eliminar el empleado.")
        else:
            print("Eliminacion cancelada.")

    def _cargar_semilla(self):
        self._titulo("CARGAR SEMILLA DE DATOS FICTICIOS")
        print("Se prepararan hasta 10 registros de demostracion en cada tabla.")
        print("Los datos no pertenecientes a la semilla no se borraran.")
        print("Si ya existen registros de semilla, no se duplicaran.\n")

        if not self._pedir_confirmacion("¿Desea cargar la semilla? (s/n)"):
            print("Carga cancelada.")
            return

        resumen = cargar_semilla(
            self.registro_dao,
            self.empleado_dao,
            self.proyecto_dao,
            self.departamento_dao,
        )
        imprimir_resumen(resumen)

    # -------------------- VALIDACION DE ENTRADAS --------------------
    @staticmethod
    def _leer_linea_limitada(mensaje, maximo):
        """Lee como maximo unos pocos caracteres y descarta el resto de una linea larga."""
        sys.stdout.write(f"{mensaje} [max. {maximo} caracteres]: ")
        sys.stdout.flush()

        linea = sys.stdin.readline(maximo + 2)
        if linea == "":
            raise EOFError("No se recibio mas entrada.")

        if "\n" in linea:
            valor = linea.split("\n", 1)[0]
            if valor.endswith("\r"):
                valor = valor[:-1]
            if len(valor) > maximo:
                raise ValueError(f"El limite es de {maximo} caracteres. Intente nuevamente.")
            return valor

        if len(linea) > maximo:
            # Descarta el resto de la linea por bloques, sin guardarla completa en memoria.
            while True:
                resto = sys.stdin.readline(4096)
                if not resto or resto.endswith("\n"):
                    break
            raise ValueError(f"El limite es de {maximo} caracteres. Intente nuevamente.")

        return linea[:-1] if linea.endswith("\r") else linea

    @classmethod
    def _pedir_texto(cls, mensaje, maximo):
        while True:
            try:
                valor = cls._leer_linea_limitada(mensaje, maximo).strip()
            except ValueError as error:
                print(error)
                continue

            if not valor:
                print("Este campo es obligatorio. No puede quedar vacio.")
                continue
            if len(valor) > maximo:
                print(f"El limite es de {maximo} caracteres.")
                continue
            return valor

    def _pedir_correo(self):
        patron = r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
        while True:
            correo = self._pedir_texto("Correo", 150)
            if re.fullmatch(patron, correo):
                return correo
            print("Correo invalido. Ejemplo: usuario@empresa.cl")

    def _pedir_telefono(self):
        while True:
            telefono = self._pedir_texto("Telefono", 30)
            digitos = re.sub(r"\D", "", telefono)
            if re.fullmatch(r"[0-9()+ -]+", telefono) and 7 <= len(digitos) <= 15:
                return telefono
            print("Telefono invalido. Use de 7 a 15 digitos y solo numeros, +, parentesis, espacios o guiones.")

    def _pedir_int(self, mensaje):
        while True:
            texto = self._pedir_texto(mensaje, 10)
            if not re.fullmatch(r"[0-9]+", texto):
                print("Ingrese un numero entero positivo.")
                continue
            valor = int(texto)
            if not 1 <= valor <= 2147483647:
                print("El numero debe estar entre 1 y 2147483647.")
                continue
            return valor

    def _pedir_float(self, mensaje, minimo=0, maximo=9999999999.99):
        while True:
            texto = self._pedir_texto(mensaje, 20)
            if not re.fullmatch(r"[0-9]+(?:[.,][0-9]{1,2})?", texto):
                print("Ingrese un numero valido con hasta 2 decimales. No use separadores de miles.")
                continue

            valor = float(texto.replace(",", "."))
            if valor < minimo or valor > maximo:
                print(f"El valor debe estar entre {minimo} y {maximo}.")
                continue
            return valor

    def _pedir_fecha(self, mensaje):
        while True:
            texto = self._pedir_texto(mensaje, 10)
            try:
                return datetime.strptime(texto, "%Y-%m-%d").date()
            except ValueError:
                print("Fecha invalida. Use AAAA-MM-DD y una fecha real, por ejemplo 2026-10-15.")

    def _pedir_id_existente(self, dao, tipo):
        while True:
            identificador = self._pedir_int(f"ID del {tipo}")
            if dao.obtener_por_id(identificador) is not None:
                return identificador
            print(f"No existe un {tipo} con ID {identificador}. Intente nuevamente.")

    def _pedir_confirmacion(self, mensaje):
        while True:
            respuesta = self._pedir_texto(mensaje, 1).lower()
            if respuesta in ("s", "n"):
                return respuesta == "s"
            print("Responda solamente s o n.")

    @staticmethod
    def _cortar(valor, ancho):
        texto = str(valor if valor is not None else "")
        if len(texto) <= ancho:
            return texto
        return texto[:max(0, ancho - 3)] + "..."
