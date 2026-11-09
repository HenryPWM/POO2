# Modulo singleton: Configuracion de la aplicacion cargada desde archivo .env
from __future__ import annotations
import os
from .logger import SingletonMeta


class ConfiguracionApp(metaclass=SingletonMeta):
    """
    Gestiona la configuracion global de la aplicacion garantizando una unica instancia.
    Carga los parametros desde un archivo de entorno .env.
    """
    def __init__(self, ruta_env: str = ".env") -> None:
        if getattr(self, "_inicializado", False):
            return

        self._parametros: dict[str, str] = {
            "APP_ENV": "development",
            "DB_URL": "sqlite:///sistema_academico.db",
            "STORAGE_PATH": "./datos_estudiantes.json",
            "NIVEL_LOG": "INFO",
            "UI_FRAMEWORK": "Tkinter"
        }
        self._cargar_env(ruta_env)
        self._inicializado = True

    def _cargar_env(self, ruta_env: str) -> None:
        # Resolver ruta relativa y buscar en el directorio del modulo si es necesario
        candidatos = [
            ruta_env,
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ruta_env),
            os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
        ]
        ruta_encontrada = None
        for c in candidatos:
            if os.path.exists(c) and os.path.isfile(c):
                ruta_encontrada = c
                break

        if not ruta_encontrada:
            return

        with open(ruta_encontrada, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                if "=" in linea:
                    k, v = linea.split("=", 1)
                    self._parametros[k.strip()] = v.strip()

    def obtener(self, clave: str, default: str | None = None) -> str:
        return self._parametros.get(clave, default if default is not None else "")

    def obtener_entero(self, clave: str, default: int = 0) -> int:
        valor = self.obtener(clave)
        try:
            return int(valor)
        except (ValueError, TypeError):
            return default

    def establecer(self, clave: str, valor: str) -> None:
        self._parametros[clave] = valor

    @property
    def entorno(self) -> str:
        return self.obtener("APP_ENV", "development").lower()
