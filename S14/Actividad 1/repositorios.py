# repositorios.py — Patrón Repositorio para persistencia de datos
from __future__ import annotations
from abc import ABC, abstractmethod
import json
import os

from estudiante import Estudiante


class IRepositorioEstudiante(ABC):
    """Interfaz abstracta del repositorio de estudiantes."""

    @abstractmethod
    def guardar(self, estudiante: Estudiante) -> None:
        """Guarda o actualiza un estudiante en el almacenamiento."""
        pass

    @abstractmethod
    def eliminar(self, codigo: int) -> None:
        """Elimina a un estudiante según su código."""
        pass

    @abstractmethod
    def listar(self) -> list[Estudiante]:
        """Obtiene todos los estudiantes almacenados."""
        pass

    @abstractmethod
    def buscar(self, codigo: int) -> Estudiante | None:
        """Busca un estudiante por código."""
        pass


class RepositorioJSON(IRepositorioEstudiante):
    """Implementación concreta con persistencia en archivo JSON plano."""

    def __init__(self, ruta_archivo: str = "datos.json") -> None:
        self.ruta_archivo = ruta_archivo
        if not os.path.exists(self.ruta_archivo):
            self._guardar_datos({})

    def _leer_datos(self) -> dict[str, dict]:
        if not os.path.exists(self.ruta_archivo):
            return {}
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _guardar_datos(self, datos: dict[str, dict]) -> None:
        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def guardar(self, estudiante: Estudiante) -> None:
        datos = self._leer_datos()
        datos[str(estudiante.codigo)] = estudiante.to_dict()
        self._guardar_datos(datos)

    def eliminar(self, codigo: int) -> None:
        datos = self._leer_datos()
        clave = str(codigo)
        if clave in datos:
            del datos[clave]
            self._guardar_datos(datos)

    def listar(self) -> list[Estudiante]:
        datos = self._leer_datos()
        return [Estudiante.from_dict(item) for item in datos.values()]

    def buscar(self, codigo: int) -> Estudiante | None:
        datos = self._leer_datos()
        item = datos.get(str(codigo))
        return Estudiante.from_dict(item) if item else None
