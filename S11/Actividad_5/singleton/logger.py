# Modulo singleton: Logger centralizado thread-safe
from __future__ import annotations
import os
import datetime
from threading import Lock
from typing import Any
from enum import Enum


class SingletonMeta(type):
    """Metaclase que asegura una única instancia thread-safe."""
    _instancias: dict[type, Any] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args: Any, **kwargs: Any) -> Any:
        with cls._lock:
            if cls not in cls._instancias:
                instancia = super().__call__(*args, **kwargs)
                cls._instancias[cls] = instancia
        return cls._instancias[cls]


class NivelLog(Enum):
    DEBUG = 10
    INFO = 20
    WARN = 30
    ERROR = 40


class Logger(metaclass=SingletonMeta):
    """
    Logger Singleton del sistema académico.
    Permite registrar eventos en consola y archivo con timestamp y niveles de severidad.
    """
    def __init__(self, ruta_archivo: str = "sistema.log", nivel_minimo: NivelLog = NivelLog.INFO) -> None:
        if getattr(self, "_inicializado", False):
            return
        self.ruta_archivo = ruta_archivo
        self.nivel_minimo = nivel_minimo
        self._lock = Lock()
        self._inicializado = True

    def log(self, nivel: NivelLog, modulo: str, mensaje: str) -> str:
        if nivel.value < self.nivel_minimo.value:
            return ""

        ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entrada = f"[{ahora}] [{nivel.name:<5}] [{modulo}] {mensaje}"

        with self._lock:
            # Salida a archivo
            try:
                with open(self.ruta_archivo, "a", encoding="utf-8") as f:
                    f.write(entrada + "\n")
            except OSError:
                pass
            # Salida a consola
            print(entrada)

        return entrada

    def debug(self, modulo: str, mensaje: str) -> str:
        return self.log(NivelLog.DEBUG, modulo, mensaje)

    def info(self, modulo: str, mensaje: str) -> str:
        return self.log(NivelLog.INFO, modulo, mensaje)

    def warn(self, modulo: str, mensaje: str) -> str:
        return self.log(NivelLog.WARN, modulo, mensaje)

    def error(self, modulo: str, mensaje: str) -> str:
        return self.log(NivelLog.ERROR, modulo, mensaje)
