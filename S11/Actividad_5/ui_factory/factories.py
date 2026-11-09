# Modulo ui_factory: Fabricas abstractas y familias de componentes UI
from __future__ import annotations
from abc import ABC, abstractmethod
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from singleton.config import ConfiguracionApp
from singleton.logger import Logger
from .components import (
    VentanaPrincipal,
    MenuNavegacion,
    TablaResultados,
    VentanaPrincipalTkinter,
    MenuNavegacionTkinter,
    TablaResultadosTkinter,
    VentanaPrincipalPyQt,
    MenuNavegacionPyQt,
    TablaResultadosPyQt
)


class UIFactory(ABC):
    """
    Abstract Factory: declara los metodos para crear familias de componentes
    de interfaz de usuario relacionados.
    """
    @abstractmethod
    def crear_ventana_principal(self) -> VentanaPrincipal:
        pass

    @abstractmethod
    def crear_menu_navegacion(self) -> MenuNavegacion:
        pass

    @abstractmethod
    def crear_tabla_resultados(self) -> TablaResultados:
        pass

    @property
    @abstractmethod
    def framework(self) -> str:
        pass


class UIFactoryTkinter(UIFactory):
    def crear_ventana_principal(self) -> VentanaPrincipal:
        return VentanaPrincipalTkinter()

    def crear_menu_navegacion(self) -> MenuNavegacion:
        return MenuNavegacionTkinter()

    def crear_tabla_resultados(self) -> TablaResultados:
        return TablaResultadosTkinter()

    @property
    def framework(self) -> str:
        return "Tkinter"


class UIFactoryPyQt5(UIFactory):
    def crear_ventana_principal(self) -> VentanaPrincipal:
        return VentanaPrincipalPyQt()

    def crear_menu_navegacion(self) -> MenuNavegacion:
        return MenuNavegacionPyQt()

    def crear_tabla_resultados(self) -> TablaResultados:
        return TablaResultadosPyQt()

    @property
    def framework(self) -> str:
        return "PyQt5"


class SelectorUIFactory:
    """
    Permite obtener la fabrica UI correspondiente de acuerdo al framework configurado.
    """
    @staticmethod
    def obtener_fabrica(framework_forzado: str | None = None) -> UIFactory:
        config = ConfiguracionApp()
        fw = framework_forzado if framework_forzado else config.obtener("UI_FRAMEWORK", "Tkinter")
        fw = fw.lower().strip()

        logger = Logger()
        if fw in ("pyqt", "pyqt5", "qt"):
            logger.info("SelectorUIFactory", "Instanciando fabrica de UI: UIFactoryPyQt5")
            return UIFactoryPyQt5()

        logger.info("SelectorUIFactory", "Instanciando fabrica de UI: UIFactoryTkinter")
        return UIFactoryTkinter()
