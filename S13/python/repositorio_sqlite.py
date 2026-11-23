import json
import pathlib
import sqlite3
from typing import Optional
from estudiante import Estudiante

CREATE_SQL = (
    "CREATE TABLE IF NOT EXISTS estudiante("
    " codigo INTEGER PRIMARY KEY,"
    " nombre TEXT NOT NULL,"
    " ppa    REAL NOT NULL DEFAULT 0,"
    " notas  TEXT NOT NULL DEFAULT '[]')"
)


class RepositorioSQLite:
    def __init__(self, ruta: str) -> None:
        if ruta != ":memory:":
            pathlib.Path(ruta).parent.mkdir(parents=True, exist_ok=True)
        self._con = sqlite3.connect(ruta, check_same_thread=False)
        self._con.execute(CREATE_SQL)
        self._con.commit()

    def guardar(self, e: Estudiante) -> None:
        self._con.execute(
            "INSERT OR REPLACE INTO estudiante VALUES(?,?,?,?)",
            (e.codigo, e.nombre, e.ppa, json.dumps(e.notas)),
        )
        self._con.commit()

    def buscar(self, cod: int) -> Optional[Estudiante]:
        row = self._con.execute(
            "SELECT * FROM estudiante WHERE codigo=?", (cod,)
        ).fetchone()
        if row is None:
            return None
        return Estudiante(row[0], row[1], row[2], json.loads(row[3]))

    def listar(self) -> list[Estudiante]:
        rows = self._con.execute("SELECT * FROM estudiante").fetchall()
        return [Estudiante(r[0], r[1], r[2], json.loads(r[3])) for r in rows]

    def eliminar(self, cod: int) -> None:
        self._con.execute("DELETE FROM estudiante WHERE codigo=?", (cod,))
        self._con.commit()

    def cerrar(self) -> None:
        if hasattr(self, "_con") and self._con:
            self._con.close()

    def __del__(self) -> None:
        self.cerrar()

