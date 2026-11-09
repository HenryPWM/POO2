from __future__ import annotations
import os
from threading import Lock
from typing import Any


class SingletonMeta(type):
   
    _instancias: dict[type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instancias:
                instancia = super().__call__(*args, **kwargs)
                cls._instancias[cls] = instancia
        return cls._instancias[cls]


class ConfiguracionApp(metaclass=SingletonMeta):
   
    def __init__(self, ruta_env: str = ".env") -> None:
        if getattr(self, "_inicializado", False):
            return

        self._parametros: dict[str, str] = {}
        self._ruta_env = ruta_env
        self._cargar_env(ruta_env)
        self._inicializado = True

    def _cargar_env(self, ruta_env: str) -> None:
        ruta_archivo = ruta_env
        if not os.path.exists(ruta_archivo):
            ruta_directorio = os.path.dirname(os.path.abspath(__file__))
            candidata = os.path.join(ruta_directorio, ruta_env)
            if os.path.exists(candidata):
                ruta_archivo = candidata

        if not os.path.exists(ruta_archivo):
            return

        with open(ruta_archivo, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith("#"):
                    continue
                if "=" in linea:
                    clave, valor = linea.split("=", 1)
                    self._parametros[clave.strip()] = valor.strip()

    def obtener(self, clave: str, valor_por_defecto: str | None = None) -> str | None:
        return self._parametros.get(clave, valor_por_defecto)

    def obtener_entero(self, clave: str, valor_por_defecto: int = 0) -> int:
        valor = self.obtener(clave)
        if valor is None:
            return valor_por_defecto
        try:
            return int(valor)
        except ValueError:
            return valor_por_defecto

    @property
    def parametros(self) -> dict[str, str]:
        return dict(self._parametros)

    def __getitem__(self, clave: str) -> str:
        return self._parametros[clave]

    def __contains__(self, clave: str) -> bool:
        return clave in self._parametros
