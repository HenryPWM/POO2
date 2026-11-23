from __future__ import annotations
from typing import Optional
from estudiante import Estudiante
from estrategias import IEstrategiaCalculo
from repositorios import IRepositorioEstudiante


class ServicioEstudiante:
    def __init__(self, repo: IRepositorioEstudiante, calc: IEstrategiaCalculo) -> None:
        self._repo = repo
        self._calc = calc

    def set_estrategia(self, calc: IEstrategiaCalculo) -> None:
        self._calc = calc

    def registrar(self, e: Estudiante) -> None:
        e.ppa = self._calc.calcular(e.notas)
        self._repo.guardar(e)

    def buscar(self, cod: int) -> Optional[Estudiante]:
        return self._repo.buscar(cod)

    def listar(self) -> list[Estudiante]:
        return self._repo.listar()
