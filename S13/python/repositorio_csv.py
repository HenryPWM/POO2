import csv
import json
import pathlib
from typing import Optional
from estudiante import Estudiante

CAMPOS = ["codigo", "nombre", "ppa", "notas"]


class RepositorioCSV:
    def __init__(self, ruta: str) -> None:
        self._ruta = pathlib.Path(ruta)
        self._datos: dict[int, Estudiante] = {}
        self._cargar()

    def _cargar(self) -> None:
        if not self._ruta.exists():
            return
        with self._ruta.open(newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                e = Estudiante(
                    int(row["codigo"]),
                    row["nombre"],
                    float(row["ppa"]),
                    json.loads(row["notas"]),
                )
                self._datos[e.codigo] = e

    def _persistir(self) -> None:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        with self._ruta.open("w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=CAMPOS)
            w.writeheader()
            for e in self._datos.values():
                w.writerow(
                    {
                        "codigo": e.codigo,
                        "nombre": e.nombre,
                        "ppa": e.ppa,
                        "notas": json.dumps(e.notas),
                    }
                )

    def guardar(self, e: Estudiante) -> None:
        self._datos[e.codigo] = e
        self._persistir()

    def buscar(self, cod: int) -> Optional[Estudiante]:
        return self._datos.get(cod)

    def listar(self) -> list[Estudiante]:
        return list(self._datos.values())

    def eliminar(self, cod: int) -> None:
        self._datos.pop(cod, None)
        self._persistir()
