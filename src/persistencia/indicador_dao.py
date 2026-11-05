"""Persistencia del historial de indicadores con UPSERT sin duplicados."""
from persistencia.conexion import abrir_conexion, obtener_motor
from dominio.indicador import Indicador
from persistencia.interfaces_dao import IIndicadorDAO


class IndicadorDAO(IIndicadorDAO):
    def guardar(self, indicador):
        if not isinstance(indicador, Indicador):
            raise TypeError("Solo se pueden guardar objetos Indicador validados.")
        valores = (
            indicador.fuente, indicador.codigo, indicador.fecha,
            indicador.valor, indicador.unidad, indicador.verificado_en,
        )
        if obtener_motor() == "sqlite":
            sql = """INSERT INTO indicador_api
                (fuente, codigo, fecha, valor, unidad, verificado_en)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (fuente, codigo, fecha) DO UPDATE SET
                    valor=excluded.valor,
                    unidad=excluded.unidad,
                    verificado_en=excluded.verificado_en"""
        else:
            sql = """INSERT INTO indicador_api
                (fuente, codigo, fecha, valor, unidad, verificado_en)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    valor=VALUES(valor), unidad=VALUES(unidad),
                    verificado_en=VALUES(verificado_en)"""

        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute(sql, valores)
            conexion.commit()
            return indicador
        except Exception:
            conexion.rollback()
            raise
        finally:
            cursor.close()
            conexion.close()

    def buscar_ultimo(self, codigo=Indicador.CODIGO_DOLAR,
                      fuente=Indicador.FUENTE_DOLAR):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""SELECT fecha, valor, verificado_en, fuente, codigo, unidad
                FROM indicador_api WHERE codigo=%s AND fuente=%s
                ORDER BY fecha DESC, verificado_en DESC LIMIT 1""", (codigo, fuente))
            fila = cursor.fetchone()
            return self._fila_a_indicador(fila) if fila else None
        finally:
            cursor.close()
            conexion.close()

    def listar(self, codigo=Indicador.CODIGO_DOLAR):
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            cursor.execute("""SELECT fecha, valor, verificado_en, fuente, codigo, unidad
                FROM indicador_api WHERE codigo=%s
                ORDER BY fecha DESC, verificado_en DESC""", (codigo,))
            return [self._fila_a_indicador(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conexion.close()

    @staticmethod
    def _fila_a_indicador(fila):
        return Indicador(
            fecha=fila[0], valor=float(fila[1]), verificado_en=fila[2],
            fuente=fila[3], codigo=fila[4], unidad=fila[5],
        )
