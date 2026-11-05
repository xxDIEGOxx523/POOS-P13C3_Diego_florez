"""Entidad de dominio para una observación económica validada."""
from datetime import date, datetime
import math


class Indicador:
    CODIGO_DOLAR = "dolar"
    UNIDAD_DOLAR = "CLP/USD"
    FUENTE_DOLAR = "mindicador.cl"

    def __init__(self, fecha, valor, verificado_en=None,
                 fuente=FUENTE_DOLAR, codigo=CODIGO_DOLAR, unidad=UNIDAD_DOLAR):
        self.fecha = self._validar_fecha(fecha)
        self.valor = self._validar_valor(valor)
        self.fuente = self._validar_texto(fuente, "fuente", 80)
        self.codigo = self._validar_texto(codigo, "código", 40)
        self.unidad = self._validar_texto(unidad, "unidad", 30)
        self.verificado_en = self._validar_verificacion(verificado_en)

    @staticmethod
    def _validar_texto(valor, campo, maximo):
        if not isinstance(valor, str):
            raise TypeError(f"El campo {campo} debe ser texto.")
        valor = valor.strip()
        if not valor or len(valor) > maximo:
            raise ValueError(f"El campo {campo} está vacío o supera {maximo} caracteres.")
        return valor

    @staticmethod
    def _validar_fecha(valor):
        if isinstance(valor, datetime):
            valor = valor.date().isoformat()
        elif isinstance(valor, date):
            valor = valor.isoformat()
        elif isinstance(valor, str):
            valor = valor.strip()
            try:
                # La API entrega fecha ISO con hora y zona; el historial identifica el día.
                valor = date.fromisoformat(valor[:10]).isoformat()
            except ValueError as error:
                raise ValueError("La fecha del indicador no tiene formato ISO válido.") from error
        else:
            raise TypeError("La fecha del indicador debe ser texto o una fecha.")
        return valor

    @staticmethod
    def _validar_valor(valor):
        if isinstance(valor, bool) or not isinstance(valor, (int, float)):
            raise TypeError("El valor del indicador debe ser numérico.")
        valor = float(valor)
        if not math.isfinite(valor) or valor <= 0:
            raise ValueError("El valor del indicador debe ser finito y mayor que cero.")
        return valor

    @staticmethod
    def _validar_verificacion(valor):
        if valor is None:
            return datetime.now().astimezone().isoformat(timespec="seconds")
        if isinstance(valor, datetime):
            return valor.isoformat(timespec="seconds")
        if isinstance(valor, str) and valor.strip() and len(valor) <= 40:
            return valor.strip()
        raise ValueError("La fecha de verificación no es válida.")
