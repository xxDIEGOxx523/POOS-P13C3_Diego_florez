import re
import sys
from datetime import datetime
from getpass import getpass

from dominio.empleado import Empleado
from dominio.departamento import Departamento
from dominio.proyecto import Proyecto
from dominio.registrotiempo import RegistroTiempo
from dominio.usuario import Usuario
from semilla import cargar_semilla, imprimir_resumen
from servicios.permisos import exigir_admin, exigir_sesion
from servicios import gestion_empleados, mi_cuenta
from servicios.indicadores import (
    consultar_y_conservar_dolar,
    obtener_historial_dolar,
    IndicadorNoDisponible,
)


class TerminalInterface:
    ANCHO = 68

    def __init__(self, registro_dao, empleado_dao, proyecto_dao, departamento_dao,
                 usuario=None, autenticacion=None):
        self.registro_dao = registro_dao
        self.empleado_dao = empleado_dao
        self.proyecto_dao = proyecto_dao
        self.departamento_dao = departamento_dao
        self.usuario = usuario or {}
        self.autenticacion = autenticacion

    # -------------------- MENU E INTERACCION --------------------
    def mostrar_menu(self):
        exigir_sesion(self.usuario)
        linea = "=" * self.ANCHO
        print("\n" + linea)
        print("                 ECOTECH SOLUTIONS")
        print("          Sistema de gestión interna | " + self.usuario["rol"].upper())
        print(f"          Sesión: {self.usuario['nombre_usuario']}")
        print(linea)

        if self.usuario["rol"] == "admin":
            print("  ADMINISTRACIÓN")
            print("    [1] Registrar empleado")
            print("    [2] Listar empleados")
            print("    [3] Registrar departamento")
            print("    [4] Listar departamentos")
            print("    [5] Registrar proyecto")
            print("    [6] Listar proyectos")
            print("    [7] Registrar tiempo trabajado")
            print("    [8] Consultar registros laborales del sistema")
            print("    [9] Actualizar empleado")
            print("   [10] Eliminar empleado")
            print("   [12] Cargar semilla de datos ficticios")
            print("   [13] Consultar dólar observado (API)")
            print("   [14] Cambiar contraseña")
            print("   [15] Registrar cuenta de empleado")
            print("   [16] Consultar historial del dólar")
            print("   [11] Cerrar sesión")
        else:
            print("  MI CUENTA")
            print("    [1] Mi ficha")
            print("    [2] Mis registros laborales")
            print("    [3] Modificar mi nombre y correo")
            print("    [4] Consultar dólar observado (API)")
            print("    [5] Cambiar contraseña")
            print("    [6] Consultar historial del dólar")
            print("    [9] Cerrar sesión")
        print(linea)
        print("El sistema comprueba los permisos antes de ejecutar cada operación.")

    def iniciar(self):
        exigir_sesion(self.usuario)
        if self.usuario["rol"] == "admin":
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
                "13": self._consultar_dolar,
                "14": self._cambiar_password,
                "15": self._registrar_cuenta,
                "16": self._consultar_historial_dolar,
            }
            opcion_cerrar = "11"
        else:
            acciones = {
                "1": self._mostrar_mi_ficha,
                "2": self._mostrar_mis_registros,
                "3": self._actualizar_mis_datos,
                "4": self._consultar_dolar,
                "5": self._cambiar_password,
                "6": self._consultar_historial_dolar,
            }
            opcion_cerrar = "9"

        while True:
            self.mostrar_menu()
            try:
                opcion = self._pedir_texto("Seleccione una opcion: ", 2)
            except EOFError:
                print("\nEntrada finalizada.")
                return "salir"

            if opcion == opcion_cerrar:
                print("\nSesión cerrada.")
                return "logout"

            accion = acciones.get(opcion)
            if accion is None:
                print("Opcion no valida. Seleccione una opción disponible.")
                self._pausar()
                continue

            try:
                accion()
            except EOFError:
                print("\nEntrada finalizada.")
                return "salir"
            except (PermissionError, ValueError, TypeError) as error:
                print(f"\nOperación rechazada: {error}")
            except IndicadorNoDisponible as error:
                print(f"\n{error}")
            except Exception:
                print(
                    "\nNo se pudo completar la operación. "
                    "Revise la configuración y vuelva a intentarlo. "
                    "No se muestran detalles internos por seguridad."
                )

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
        exigir_admin(self.usuario)
        self._titulo("REGISTRAR EMPLEADO")
        empleado = Empleado(
            self._pedir_texto("Nombre", 100),
            self._pedir_texto("Direccion", 200),
            self._pedir_telefono(),
            self._pedir_correo(),
            self._pedir_fecha("Fecha de inicio (AAAA-MM-DD)"),
            self._pedir_float("Salario", minimo=0, maximo=9999999999.99),
        )
        gestion_empleados.registrar(self.usuario, self.empleado_dao, empleado)
        print(f"\nEmpleado registrado correctamente. ID asignado: {empleado.id_empleado}")

    def _registrar_departamento(self):
        exigir_admin(self.usuario)
        self._titulo("REGISTRAR DEPARTAMENTO")
        departamento = Departamento(
            self._pedir_texto("Nombre del departamento", 100)
        )
        self.departamento_dao.insertar(departamento)
        print(f"\nDepartamento registrado. ID asignado: {departamento.id_departamento}")

    def _registrar_proyecto(self):
        exigir_admin(self.usuario)
        self._titulo("REGISTRAR PROYECTO")
        proyecto = Proyecto(
            self._pedir_texto("Nombre del proyecto", 100),
            self._pedir_texto("Descripcion", 500),
            self._pedir_fecha("Fecha de inicio (AAAA-MM-DD)"),
        )
        self.proyecto_dao.insertar(proyecto)
        print(f"\nProyecto registrado correctamente. ID asignado: {proyecto.id_proyecto}")

    def _registrar_tiempo(self):
        exigir_admin(self.usuario)
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
        exigir_admin(self.usuario)
        self._titulo("LISTADO DE " + titulo)
        if titulo == "EMPLEADOS":
            datos = gestion_empleados.listar_todos(self.usuario, dao)
        else:
            exigir_admin(self.usuario)
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
        exigir_admin(self.usuario)
        self._titulo("REGISTROS DE TIEMPO")
        registros = gestion_empleados.listar_registros_laborales(self.usuario, self.registro_dao)
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
        exigir_admin(self.usuario)
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
            if gestion_empleados.actualizar(self.usuario, self.empleado_dao, id_empleado, empleado):
                print("Empleado actualizado correctamente.")
            else:
                print("No se detectaron cambios o no se actualizo el registro.")
        else:
            print("Actualizacion cancelada.")

    def _eliminar_empleado(self):
        exigir_admin(self.usuario)
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
            if gestion_empleados.eliminar(self.usuario, self.empleado_dao, id_empleado):
                print("Empleado eliminado correctamente.")
            else:
                print("No se pudo eliminar el empleado.")
        else:
            print("Eliminacion cancelada.")

    def _registrar_cuenta(self):
        exigir_admin(self.usuario)
        self._titulo("REGISTRAR CUENTA DE EMPLEADO")
        id_empleado = self._pedir_id_existente(self.empleado_dao, "empleado")
        nombre_usuario = self._pedir_nombre_usuario()
        clave = getpass("Contraseña (mínimo 10 caracteres, letras y números): ")
        confirmacion = getpass("Repita la contraseña: ")
        if clave != confirmacion:
            print("Las contraseñas no coinciden.")
            return
        cuenta_id = gestion_empleados.registrar_cuenta(
            self.usuario, self.autenticacion, id_empleado, nombre_usuario, clave
        )
        print(f"Cuenta de empleado creada correctamente. ID de cuenta: {cuenta_id}")

    def _pedir_nombre_usuario(self):
        while True:
            texto = self._pedir_texto("Nombre de usuario", Usuario.MAX_USUARIO)
            try:
                return Usuario.normalizar_usuario(texto)
            except (TypeError, ValueError) as error:
                print(error)

    def _mostrar_mi_ficha(self):
        ficha = mi_cuenta.mi_ficha(self.usuario, self.empleado_dao)
        self._titulo("MI FICHA")
        print(f"ID de empleado: {ficha['id_empleado']}")
        print(f"Nombre: {ficha['nombre']}")
        print(f"Correo: {ficha['correo']}")
        print(f"Teléfono: {ficha['telefono']}")
        print(f"Dirección: {ficha['direccion']}")
        print(f"Fecha de contrato: {ficha['fecha_inicio_contrato']}")
        print(f"Departamento: {ficha.get('id_departamento') or 'Sin departamento'}")

    def _mostrar_mis_registros(self):
        registros = mi_cuenta.mis_registros(self.usuario, self.registro_dao)
        self._titulo("MIS REGISTROS LABORALES")
        if not registros:
            print("No tienes registros laborales asociados.")
            return
        print(f"{'ID':<5} {'FECHA':<12} {'PROYECTO':<24} {'HORAS':>7} DESCRIPCIÓN")
        print("-" * 90)
        for registro in registros:
            print(
                f"{str(registro['id_registro']):<5} "
                f"{str(registro['fecha']):<12} "
                f"{self._cortar(registro['proyecto'], 24):<24} "
                f"{str(registro['horas']):>7} "
                f"{self._cortar(registro['descripcion'], 32)}"
            )
        print(f"\nTotal de registros propios: {len(registros)}")

    def _actualizar_mis_datos(self):
        from servicios.mi_cuenta import actualizar_mis_datos
        self._titulo("ACTUALIZAR MIS DATOS")
        ficha = mi_cuenta.mi_ficha(self.usuario, self.empleado_dao)
        print(f"Nombre actual: {ficha['nombre']}")
        print(f"Correo actual: {ficha['correo']}")
        nombre = self._pedir_texto("Nuevo nombre", 100)
        correo = self._pedir_correo()
        if not self._pedir_confirmacion("¿Guardar solo el nombre y correo? (s/n)"):
            print("Actualización cancelada.")
            return
        actualizado = actualizar_mis_datos(
            self.usuario, self.empleado_dao, nombre, correo
        )
        print("Datos propios actualizados." if actualizado else "No se detectaron cambios.")

    def _cambiar_password(self):
        exigir_sesion(self.usuario)
        from getpass import getpass
        self._titulo("CAMBIAR CONTRASEÑA")
        if not self.autenticacion or not self.usuario.get("id_usuario"):
            print("No hay una sesión autenticada disponible.")
            return
        actual = getpass("Contraseña actual (entrada oculta): ")
        nueva = getpass("Nueva contraseña (mínimo 10 caracteres, letras y números): ")
        repetir = getpass("Repita la nueva contraseña: ")
        if nueva != repetir:
            print("Las contraseñas nuevas no coinciden.")
            return
        try:
            self.autenticacion.cambiar_password(self.usuario["id_usuario"], actual, nueva)
            print("Contraseña actualizada correctamente.")
        except ValueError as error:
            print(f"No se pudo cambiar la contraseña: {error}")

    def _consultar_dolar(self):
        """Consulta, valida y conserva el dólar, con respaldo local autenticado."""
        exigir_sesion(self.usuario)
        self._titulo("CONSULTA DEL DÓLAR OBSERVADO")
        resultado = consultar_y_conservar_dolar(self.usuario)
        indicador = resultado.indicador
        print(f"Indicador: {indicador.nombre} ({indicador.codigo})")
        print(f"Valor: ${indicador.valor:,.2f} {indicador.unidad}")
        print(f"Fecha del dato: {indicador.fecha.isoformat()}")
        print(f"Origen del dato: {resultado.origen}")
        if resultado.guardado:
            print("Persistencia: confirmada en la base de datos.")
        elif resultado.mensaje:
            print(f"Aviso: {resultado.mensaje}")

        monto_usd = self._pedir_float(
            "Monto en USD para calcular una referencia en CLP (0 para omitir)",
            minimo=0,
            maximo=9999999999.99,
        )
        if monto_usd > 0:
            equivalente = monto_usd * indicador.valor
            print(
                f"\nReferencia: USD {monto_usd:,.2f} equivalen aproximadamente "
                f"a CLP ${equivalente:,.2f}."
            )
            print("Esta conversión es informativa y no reemplaza una liquidación de nómina.")

    def _consultar_historial_dolar(self):
        """Muestra los últimos indicadores persistidos sin consultar la API."""
        exigir_sesion(self.usuario)
        self._titulo("HISTORIAL LOCAL DEL DÓLAR")
        historial = obtener_historial_dolar(self.usuario, limite=20)
        if not historial:
            print("Todavía no hay indicadores guardados. Consulte el dólar primero.")
            return

        print(f"{'FECHA DEL DATO':<24} {'VALOR':>14} {'UNIDAD':<12} {'VERIFICADO EN':<22}")
        print("-" * 76)
        for fila in historial:
            fecha = str(fila.get("fecha", ""))[:19]
            verificado = str(fila.get("verificado_en", ""))[:19]
            valor = float(fila.get("valor", 0))
            print(
                f"{fecha:<24} {valor:>14,.2f} "
                f"{str(fila.get('unidad', '')):<12} {verificado:<22}"
            )
        print("\nHistorial recuperado desde la base de datos local; no se llamó a la API.")

    # -------------------- SEMILLA Y VALIDACION DE ENTRADAS --------------------
    def _cargar_semilla(self):
        exigir_admin(self.usuario)
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
