from __future__ import annotations
from typing import Protocol, Sequence


class IEstrategiaCalculo(Protocol):
    def calcular(self, notas: Sequence[float]) -> float: ...


class PromedioSimple:
    """Calcula el promedio aritmético simple de las notas."""

    def calcular(self, notas: Sequence[float]) -> float:
        if not notas:
            return 0.0
        return sum(notas) / len(notas)
