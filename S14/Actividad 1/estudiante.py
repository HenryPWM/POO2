# estudiante.py — Modelo de Dominio
from __future__ import annotations


class Estudiante:
    """Entidad del dominio que representa a un estudiante universitario."""

    def __init__(
        self,
        codigo: int,
        nombre: str,
        ppa: float = 0.0,
        notas: list[float] | None = None
    ) -> None:
        self.codigo = int(codigo)
        self.nombre = str(nombre).strip()
        self.ppa = float(ppa)
        self.notas = [float(n) for n in notas] if notas is not None else []

    def to_dict(self) -> dict:
        """Serializa el objeto a diccionario para persistencia."""
        return {
            "codigo": self.codigo,
            "nombre": self.nombre,
            "ppa": round(self.ppa, 2),
            "notas": self.notas
        }

    @classmethod
    def from_dict(cls, data: dict) -> Estudiante:
        """Reconstruye una instancia de Estudiante desde un diccionario."""
        return cls(
            codigo=int(data["codigo"]),
            nombre=str(data["nombre"]),
            ppa=float(data.get("ppa", 0.0)),
            notas=[float(x) for x in data.get("notas", [])]
        )

    def __repr__(self) -> str:
        return f"Estudiante(codigo={self.codigo}, nombre='{self.nombre}', ppa={self.ppa:.2f}, notas={self.notas})"
