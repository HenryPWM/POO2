# Modulo factory: Creadores base y concretos aplicando Factory Method
from __future__ import annotations
from abc import ABC, abstractmethod
import sys
import os

# Asegurar importacion de modulos hermanos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from singleton.config import ConfiguracionApp
from singleton.logger import Logger
from .repository import (
    RepositorioEstudiante,
    RepositorioMemoria,
    RepositorioArchivo,
    RepositorioBD
)


class CreadorRepositorio(ABC):
    """
    Creador base que define el Factory Method crear_repositorio().
    """
    @abstractmethod
    def crear_repositorio(self) -> RepositorioEstudiante:
        """Factory Method: las subclases deciden que repositorio concreto instanciar."""
        pass

    def inicializar_con_datos_prueba(self, datos_iniciales: list[dict]) -> RepositorioEstudiante:
        """Template method: crea el repositorio y lo precarga con datos iniciales."""
        repo = self.crear_repositorio()
        logger = Logger()
        logger.info("FactoryMethod", f"Inicializando repositorio de tipo '{repo.tipo}'...")
        for est in datos_iniciales:
            repo.guardar(est)
        logger.info("FactoryMethod", f"Repositorio '{repo.tipo}' cargado con {len(datos_iniciales)} registros.")
        return repo


class CreadorRepositorioMemoria(CreadorRepositorio):
    def crear_repositorio(self) -> RepositorioMemoria:
        return RepositorioMemoria()


class CreadorRepositorioArchivo(CreadorRepositorio):
    def __init__(self, ruta_archivo: str = "estudiantes.json") -> None:
        self.ruta_archivo = ruta_archivo

    def crear_repositorio(self) -> RepositorioArchivo:
        return RepositorioArchivo(self.ruta_archivo)


class CreadorRepositorioBD(CreadorRepositorio):
    def __init__(self, ruta_db: str = "estudiantes.db") -> None:
        self.ruta_db = ruta_db

    def crear_repositorio(self) -> RepositorioBD:
        return RepositorioBD(self.ruta_db)


class FabricaRepositorioEntorno:
    """
    Resuelve e instancia el repositorio adecuado segun la configuracion del entorno (APP_ENV).
    Aplica DIP y OCP al desacoplar al cliente de la creacion concreta.
    """
    _creadores: dict[str, type[CreadorRepositorio]] = {
        "development": CreadorRepositorioMemoria,
        "testing": CreadorRepositorioArchivo,
        "production": CreadorRepositorioBD
    }

    @classmethod
    def registrar_creador(cls, entorno: str, creador_cls: type[CreadorRepositorio]) -> None:
        cls._creadores[entorno.lower()] = creador_cls

    @classmethod
    def obtener_repositorio(cls, entorno_forzado: str | None = None) -> RepositorioEstudiante:
        config = ConfiguracionApp()
        entorno = entorno_forzado if entorno_forzado else config.obtener("APP_ENV", "development")
        entorno = entorno.lower().strip()

        creador_cls = cls._creadores.get(entorno, CreadorRepositorioMemoria)
        creador = creador_cls()
        repo = creador.crear_repositorio()

        logger = Logger()
        logger.info("FabricaRepositorioEntorno", f"Repositorio resuelto para entorno '{entorno}': {type(repo).__name__}")
        return repo
