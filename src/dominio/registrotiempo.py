"""Entidad de dominio para los registros de tiempo trabajado."""
from datetime import date, datetime
import math


class RegistroTiempo:
    def __init__(self, fecha, horas_trabajadas, descripcion_trabajo,
                 id_empleado, id_proyecto, id_registro=None):
        self.id_registro = id_registro
        self.fecha = fecha
        self.horas_trabajadas = horas_trabajadas
        self.descripcion_trabajo = descripcion_trabajo
        self.id_empleado = id_empleado
        self.id_proyecto = id_proyecto

    def registrar_tiempo(self):
        self.validar_registro()
        return True

    def validar_registro(self):
        if isinstance(self.fecha, datetime):
            self.fecha = self.fecha.date()
        if isinstance(self.fecha, str):
            try:
                self.fecha = date.fromisoformat(self.fecha[:10])
            except ValueError as error:
                raise ValueError("La fecha debe tener formato AAAA-MM-DD.") from error
        if not isinstance(self.fecha, date):
            raise ValueError("La fecha del registro no es válida.")
        if type(self.id_empleado) is not int or self.id_empleado <= 0:
            raise ValueError("El empleado del registro no es válido.")
        if type(self.id_proyecto) is not int or self.id_proyecto <= 0:
            raise ValueError("El proyecto del registro no es válido.")
        if isinstance(self.horas_trabajadas, bool):
            raise ValueError("Las horas trabajadas deben ser numéricas.")
        try:
            horas = float(self.horas_trabajadas)
        except (TypeError, ValueError) as error:
            raise ValueError("Las horas trabajadas deben ser numéricas.") from error
        if not math.isfinite(horas) or not 0 < horas <= 24:
            raise ValueError("Las horas trabajadas deben estar entre 0 y 24.")
        self.horas_trabajadas = horas
        if not isinstance(self.descripcion_trabajo, str) or not self.descripcion_trabajo.strip():
            raise ValueError("La descripción del trabajo no puede estar vacía.")
        if len(self.descripcion_trabajo.strip()) > 500:
            raise ValueError("La descripción no puede superar 500 caracteres.")
        self.descripcion_trabajo = self.descripcion_trabajo.strip()
        return True

    def actualizar_registro(self, fecha, horas_trabajadas, descripcion_trabajo):
        self.fecha = fecha
        self.horas_trabajadas = horas_trabajadas
        self.descripcion_trabajo = descripcion_trabajo
        self.validar_registro()
