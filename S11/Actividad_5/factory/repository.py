# Modulo factory: Abstraccion y productos concretos de repositorios de estudiantes
from __future__ import annotations
from abc import ABC, abstractmethod
import json
import os
import sqlite3


class RepositorioEstudiante(ABC):
    """Interfaz abstracta del producto Repositorio."""
    @abstractmethod
    def guardar(self, estudiante: dict) -> None:
        pass

    @abstractmethod
    def obtener(self, codigo: str) -> dict | None:
        pass

    @abstractmethod
    def listar_todos(self) -> list[dict]:
        pass

    @property
    @abstractmethod
    def tipo(self) -> str:
        pass


class RepositorioMemoria(RepositorioEstudiante):
    """Producto concreto: almacenamiento volatil en memoria RAM."""
    def __init__(self) -> None:
        self._almacen: dict[str, dict] = {}

    @property
    def tipo(self) -> str:
        return "memoria"

    def guardar(self, estudiante: dict) -> None:
        codigo = estudiante["codigo"]
        self._almacen[codigo] = dict(estudiante)

    def obtener(self, codigo: str) -> dict | None:
        item = self._almacen.get(codigo)
        return dict(item) if item else None

    def listar_todos(self) -> list[dict]:
        return [dict(e) for e in self._almacen.values()]


class RepositorioArchivo(RepositorioEstudiante):
    """Producto concreto: persistencia en archivo JSON plano."""
    def __init__(self, ruta_archivo: str = "estudiantes.json") -> None:
        self.ruta_archivo = ruta_archivo
        if not os.path.exists(self.ruta_archivo):
            self._escribir_datos({})

    @property
    def tipo(self) -> str:
        return "archivo"

    def _leer_datos(self) -> dict[str, dict]:
        if not os.path.exists(self.ruta_archivo):
            return {}
        try:
            with open(self.ruta_archivo, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return {}

    def _escribir_datos(self, datos: dict[str, dict]) -> None:
        with open(self.ruta_archivo, "w", encoding="utf-8") as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)

    def guardar(self, estudiante: dict) -> None:
        datos = self._leer_datos()
        datos[estudiante["codigo"]] = dict(estudiante)
        self._escribir_datos(datos)

    def obtener(self, codigo: str) -> dict | None:
        datos = self._leer_datos()
        return datos.get(codigo)

    def listar_todos(self) -> list[dict]:
        datos = self._leer_datos()
        return list(datos.values())


class RepositorioBD(RepositorioEstudiante):
    """Producto concreto: persistencia relacional en SQLite."""
    def __init__(self, ruta_db: str = "estudiantes.db") -> None:
        self.ruta_db = ruta_db
        self._inicializar_tabla()

    @property
    def tipo(self) -> str:
        return "bd"

    def _inicializar_tabla(self) -> None:
        with sqlite3.connect(self.ruta_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS estudiantes (
                    codigo TEXT PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    promedio REAL NOT NULL
                )
            """)
            conn.commit()

    def guardar(self, estudiante: dict) -> None:
        with sqlite3.connect(self.ruta_db) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO estudiantes (codigo, nombre, promedio)
                VALUES (?, ?, ?)
                ON CONFLICT(codigo) DO UPDATE SET
                    nombre = excluded.nombre,
                    promedio = excluded.promedio
            """, (estudiante["codigo"], estudiante["nombre"], float(estudiante["promedio"])))
            conn.commit()

    def obtener(self, codigo: str) -> dict | None:
        with sqlite3.connect(self.ruta_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, promedio FROM estudiantes WHERE codigo = ?", (codigo,))
            row = cursor.fetchone()
            if row:
                return {"codigo": row[0], "nombre": row[1], "promedio": row[2]}
            return None

    def listar_todos(self) -> list[dict]:
        with sqlite3.connect(self.ruta_db) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT codigo, nombre, promedio FROM estudiantes")
            rows = cursor.fetchall()
            return [{"codigo": r[0], "nombre": r[1], "promedio": r[2]} for r in rows]
