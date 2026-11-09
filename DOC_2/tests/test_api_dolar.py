"""Pruebas unitarias de validación y control de sesión del servicio API."""
import unittest
from unittest.mock import Mock, patch
import requests

from servicios.api_dolar import deserializar_indicador, consultar_dolar


class TestIndicadorDolar(unittest.TestCase):
    def setUp(self):
        self.payload = {
            "codigo": "dolar",
            "nombre": "Dólar observado",
            "unidad_medida": "Pesos",
            "serie": [{"valor": 950.5, "fecha": "2026-11-09T00:00:00.000Z"}],
        }
        self.sesion = {
            "id": 1, "id_usuario": 1, "empleado_id": 1,
            "nombre_usuario": "prueba", "rol": "empleado"
        }

    def test_extrae_y_valida_datos(self):
        indicador = deserializar_indicador(self.payload)
        self.assertEqual(indicador.codigo, "dolar")
        self.assertEqual(indicador.valor, 950.5)
        self.assertEqual(indicador.fuente, "Mindicador")

    def test_rechaza_serie_vacia(self):
        datos = dict(self.payload, serie=[])
        with self.assertRaises(ValueError):
            deserializar_indicador(datos)

    def test_rechaza_valor_no_numerico(self):
        datos = dict(self.payload, serie=[{"valor": "950", "fecha": "2026-11-09"}])
        with self.assertRaises(ValueError):
            deserializar_indicador(datos)

    def test_exige_sesion_antes_de_consultar(self):
        with self.assertRaises(PermissionError):
            consultar_dolar(None)

    @patch("servicios.api_dolar.requests.get")
    def test_consulta_http_con_timeout_y_sesion(self, get):
        respuesta = Mock()
        respuesta.json.return_value = self.payload
        respuesta.raise_for_status.return_value = None
        get.return_value = respuesta
        indicador = consultar_dolar(self.sesion)
        self.assertEqual(indicador.valor, 950.5)
        self.assertEqual(get.call_args.kwargs["timeout"], (3, 7))
        self.assertIn("https://", get.call_args.args[0])

    @patch("servicios.api_dolar.requests.get")
    def test_controla_timeout(self, get):
        get.side_effect = requests.exceptions.Timeout()
        with self.assertRaises(ConnectionError):
            consultar_dolar(self.sesion)


if __name__ == "__main__":
    unittest.main()
