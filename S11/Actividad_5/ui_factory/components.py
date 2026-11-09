# Modulo ui_factory: Componentes abstractos y concretos para las familias Tkinter y PyQt5
from __future__ import annotations
from abc import ABC, abstractmethod


# ── Componentes Abstractos ───────────────────────────────────────────
class VentanaPrincipal(ABC):
    @abstractmethod
    def mostrar(self, titulo: str, ancho: int, alto: int) -> str:
        pass

    @abstractmethod
    def cerrar(self) -> str:
        pass


class MenuNavegacion(ABC):
    def __init__(self) -> None:
        self.items: list[tuple[str, str]] = []

    def agregar_item(self, etiqueta: str, accion: str) -> None:
        self.items.append((etiqueta, accion))

    @abstractmethod
    def renderizar(self) -> str:
        pass


class TablaResultados(ABC):
    def __init__(self) -> None:
        self.columnas: list[str] = []
        self.filas: list[list[str]] = []

    def configurar_columnas(self, columnas: list[str]) -> None:
        self.columnas = list(columnas)

    def agregar_fila(self, valores: list[str]) -> None:
        self.filas.append(list(valores))

    @abstractmethod
    def renderizar(self) -> str:
        pass


# ── Componentes Concretos: Familia Tkinter ──────────────────────────
class VentanaPrincipalTkinter(VentanaPrincipal):
    def mostrar(self, titulo: str, ancho: int, alto: int) -> str:
        return f"[Tkinter] tk.Tk(title='{titulo}', geometry='{ancho}x{alto}') desplegado."

    def cerrar(self) -> str:
        return "[Tkinter] root.destroy() ejecutado exitosamente."


class MenuNavegacionTkinter(MenuNavegacion):
    def renderizar(self) -> str:
        items_str = ", ".join(f"{lbl}->{cmd}" for lbl, cmd in self.items)
        return f"[Tkinter] tk.Menu renderizado con comandos: [{items_str}]"


class TablaResultadosTkinter(TablaResultados):
    def renderizar(self) -> str:
        cols_str = ", ".join(self.columnas)
        return f"[Tkinter] ttk.Treeview renderizado con columnas: [{cols_str}], registros: {len(self.filas)}"


# ── Componentes Concretos: Familia PyQt5 ────────────────────────────
class VentanaPrincipalPyQt(VentanaPrincipal):
    def mostrar(self, titulo: str, ancho: int, alto: int) -> str:
        return f"[PyQt5] QMainWindow(title='{titulo}', size=({ancho}, {alto})) desplegado."

    def cerrar(self) -> str:
        return "[PyQt5] QMainWindow.close() ejecutado exitosamente."


class MenuNavegacionPyQt(MenuNavegacion):
    def renderizar(self) -> str:
        items_str = ", ".join(f"QAction('{lbl}')->{cmd}" for lbl, cmd in self.items)
        return f"[PyQt5] QMenuBar renderizado con acciones: [{items_str}]"


class TablaResultadosPyQt(TablaResultados):
    def renderizar(self) -> str:
        cols_str = ", ".join(self.columnas)
        return f"[PyQt5] QTableWidget renderizado con cabeceras: [{cols_str}], filas: {len(self.filas)}"
