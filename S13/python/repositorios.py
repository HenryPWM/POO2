from __future__ import annotations
from typing import Optional, Protocol
from estudiante import Estudiante
from repositorio_json import RepositorioJSON
from repositorio_csv import RepositorioCSV
from repositorio_sqlite import RepositorioSQLite


class IRepositorioEstudiante(Protocol):
    def guardar(self, e: Estudiante) -> None: ...
    def buscar(self, cod: int) -> Optional[Estudiante]: ...
    def listar(self) -> list[Estudiante]: ...


class RepositorioMemoria:
    def __init__(self) -> None:
        self._datos: dict[int, Estudiante] = {}

    def guardar(self, e: Estudiante) -> None:
        self._datos[e.codigo] = e

    def buscar(self, cod: int) -> Optional[Estudiante]:
        return self._datos.get(cod)

    def listar(self) -> list[Estudiante]:
        return list(self._datos.values())

    def eliminar(self, cod: int) -> None:
        self._datos.pop(cod, None)


class MockRepositorio:
    """Mock adicional solicitado en Actividad 3A: cuenta llamadas a guardar()."""

    def __init__(self) -> None:
        self._datos: dict[int, Estudiante] = {}
        self.llamadas_guardar: int = 0

    def guardar(self, e: Estudiante) -> None:
        self.llamadas_guardar += 1
        self._datos[e.codigo] = e

    def buscar(self, cod: int) -> Optional[Estudiante]:
        return self._datos.get(cod)

    def listar(self) -> list[Estudiante]:
        return list(self._datos.values())

    def eliminar(self, cod: int) -> None:
        self._datos.pop(cod, None)


__all__ = [
    "IRepositorioEstudiante",
    "RepositorioMemoria",
    "RepositorioJSON",
    "RepositorioCSV",
    "RepositorioSQLite",
    "MockRepositorio",
]
