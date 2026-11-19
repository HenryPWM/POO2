# estrategias.py — Patrón Estrategia para cálculo de promedios
from __future__ import annotations
from abc import ABC, abstractmethod


class IEstrategiaPromedio(ABC):
    """Interfaz abstracta para las diferentes estrategias de cálculo de promedio."""

    @abstractmethod
    def calcular(self, notas: list[float]) -> float:
        """Calcula el promedio según el algoritmo concreto."""
        pass


class PromedioSimple(IEstrategiaPromedio):
    """Estrategia concreta: media aritmética estándar."""

    def calcular(self, notas: list[float]) -> float:
        if not notas:
            return 0.0
        return sum(notas) / len(notas)


class PromedioEliminaMenor(IEstrategiaPromedio):
    """Estrategia alternativa: descarta la nota más baja si hay más de una."""

    def calcular(self, notas: list[float]) -> float:
        if not notas:
            return 0.0
        if len(notas) == 1:
            return notas[0]
        notas_ordenadas = sorted(notas)[1:]
        return sum(notas_ordenadas) / len(notas_ordenadas)
