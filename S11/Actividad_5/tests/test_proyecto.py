# Entregable test Actividad 5: Pruebas unitarias completas con pytest/unittest y mocks
# Verifica la creacion del tipo correcto en Singletons, Factory Method y Abstract Factory.

import unittest
from unittest.mock import patch, MagicMock
import os
import sys

# Asegurar path de importacion del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from singleton.logger import Logger, NivelLog
from singleton.config import ConfiguracionApp
from factory.repository import (
    RepositorioEstudiante,
    RepositorioMemoria,
    RepositorioArchivo,
    RepositorioBD
)
from factory.repository_factory import (
    CreadorRepositorioMemoria,
    CreadorRepositorioArchivo,
    CreadorRepositorioBD,
    FabricaRepositorioEntorno
)
from ui_factory.components import (
    VentanaPrincipalTkinter,
    VentanaPrincipalPyQt,
    MenuNavegacionTkinter,
    MenuNavegacionPyQt,
    TablaResultadosTkinter,
    TablaResultadosPyQt
)
from ui_factory.factories import (
    UIFactoryTkinter,
    UIFactoryPyQt5,
    SelectorUIFactory
)


class TestSingleton(unittest.TestCase):
    def test_logger_unicidad_instancia(self):
        """Verifica que Logger mantenga una unica instancia global."""
        log1 = Logger()
        log2 = Logger()
        self.assertIs(log1, log2)
        self.assertEqual(id(log1), id(log2))

    def test_configuracion_unicidad_instancia(self):
        """Verifica que ConfiguracionApp mantenga una unica instancia global."""
        cfg1 = ConfiguracionApp()
        cfg2 = ConfiguracionApp()
        self.assertIs(cfg1, cfg2)
        self.assertEqual(id(cfg1), id(cfg2))


class TestFactoryMethodConMocks(unittest.TestCase):
    def test_creadores_concretos_producen_tipo_correcto(self):
        """Verifica que cada creador instancie el tipo exacto de repositorio."""
        creador_mem = CreadorRepositorioMemoria()
        creador_arch = CreadorRepositorioArchivo(ruta_archivo="test_estudiantes.json")
        creador_bd = CreadorRepositorioBD(ruta_db="test_estudiantes.db")

        repo_mem = creador_mem.crear_repositorio()
        repo_arch = creador_arch.crear_repositorio()
        repo_bd = creador_bd.crear_repositorio()

        self.assertIsInstance(repo_mem, RepositorioMemoria)
        self.assertIsInstance(repo_arch, RepositorioArchivo)
        self.assertIsInstance(repo_bd, RepositorioBD)
        self.assertEqual(repo_mem.tipo, "memoria")
        self.assertEqual(repo_arch.tipo, "archivo")
        self.assertEqual(repo_bd.tipo, "bd")

        # Limpieza de archivos temporales de prueba
        if os.path.exists("test_estudiantes.json"):
            os.remove("test_estudiantes.json")
        if os.path.exists("test_estudiantes.db"):
            os.remove("test_estudiantes.db")

    @patch.object(ConfiguracionApp, "obtener")
    def test_fabrica_entorno_resuelve_memoria_en_desarrollo(self, mock_obtener):
        """Simula entorno 'development' con mock y verifica creacion de RepositorioMemoria."""
        mock_obtener.return_value = "development"
        repo = FabricaRepositorioEntorno.obtener_repositorio()
        self.assertIsInstance(repo, RepositorioMemoria)
        mock_obtener.assert_called_with("APP_ENV", "development")

    @patch.object(ConfiguracionApp, "obtener")
    def test_fabrica_entorno_resuelve_archivo_en_testing(self, mock_obtener):
        """Simula entorno 'testing' con mock y verifica creacion de RepositorioArchivo."""
        mock_obtener.return_value = "testing"
        repo = FabricaRepositorioEntorno.obtener_repositorio()
        self.assertIsInstance(repo, RepositorioArchivo)
        # Limpieza
        if os.path.exists(repo.ruta_archivo):
            os.remove(repo.ruta_archivo)

    @patch.object(ConfiguracionApp, "obtener")
    def test_fabrica_entorno_resuelve_bd_en_produccion(self, mock_obtener):
        """Simula entorno 'production' con mock y verifica creacion de RepositorioBD."""
        mock_obtener.return_value = "production"
        repo = FabricaRepositorioEntorno.obtener_repositorio()
        self.assertIsInstance(repo, RepositorioBD)
        # Limpieza
        if os.path.exists(repo.ruta_db):
            os.remove(repo.ruta_db)

    def test_mock_interaccion_repositorio(self):
        """Usa MagicMock para verificar llamadas del cliente al contrato de repositorio."""
        mock_repo = MagicMock(spec=RepositorioEstudiante)
        mock_repo.guardar.return_value = None
        mock_repo.obtener.return_value = {"codigo": "2023001", "nombre": "Ana Perez", "promedio": 18.0}

        estudiante = {"codigo": "2023001", "nombre": "Ana Perez", "promedio": 18.0}
        mock_repo.guardar(estudiante)
        resultado = mock_repo.obtener("2023001")

        mock_repo.guardar.assert_called_once_with(estudiante)
        mock_repo.obtener.assert_called_once_with("2023001")
        self.assertEqual(resultado["nombre"], "Ana Perez")


class TestAbstractFactoryConMocks(unittest.TestCase):
    def test_fabrica_tkinter_crea_familia_completa(self):
        """Verifica que UIFactoryTkinter instancie los 3 componentes de su familia."""
        factory = UIFactoryTkinter()
        ventana = factory.crear_ventana_principal()
        menu = factory.crear_menu_navegacion()
        tabla = factory.crear_tabla_resultados()

        self.assertIsInstance(ventana, VentanaPrincipalTkinter)
        self.assertIsInstance(menu, MenuNavegacionTkinter)
        self.assertIsInstance(tabla, TablaResultadosTkinter)
        self.assertEqual(factory.framework, "Tkinter")

    def test_fabrica_pyqt5_crea_familia_completa(self):
        """Verifica que UIFactoryPyQt5 instancie los 3 componentes de su familia."""
        factory = UIFactoryPyQt5()
        ventana = factory.crear_ventana_principal()
        menu = factory.crear_menu_navegacion()
        tabla = factory.crear_tabla_resultados()

        self.assertIsInstance(ventana, VentanaPrincipalPyQt)
        self.assertIsInstance(menu, MenuNavegacionPyQt)
        self.assertIsInstance(tabla, TablaResultadosPyQt)
        self.assertEqual(factory.framework, "PyQt5")

    @patch.object(ConfiguracionApp, "obtener")
    def test_selector_ui_factory_con_mock(self, mock_obtener):
        """Usa mock para verificar seleccion de fabricas basadas en configuracion."""
        # Mock para PyQt5
        mock_obtener.return_value = "PyQt5"
        fabrica_qt = SelectorUIFactory.obtener_fabrica()
        self.assertIsInstance(fabrica_qt, UIFactoryPyQt5)

        # Mock para Tkinter
        mock_obtener.return_value = "Tkinter"
        fabrica_tk = SelectorUIFactory.obtener_fabrica()
        self.assertIsInstance(fabrica_tk, UIFactoryTkinter)


if __name__ == "__main__":
    unittest.main()
