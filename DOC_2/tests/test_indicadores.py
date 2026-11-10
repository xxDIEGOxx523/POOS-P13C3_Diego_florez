"""Pruebas del flujo API -> persistencia -> historial/respaldo."""
import os
import tempfile
import unittest
from datetime import datetime
from unittest.mock import Mock, patch

from servicios.api_dolar import IndicadorDolar
from servicios.indicadores import (
    consultar_y_conservar_dolar,
    obtener_historial_dolar,
    IndicadorNoDisponible,
)
from persistencia.indicador_dao import IndicadorDAO, ErrorPersistenciaIndicador
from persistencia.crear_db import crear_base_y_tablas


SESION = {
    "id": 1,
    "id_usuario": 1,
    "empleado_id": 1,
    "nombre_usuario": "prueba",
    "rol": "empleado",
}


class TestServicioIndicadores(unittest.TestCase):
    def setUp(self):
        self.indicador = IndicadorDolar(
            codigo="dolar",
            nombre="Dólar observado",
            unidad="Pesos",
            valor=950.5,
            fecha=datetime(2026, 11, 9),
            fuente="Mindicador",
        )

    @patch("servicios.indicadores.consultar_dolar")
    def test_consulta_y_guarda_indicador(self, consultar):
        consultar.return_value = self.indicador
        dao = Mock()
        resultado = consultar_y_conservar_dolar(SESION, dao=dao)
        dao.guardar_o_actualizar.assert_called_once_with(self.indicador)
        self.assertEqual(resultado.origen, "API (Mindicador)")
        self.assertTrue(resultado.guardado)

    @patch("servicios.indicadores.consultar_dolar", side_effect=ConnectionError("offline"))
    def test_usa_respaldo_local_si_falla_api(self, consultar):
        dao = Mock()
        dao.obtener_ultimo.return_value = {
            "fuente": "Mindicador", "codigo": "dolar",
            "fecha": "2026-11-08 00:00:00", "valor": 945.0,
            "unidad": "Pesos", "verificado_en": "2026-11-08 09:00:00",
        }
        resultado = consultar_y_conservar_dolar(SESION, dao=dao)
        self.assertEqual(resultado.origen, "BD local (respaldo)")
        self.assertFalse(resultado.guardado)
        self.assertEqual(resultado.indicador.valor, 945.0)
        self.assertIn("no corresponde a una consulta actualizada", resultado.mensaje)

    @patch("servicios.indicadores.consultar_dolar", side_effect=ConnectionError("offline"))
    def test_falla_controladamente_si_no_hay_respaldo(self, consultar):
        dao = Mock()
        dao.obtener_ultimo.return_value = None
        with self.assertRaises(IndicadorNoDisponible):
            consultar_y_conservar_dolar(SESION, dao=dao)

    def test_exige_sesion_para_historial(self):
        with self.assertRaises(PermissionError):
            obtener_historial_dolar(None, dao=Mock())


class TestIndicadorDAO_SQLite(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.tmp.name, "pruebas.db")
        self.anterior_backend = os.environ.get("DB_BACKEND")
        self.anterior_path = os.environ.get("SQLITE_PATH")
        os.environ["DB_BACKEND"] = "sqlite"
        os.environ["SQLITE_PATH"] = self.db_path
        crear_base_y_tablas()
        self.dao = IndicadorDAO()

    def tearDown(self):
        if self.anterior_backend is None:
            os.environ.pop("DB_BACKEND", None)
        else:
            os.environ["DB_BACKEND"] = self.anterior_backend
        if self.anterior_path is None:
            os.environ.pop("SQLITE_PATH", None)
        else:
            os.environ["SQLITE_PATH"] = self.anterior_path
        self.tmp.cleanup()

    def test_guarda_actualiza_sin_duplicar_y_lista_historial(self):
        primero = IndicadorDolar("dolar", "Dólar", "Pesos", 950.0,
                                 datetime(2026, 11, 9), "Mindicador")
        actualizado = IndicadorDolar("dolar", "Dólar", "Pesos", 951.5,
                                     datetime(2026, 11, 9), "Mindicador")
        self.dao.guardar_o_actualizar(primero)
        self.dao.guardar_o_actualizar(actualizado)
        historial = self.dao.listar("dolar", 20)
        self.assertEqual(len(historial), 1)
        self.assertAlmostEqual(float(historial[0]["valor"]), 951.5)

    def test_limite_historial_se_valida(self):
        with self.assertRaises(ValueError):
            self.dao.listar("dolar", 1000)


if __name__ == "__main__":
    unittest.main()
