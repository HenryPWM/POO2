from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class Estudiante:
    codigo: int
    nombre: str
    ppa: float = 0.0
    notas: list[float] = field(default_factory=list)

    def __str__(self) -> str:
        return f"[{self.codigo}] {self.nombre} — PPA: {self.ppa:.1f}"
