"""Persistencia del indicador económico externo para MySQL y SQLite."""
from datetime import datetime, timezone
import math

from persistencia.conexion import abrir_conexion, obtener_motor


class ErrorPersistenciaIndicador(RuntimeError):
    """Fallo controlado al guardar o recuperar el historial de indicadores."""


class IndicadorDAO:
    """DAO con operaciones parametrizadas y actualización idempotente."""

    def guardar_o_actualizar(self, indicador):
        if not indicador or not getattr(indicador, "codigo", None):
            raise ValueError("Se requiere un indicador válido para persistir.")
        if not isinstance(indicador.fecha, datetime):
            raise ValueError("La fecha del indicador debe ser datetime.")
        if isinstance(indicador.valor, bool) or not isinstance(indicador.valor, (int, float)):
            raise ValueError("El valor del indicador debe ser numérico.")
        if not math.isfinite(float(indicador.valor)) or float(indicador.valor) <= 0:
            raise ValueError("El valor del indicador debe ser positivo y finito.")

        fecha = indicador.fecha.replace(tzinfo=None).isoformat(sep=" ", timespec="seconds")
        # MySQL DATETIME y SQLite TEXT reciben una fecha UTC sin tzinfo.
        verificado_en = datetime.now(timezone.utc).replace(tzinfo=None).isoformat(
            sep=" ", timespec="seconds"
        )
        conexion = abrir_conexion()
        cursor = conexion.cursor()
        try:
            valores = (
                indicador.fuente[:80], indicador.codigo[:30], fecha,
                float(indicador.valor), indicador.unidad[:30], verificado_en,
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
            cursor.execute(sql, valores)
            conexion.commit()
            return True
        except Exception as exc:
            conexion.rollback()
            raise ErrorPersistenciaIndicador(
                "No fue posible guardar el indicador en la base de datos."
            ) from exc
        finally:
            cursor.close()
            conexion.close()

    def obtener_ultimo(self, codigo="dolar"):
        codigo = _validar_codigo(codigo)
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT fuente, codigo, fecha, valor, unidad, verificado_en
                   FROM indicador_api WHERE codigo=%s
                   ORDER BY fecha DESC, verificado_en DESC LIMIT 1""",
                (codigo,),
            )
            return cursor.fetchone()
        except Exception as exc:
            raise ErrorPersistenciaIndicador(
                "No fue posible recuperar el último indicador guardado."
            ) from exc
        finally:
            cursor.close()
            conexion.close()

    def listar(self, codigo="dolar", limite=20):
        codigo = _validar_codigo(codigo)
        if type(limite) is not int or not 1 <= limite <= 100:
            raise ValueError("El límite del historial debe estar entre 1 y 100.")
        conexion = abrir_conexion()
        cursor = conexion.cursor(dictionary=True)
        try:
            cursor.execute(
                """SELECT fuente, codigo, fecha, valor, unidad, verificado_en
                   FROM indicador_api WHERE codigo=%s
                   ORDER BY fecha DESC, verificado_en DESC LIMIT %s""",
                (codigo, limite),
            )
            return cursor.fetchall()
        except Exception as exc:
            raise ErrorPersistenciaIndicador(
                "No fue posible consultar el historial de indicadores."
            ) from exc
        finally:
            cursor.close()
            conexion.close()


def _validar_codigo(codigo):
    """Lista permitida: no se concatena texto arbitrario en una consulta SQL."""
    if not isinstance(codigo, str) or codigo not in {"dolar"}:
        raise ValueError("El código de indicador solicitado no está permitido.")
    return codigo
