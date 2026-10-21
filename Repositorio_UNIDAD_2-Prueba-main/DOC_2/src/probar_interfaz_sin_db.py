"""Prueba interactiva de la interfaz EcoTech sin conectar con MySQL.

Ejecutar desde la carpeta src:
    python probar_interfaz_sin_db.py

Los datos se guardan solo en memoria y desaparecen al cerrar el programa.
Este archivo NO reemplaza main.py ni prueba las consultas SQL reales.
"""

from datetime import date

from ux.interfaz import TerminalInterface


class EmpleadoDAOFalso:
    def __init__(self):
        self.datos = {}
        self.siguiente_id = 1

    @staticmethod
    def _a_dict(empleado):
        return {
            "id_empleado": empleado.id_empleado,
            "nombre": empleado.nombre,
            "direccion": empleado.direccion,
            "telefono": empleado.telefono,
            "correo": empleado.correo,
            "fecha_inicio_contrato": empleado.fecha_inicio_contrato,
            "salario": empleado.salario,
            "id_departamento": empleado.id_departamento,
        }

    def insertar(self, empleado):
        empleado.id_empleado = self.siguiente_id
        self.siguiente_id += 1
        self.datos[empleado.id_empleado] = self._a_dict(empleado)
        return empleado

    def obtener_por_id(self, id_empleado):
        registro = self.datos.get(id_empleado)
        return registro.copy() if registro else None

    def obtener_todos(self):
        return [self.datos[i].copy() for i in sorted(self.datos)]

    def actualizar(self, id_empleado, empleado):
        if id_empleado not in self.datos:
            return False
        empleado.id_empleado = id_empleado
        self.datos[id_empleado] = self._a_dict(empleado)
        return True

    def eliminar(self, id_empleado):
        return self.datos.pop(id_empleado, None) is not None


class DepartamentoDAOFalso:
    def __init__(self):
        self.datos = {}
        self.siguiente_id = 1

    def insertar(self, departamento):
        departamento.id_departamento = self.siguiente_id
        self.siguiente_id += 1
        self.datos[departamento.id_departamento] = {
            "id_departamento": departamento.id_departamento,
            "nombre": departamento.nombre,
            "id_gerente": departamento.id_gerente,
        }
        return departamento

    def obtener_todos(self):
        return [self.datos[i].copy() for i in sorted(self.datos)]

    def asignar_gerente(self, id_departamento, id_empleado):
        if id_departamento not in self.datos:
            return False
        self.datos[id_departamento]["id_gerente"] = id_empleado
        return True


class ProyectoDAOFalso:
    def __init__(self):
        self.datos = {}
        self.siguiente_id = 1
        self.asignaciones = set()

    def insertar(self, proyecto):
        proyecto.id_proyecto = self.siguiente_id
        self.siguiente_id += 1
        self.datos[proyecto.id_proyecto] = {
            "id_proyecto": proyecto.id_proyecto,
            "nombre": proyecto.nombre,
            "descripcion": proyecto.descripcion,
            "fecha_inicio": proyecto.fecha_inicio,
        }
        return proyecto

    def obtener_por_id(self, id_proyecto):
        registro = self.datos.get(id_proyecto)
        return registro.copy() if registro else None

    def obtener_todos(self):
        return [self.datos[i].copy() for i in sorted(self.datos)]

    def asignar_empleado(self, id_proyecto, id_empleado):
        pareja = (id_proyecto, id_empleado)
        if pareja in self.asignaciones:
            return False
        self.asignaciones.add(pareja)
        return True

    def tiene_asignacion(self, id_proyecto, id_empleado):
        return (id_proyecto, id_empleado) in self.asignaciones


class RegistroTiempoDAOFalso:
    def __init__(self, empleado_dao, proyecto_dao):
        self.empleado_dao = empleado_dao
        self.proyecto_dao = proyecto_dao
        self.datos = {}
        self.siguiente_id = 1

    def insertar(self, registro):
        registro.id_registro = self.siguiente_id
        self.siguiente_id += 1
        self.datos[registro.id_registro] = registro
        return registro

    def obtener_todos(self):
        resultado = []
        for registro in self.datos.values():
            resultado.append({
                "id_registro": registro.id_registro,
                "id_empleado": registro.id_empleado,
                "id_proyecto": registro.id_proyecto,
                "fecha": registro.fecha,
                "horas_trabajadas": registro.horas_trabajadas,
                "descripcion_trabajo": registro.descripcion_trabajo,
            })
        return resultado

    def obtener_todos_con_detalles(self):
        resultado = []
        for registro in self.datos.values():
            empleado = self.empleado_dao.obtener_por_id(registro.id_empleado)
            proyecto = self.proyecto_dao.obtener_por_id(registro.id_proyecto)
            if empleado is None or proyecto is None:
                continue
            resultado.append({
                "id_registro": registro.id_registro,
                "fecha": registro.fecha,
                "empleado": empleado["nombre"],
                "proyecto": proyecto["nombre"],
                "horas": registro.horas_trabajadas,
                "descripcion": registro.descripcion_trabajo,
            })
        return resultado


def main():
    print("\nMODO DE PRUEBA: SIN CONEXION A MYSQL")
    print("Los datos introducidos solo existen mientras esta ventana siga abierta.\n")

    empleado_dao = EmpleadoDAOFalso()
    departamento_dao = DepartamentoDAOFalso()
    proyecto_dao = ProyectoDAOFalso()
    registro_dao = RegistroTiempoDAOFalso(empleado_dao, proyecto_dao)

    app = TerminalInterface(
        registro_dao,
        empleado_dao,
        proyecto_dao,
        departamento_dao,
    )
    app.iniciar()


if __name__ == "__main__":
    main()
