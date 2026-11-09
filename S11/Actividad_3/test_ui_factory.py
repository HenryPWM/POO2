import unittest
from ui_abstract_factory import (
    UIFactoryTkinter,
    UIFactoryPyQt5,
    VentanaPrincipalTkinter,
    VentanaPrincipalPyQt,
    MenuNavegacionTkinter,
    MenuNavegacionPyQt,
    TablaResultadosTkinter,
    TablaResultadosPyQt,
    FormularioBusqueda
)


class TestAbstractFactoryUI(unittest.TestCase):
    def setUp(self):
        self.factory_tk = UIFactoryTkinter()
        self.factory_qt = UIFactoryPyQt5()
        self.columnas = ["ID", "Estudiante", "Promedio", "Estado"]
        self.datos = [
            ["001", "Henry Juarez", "17.5", "Aprobado"],
            ["002", "Anghely Santander", "14.0", "Aprobado"]
        ]
        self.menu_opciones = [
            ("Buscar", "on_buscar"),
            ("Exportar", "on_exportar"),
            ("Salir", "on_salir")
        ]

    def test_creacion_productos_familia_tkinter(self):
        ventana = self.factory_tk.crear_ventana_principal()
        menu = self.factory_tk.crear_menu_navegacion()
        tabla = self.factory_tk.crear_tabla_resultados()

        self.assertIsInstance(ventana, VentanaPrincipalTkinter)
        self.assertIsInstance(menu, MenuNavegacionTkinter)
        self.assertIsInstance(tabla, TablaResultadosTkinter)
        self.assertEqual(self.factory_tk.framework, "Tkinter")

    def test_creacion_productos_familia_pyqt5(self):
        ventana = self.factory_qt.crear_ventana_principal()
        menu = self.factory_qt.crear_menu_navegacion()
        tabla = self.factory_qt.crear_tabla_resultados()

        self.assertIsInstance(ventana, VentanaPrincipalPyQt)
        self.assertIsInstance(menu, MenuNavegacionPyQt)
        self.assertIsInstance(tabla, TablaResultadosPyQt)
        self.assertEqual(self.factory_qt.framework, "PyQt5")

    def test_cliente_formulario_busqueda_independiente_de_familia(self):
        form_tk = FormularioBusqueda(self.factory_tk)
        res_tk = form_tk.construir("Búsqueda Estudiantes", self.menu_opciones, self.columnas, self.datos)
        self.assertEqual(res_tk["framework"], "Tkinter")
        self.assertIn("[Tkinter]", res_tk["ventana"])
        self.assertIn("[Tkinter]", res_tk["menu"])
        self.assertIn("[Tkinter]", res_tk["tabla"])

        form_qt = FormularioBusqueda(self.factory_qt)
        res_qt = form_qt.construir("Búsqueda Estudiantes", self.menu_opciones, self.columnas, self.datos)
        self.assertEqual(res_qt["framework"], "PyQt5")
        self.assertIn("[PyQt5]", res_qt["ventana"])
        self.assertIn("[PyQt5]", res_qt["menu"])
        self.assertIn("[PyQt5]", res_qt["tabla"])


if __name__ == "__main__":
    unittest.main()
