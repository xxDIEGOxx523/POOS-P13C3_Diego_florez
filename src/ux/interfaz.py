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
from servicios import (gestion_empleados, mi_cuenta, indicadores,
                        gestion_proyectos, gestion_departamentos, gestion_tiempos)


class TerminalInterface:
    ANCHO = 68

    def __init__(self, registro_dao, empleado_dao, proyecto_dao, departamento_dao,
                 usuario=None, autenticacion=None, indicador_dao=None):
        self.registro_dao = registro_dao
        self.empleado_dao = empleado_dao
        self.proyecto_dao = proyecto_dao
        self.departamento_dao = departamento_dao
        self.usuario = usuario or {}
        self.autenticacion = autenticacion
        self.indicador_dao = indicador_dao

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
            print("    [7] Registrar tiempo trabajado para un empleado")
            print("    [8] Consultar registros laborales del sistema")
            print("    [9] Actualizar empleado")
            print("   [10] Eliminar empleado")
            print("   [11] Cerrar sesión")
            print("   [12] Cargar semilla de datos ficticios")
            print("   [13] Indicadores: consultar dólar / ver historial")
            print("   [14] Mi ficha")
            print("   [15] Cambiar contraseña")
            print("   [16] Registrar cuenta de empleado")
            print("   [17] Asignar empleado a proyecto")
            print("   [18] Desasignar empleado de proyecto")
            print("   [19] Actualizar departamento")
            print("   [20] Eliminar departamento")
            print("   [21] Asignar gerente a departamento")
            print("   [22] Actualizar proyecto")
            print("   [23] Eliminar proyecto")
            print("   [24] Actualizar registro de tiempo")
            print("   [25] Eliminar registro de tiempo")
            print("   [26] Modificar mi perfil")
        else:
            print("  MI CUENTA")
            print("    [1] Mi ficha")
            print("    [2] Mis proyectos asignados")
            print("    [3] Registrar horas en un proyecto asignado")
            print("    [4] Indicadores: consultar dólar / ver historial")
            print("    [5] Mis registros laborales")
            print("    [6] Modificar mi nombre y correo")
            print("    [7] Cambiar contraseña")
            print("    [9] Cerrar sesión")
        print(linea)
        print("Los servicios comprueban la sesión y el rol antes de acceder a los DAO.")

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
                "13": self._menu_indicadores,
                "14": self._mostrar_mi_ficha,
                "15": self._cambiar_password,
                "16": self._registrar_cuenta,
                "17": self._asignar_empleado_proyecto,
                "18": self._desasignar_empleado_proyecto,
                "19": self._actualizar_departamento,
                "20": self._eliminar_departamento,
                "21": self._asignar_gerente,
                "22": self._actualizar_proyecto,
                "23": self._eliminar_proyecto,
                "24": self._actualizar_registro_tiempo,
                "25": self._eliminar_registro_tiempo,
                "26": self._actualizar_mis_datos,
            }
            opcion_cerrar = "11"
        else:
            acciones = {
                "1": self._mostrar_mi_ficha,
                "2": self._mostrar_mis_proyectos,
                "3": self._registrar_mis_horas,
                "4": self._menu_indicadores,
                "5": self._mostrar_mis_registros,
                "6": self._actualizar_mis_datos,
                "7": self._cambiar_password,
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
                print("Opción no válida. Seleccione una opción disponible.")
                self._pausar()
                continue
            try:
                accion()
            except EOFError:
                print("\nEntrada finalizada.")
                return "salir"
            except (PermissionError, ValueError, TypeError) as error:
                print(f"\nOperación rechazada: {error}")
            except Exception:
                # No se exponen trazas, SQL, credenciales ni detalles internos al usuario.
                print("\nNo se pudo completar la operación. Revise la configuración o los datos e intente nuevamente.")
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
        gestion_departamentos.registrar(self.usuario, self.departamento_dao, departamento)
        print(f"\nDepartamento registrado. ID asignado: {departamento.id_departamento}")

    def _registrar_proyecto(self):
        exigir_admin(self.usuario)
        self._titulo("REGISTRAR PROYECTO")
        proyecto = Proyecto(
            self._pedir_texto("Nombre del proyecto", 100),
            self._pedir_texto("Descripcion", 500),
            self._pedir_fecha("Fecha de inicio (AAAA-MM-DD)"),
        )
        gestion_proyectos.registrar(self.usuario, self.proyecto_dao, proyecto)
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
        gestion_tiempos.registrar(self.usuario, self.registro_dao, registro)
        print(f"\nRegistro de tiempo guardado. ID asignado: {registro.id_registro}")

    # -------------------- CONSULTAS Y TABLAS --------------------
    def _listar(self, dao, titulo):
        exigir_admin(self.usuario)
        self._titulo("LISTADO DE " + titulo)
        if titulo == "EMPLEADOS":
            datos = gestion_empleados.listar_todos(self.usuario, dao)
        elif titulo == "DEPARTAMENTOS":
            datos = gestion_departamentos.listar(self.usuario, dao)
        elif titulo == "PROYECTOS":
            datos = gestion_proyectos.listar(self.usuario, dao)
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

    def _menu_indicadores(self):
        exigir_sesion(self.usuario)
        while True:
            self._titulo("INDICADORES ECONÓMICOS")
            print("1. Consultar dólar observado (API y guardar/actualizar)")
            print("2. Ver historial guardado en la base local")
            print("0. Volver al menú principal")
            opcion = self._pedir_texto("Seleccione una opción: ", 1)
            if opcion == "1":
                self._consultar_dolar()
            elif opcion == "2":
                self._mostrar_historial_indicador()
            elif opcion == "0":
                return
            else:
                print("Opción no válida.")

    def _consultar_dolar(self):
        exigir_sesion(self.usuario)
        self._titulo("CONSULTA DEL DÓLAR OBSERVADO")
        if self.indicador_dao is None:
            print("El acceso al historial no está configurado.")
            return
        resultado = indicadores.consultar_indicador(self.usuario, self.indicador_dao)
        dato = resultado.get("indicador")
        print(resultado.get("mensaje", "Consulta finalizada."))
        if dato is None:
            print("No hay información disponible para mostrar.")
            return
        print(f"Valor: ${dato.valor:,.2f} {dato.unidad}")
        print(f"Fecha del dato: {dato.fecha}")
        print(f"Fuente: {dato.fuente}")
        print(f"Origen de esta respuesta: {resultado.get('origen')}")
        if resultado.get("origen") == "API":
            print("Guardado local confirmado." if resultado.get("guardado") else
                  "Aviso: el dato API se recibió, pero no se confirmó su guardado local.")
        else:
            print(f"Última verificación registrada: {dato.verificado_en}")
            print("Este valor proviene de la BD local y no se presenta como una cotización recién actualizada.")

    def _mostrar_historial_indicador(self):
        exigir_sesion(self.usuario)
        self._titulo("HISTORIAL LOCAL DEL DÓLAR")
        if self.indicador_dao is None:
            print("El historial no está configurado.")
            return
        historial = indicadores.obtener_historial(self.usuario, self.indicador_dao)
        if not historial:
            print("Todavía no existen observaciones guardadas.")
            return
        print(f"{'FECHA':<14} {'VALOR':>14} {'UNIDAD':<12} {'FUENTE':<18} ÚLTIMA VERIFICACIÓN")
        print("-" * 90)
        for dato in historial:
            print(f"{dato.fecha:<14} {dato.valor:>14,.2f} {dato.unidad:<12} {dato.fuente:<18} {dato.verificado_en}")
        print("\nOrigen: base de datos local. Esta consulta no llama a la API.")

    def _mostrar_mis_proyectos(self):
        exigir_sesion(self.usuario)
        self._titulo("MIS PROYECTOS ASIGNADOS")
        proyectos = mi_cuenta.mis_proyectos(self.usuario, self.proyecto_dao)
        if not proyectos:
            print("No tienes proyectos asignados actualmente.")
            return
        print(f"{'ID':<6} {'NOMBRE':<28} {'FECHA INICIO':<14} DESCRIPCIÓN")
        print("-" * 90)
        for proyecto in proyectos:
            print(f"{proyecto['id_proyecto']:<6} {self._cortar(proyecto['nombre'], 28):<28} {str(proyecto['fecha_inicio']):<14} {self._cortar(proyecto['descripcion'], 35)}")

    def _registrar_mis_horas(self):
        exigir_sesion(self.usuario)
        self._titulo("REGISTRAR MIS HORAS")
        proyectos = mi_cuenta.mis_proyectos(self.usuario, self.proyecto_dao)
        if not proyectos:
            print("No puedes registrar horas porque no tienes proyectos asignados.")
            return
        print("Proyectos disponibles para tu cuenta:")
        for proyecto in proyectos:
            print(f"  [{proyecto['id_proyecto']}] {proyecto['nombre']}")
        ids = {p['id_proyecto'] for p in proyectos}
        while True:
            id_proyecto = self._pedir_int("ID del proyecto asignado")
            if id_proyecto in ids:
                break
            print("Selecciona un proyecto de la lista asignada a tu cuenta.")
        fecha = self._pedir_fecha("Fecha trabajada (AAAA-MM-DD)")
        horas = self._pedir_float("Horas trabajadas (0.01 a 24)", minimo=0.01, maximo=24)
        descripcion = self._pedir_texto("Descripción del trabajo", 500)
        registro = mi_cuenta.registrar_horas(
            self.usuario, self.proyecto_dao, self.registro_dao,
            id_proyecto, fecha, horas, descripcion,
        )
        print(f"Registro propio guardado. ID: {registro.id_registro}")

    def _asignar_empleado_proyecto(self):
        exigir_admin(self.usuario)
        self._titulo("ASIGNAR EMPLEADO A PROYECTO")
        id_proyecto = self._pedir_id_existente(self.proyecto_dao, "proyecto")
        id_empleado = self._pedir_id_existente(self.empleado_dao, "empleado")
        creado = gestion_proyectos.asignar_empleado(
            self.usuario, self.proyecto_dao, self.empleado_dao, id_proyecto, id_empleado
        )
        print("Asignación creada correctamente." if creado else "El empleado ya estaba asignado a ese proyecto.")

    def _desasignar_empleado_proyecto(self):
        exigir_admin(self.usuario)
        self._titulo("DESASIGNAR EMPLEADO DE PROYECTO")
        id_proyecto = self._pedir_id_existente(self.proyecto_dao, "proyecto")
        id_empleado = self._pedir_id_existente(self.empleado_dao, "empleado")
        resultado = gestion_proyectos.desasignar_empleado(
            self.usuario, self.proyecto_dao, id_proyecto, id_empleado
        )
        print("Asignación eliminada." if resultado else "No existía esa asignación.")

    def _actualizar_departamento(self):
        exigir_admin(self.usuario)
        self._titulo("ACTUALIZAR DEPARTAMENTO")
        id_departamento = self._pedir_id_existente(self.departamento_dao, "departamento")
        actual = self.departamento_dao.obtener_por_id(id_departamento)
        departamento = Departamento(self._pedir_texto("Nuevo nombre", 100), id_departamento=id_departamento,
                                    id_gerente=actual.get("id_gerente"))
        if self._pedir_confirmacion("¿Guardar el nuevo nombre? (s/n)"):
            resultado = gestion_departamentos.actualizar(
                self.usuario, self.departamento_dao, id_departamento, departamento
            )
            print("Departamento actualizado." if resultado else "No se detectaron cambios.")
        else:
            print("Actualización cancelada.")

    def _eliminar_departamento(self):
        exigir_admin(self.usuario)
        self._titulo("ELIMINAR DEPARTAMENTO")
        id_departamento = self._pedir_id_existente(self.departamento_dao, "departamento")
        if not self._pedir_confirmacion("¿Confirmar eliminación? (s/n)"):
            print("Eliminación cancelada.")
            return
        resultado = gestion_departamentos.eliminar(self.usuario, self.departamento_dao, id_departamento)
        print("Departamento eliminado." if resultado else "No se pudo eliminar el departamento.")

    def _asignar_gerente(self):
        exigir_admin(self.usuario)
        self._titulo("ASIGNAR GERENTE A DEPARTAMENTO")
        id_departamento = self._pedir_id_existente(self.departamento_dao, "departamento")
        id_empleado = self._pedir_id_existente(self.empleado_dao, "empleado")
        resultado = gestion_departamentos.asignar_gerente(
            self.usuario, self.departamento_dao, self.empleado_dao,
            id_departamento, id_empleado,
        )
        print("Gerente asignado correctamente." if resultado else "No se pudo asignar el gerente.")

    def _actualizar_proyecto(self):
        exigir_admin(self.usuario)
        self._titulo("ACTUALIZAR PROYECTO")
        id_proyecto = self._pedir_id_existente(self.proyecto_dao, "proyecto")
        proyecto = Proyecto(
            self._pedir_texto("Nuevo nombre", 100),
            self._pedir_texto("Nueva descripción", 500),
            self._pedir_fecha("Nueva fecha de inicio (AAAA-MM-DD)"),
            id_proyecto=id_proyecto,
        )
        if self._pedir_confirmacion("¿Guardar los cambios? (s/n)"):
            resultado = gestion_proyectos.actualizar(self.usuario, self.proyecto_dao, id_proyecto, proyecto)
            print("Proyecto actualizado." if resultado else "No se detectaron cambios.")
        else:
            print("Actualización cancelada.")

    def _eliminar_proyecto(self):
        exigir_admin(self.usuario)
        self._titulo("ELIMINAR PROYECTO")
        id_proyecto = self._pedir_id_existente(self.proyecto_dao, "proyecto")
        print("Aviso: también se eliminarán relaciones y registros vinculados según las claves foráneas.")
        if not self._pedir_confirmacion("¿Confirmar eliminación? (s/n)"):
            print("Eliminación cancelada.")
            return
        resultado = gestion_proyectos.eliminar(self.usuario, self.proyecto_dao, id_proyecto)
        print("Proyecto eliminado." if resultado else "No se pudo eliminar el proyecto.")

    def _actualizar_registro_tiempo(self):
        exigir_admin(self.usuario)
        self._titulo("ACTUALIZAR REGISTRO DE TIEMPO")
        id_registro = self._pedir_int("ID del registro")
        actual = self.registro_dao.obtener_por_id(id_registro)
        if actual is None:
            print("No existe ese registro.")
            return
        id_empleado = self._pedir_id_existente(self.empleado_dao, "empleado")
        id_proyecto = self._pedir_id_existente(self.proyecto_dao, "proyecto")
        registro = RegistroTiempo(
            self._pedir_fecha("Fecha (AAAA-MM-DD)"),
            self._pedir_float("Horas trabajadas (0.01 a 24)", 0.01, 24),
            self._pedir_texto("Descripción", 500), id_empleado, id_proyecto, id_registro,
        )
        if self._pedir_confirmacion("¿Guardar los cambios? (s/n)"):
            actualizado = gestion_tiempos.actualizar(
                self.usuario, self.registro_dao, id_registro, registro
            )
            print("Registro actualizado." if actualizado else "No se detectaron cambios.")
        else:
            print("Actualización cancelada.")

    def _eliminar_registro_tiempo(self):
        exigir_admin(self.usuario)
        self._titulo("ELIMINAR REGISTRO DE TIEMPO")
        id_registro = self._pedir_int("ID del registro")
        if not self._pedir_confirmacion("¿Confirmar eliminación? (s/n)"):
            print("Eliminación cancelada.")
            return
        eliminado = gestion_tiempos.eliminar(self.usuario, self.registro_dao, id_registro)
        print("Registro eliminado." if eliminado else "No existe ese registro.")

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
