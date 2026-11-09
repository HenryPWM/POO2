import unittest
import os
import json
from boletas import (
    RegistroGeneradores,
    GeneradorBoletaTXT,
    GeneradorBoletaCSV,
    GeneradorBoletaHTML,
    BoletaTXT,
    BoletaCSV,
    BoletaHTML
)
from main_boletas import ejecutar_desde_config


class TestFactoryMethodBoletas(unittest.TestCase):
    def setUp(self):
        self.registro = RegistroGeneradores()
        self.registro.registrar("txt", GeneradorBoletaTXT)
        self.registro.registrar("csv", GeneradorBoletaCSV)
        self.registro.registrar("html", GeneradorBoletaHTML)

    def test_creacion_tipo_correcto(self):
        gen_txt = self.registro.crear("txt")
        gen_csv = self.registro.crear("csv")
        gen_html = self.registro.crear("html")

        self.assertIsInstance(gen_txt, GeneradorBoletaTXT)
        self.assertIsInstance(gen_csv, GeneradorBoletaCSV)
        self.assertIsInstance(gen_html, GeneradorBoletaHTML)

        boleta_txt = gen_txt.crear_boleta("Estudiante A")
        boleta_csv = gen_csv.crear_boleta("Estudiante B")
        boleta_html = gen_html.crear_boleta("Estudiante C")

        self.assertIsInstance(boleta_txt, BoletaTXT)
        self.assertIsInstance(boleta_csv, BoletaCSV)
        self.assertIsInstance(boleta_html, BoletaHTML)

    def test_formato_no_registrado_lanza_excepcion(self):
        with self.assertRaises(ValueError):
            self.registro.crear("pdf")

    def test_iteracion_desde_json(self):
        archivos = ejecutar_desde_config()
        self.assertEqual(len(archivos), 3)
        for ruta in archivos:
            self.assertTrue(os.path.exists(ruta), f"El archivo {ruta} no fue creado")
            with open(ruta, "r", encoding="utf-8") as f:
                contenido = f.read()
                self.assertIn("Maria Elena Quispe Mamani", contenido)
                self.assertTrue(len(contenido) > 50)


if __name__ == "__main__":
    unittest.main()
