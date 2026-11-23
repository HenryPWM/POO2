import json
import pathlib
from dataclasses import asdict
from typing import Optional
from estudiante import Estudiante


class RepositorioJSON:
    def __init__(self, ruta: str) -> None:
        self._ruta = pathlib.Path(ruta)
        self._datos: dict[int, Estudiante] = {}
        self._cargar()

    def _cargar(self) -> None:
        if not self._ruta.exists():
            return
        with self._ruta.open(encoding="utf-8") as f:
            for item in json.load(f):
                e = Estudiante(**item)
                self._datos[e.codigo] = e

    def _persistir(self) -> None:
        self._ruta.parent.mkdir(parents=True, exist_ok=True)
        lista = [asdict(e) for e in self._datos.values()]
        with self._ruta.open("w", encoding="utf-8") as f:
            json.dump(lista, f, indent=2, ensure_ascii=False)

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
