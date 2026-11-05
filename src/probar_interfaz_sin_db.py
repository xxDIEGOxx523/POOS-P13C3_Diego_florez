"""Prueba interactiva de la interfaz EcoTech sin conectar con una BD real.

Ejecutar desde la raíz del proyecto:
    python DOC_2/src/probar_interfaz_sin_db.py

Los datos se guardan solo en memoria y desaparecen al cerrar el programa.
Este archivo NO reemplaza main.py ni prueba las consultas SQL reales.
"""

from datetime import date
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = Path(__file__).resolve().parent
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

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

    def actualizar_datos_basicos(self, id_empleado, nombre, correo):
        if id_empleado not in self.datos:
            return False
        self.datos[id_empleado]["nombre"] = nombre
        self.datos[id_empleado]["correo"] = correo
        return True

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

    def obtener_por_id(self, id_departamento):
        dato = self.datos.get(id_departamento)
        return dato.copy() if dato else None

    def actualizar(self, id_departamento, departamento):
        if id_departamento not in self.datos:
            return False
        self.datos[id_departamento]["nombre"] = departamento.nombre
        return True

    def eliminar(self, id_departamento):
        return self.datos.pop(id_departamento, None) is not None

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

    def listar_por_empleado(self, id_empleado):
        return [self.datos[pid].copy() for pid, eid in sorted(self.asignaciones) if eid == id_empleado and pid in self.datos]

    def actualizar(self, id_proyecto, proyecto):
        if id_proyecto not in self.datos:
            return False
        self.datos[id_proyecto].update({"nombre": proyecto.nombre, "descripcion": proyecto.descripcion, "fecha_inicio": proyecto.fecha_inicio})
        return True

    def eliminar(self, id_proyecto):
        if id_proyecto not in self.datos:
            return False
        self.datos.pop(id_proyecto)
        self.asignaciones = {a for a in self.asignaciones if a[0] != id_proyecto}
        return True

    def asignar_empleado(self, id_proyecto, id_empleado):
        pareja = (id_proyecto, id_empleado)
        if pareja in self.asignaciones:
            return False
        self.asignaciones.add(pareja)
        return True

    def tiene_asignacion(self, id_proyecto, id_empleado):
        return (id_proyecto, id_empleado) in self.asignaciones

    def desasignar_empleado(self, id_proyecto, id_empleado):
        pareja = (id_proyecto, id_empleado)
        if pareja not in self.asignaciones:
            return False
        self.asignaciones.remove(pareja)
        return True


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

    def obtener_por_id(self, id_registro):
        registro = self.datos.get(id_registro)
        if registro is None:
            return None
        return {
            "id_registro": registro.id_registro,
            "id_empleado": registro.id_empleado,
            "id_proyecto": registro.id_proyecto,
            "fecha": registro.fecha,
            "horas_trabajadas": registro.horas_trabajadas,
            "descripcion_trabajo": registro.descripcion_trabajo,
        }

    def actualizar(self, id_registro, registro):
        if id_registro not in self.datos:
            return False
        registro.id_registro = id_registro
        registro.validar_registro()
        self.datos[id_registro] = registro
        return True

    def eliminar(self, id_registro):
        return self.datos.pop(id_registro, None) is not None

    def listar_por_empleado(self, id_empleado):
        resultado = []
        for registro in self.datos.values():
            if registro.id_empleado != id_empleado:
                continue
            empleado = self.empleado_dao.obtener_por_id(registro.id_empleado)
            proyecto = self.proyecto_dao.obtener_por_id(registro.id_proyecto)
            if empleado and proyecto:
                resultado.append({
                    "id_registro": registro.id_registro,
                    "fecha": registro.fecha,
                    "empleado": empleado["nombre"],
                    "proyecto": proyecto["nombre"],
                    "horas": registro.horas_trabajadas,
                    "descripcion": registro.descripcion_trabajo,
                })
        return resultado


class IndicadorDAOFalso:
    def __init__(self):
        self.datos = []

    def guardar(self, indicador):
        self.datos = [d for d in self.datos if not (d.fuente == indicador.fuente and d.codigo == indicador.codigo and d.fecha == indicador.fecha)]
        self.datos.append(indicador)
        return indicador

    def buscar_ultimo(self, codigo="dolar", fuente="mindicador.cl"):
        filtrados = [d for d in self.datos if d.codigo == codigo and d.fuente == fuente]
        return sorted(filtrados, key=lambda d: d.fecha, reverse=True)[0] if filtrados else None

    def listar(self, codigo="dolar"):
        return sorted([d for d in self.datos if d.codigo == codigo], key=lambda d: d.fecha, reverse=True)


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
        usuario={"id_usuario": 1, "empleado_id": 1, "nombre_usuario": "admin_prueba", "rol": "admin"},
        indicador_dao=IndicadorDAOFalso(),
    )
    app.iniciar()


if __name__ == "__main__":
    main()
