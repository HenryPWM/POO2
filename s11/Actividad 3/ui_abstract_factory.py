from __future__ import annotations
from abc import ABC, abstractmethod

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

class VentanaPrincipalTkinter(VentanaPrincipal):
    def mostrar(self, titulo: str, ancho: int, alto: int) -> str:
        return f"[Tkinter] tk.Tk() inicializado -> Title: '{titulo}', Geometry: '{ancho}x{alto}'"

    def cerrar(self) -> str:
        return "[Tkinter] root.destroy() ejecutado"


class MenuNavegacionTkinter(MenuNavegacion):
    def renderizar(self) -> str:
        opciones = ", ".join(f"'{lbl}' (command={cmd})" for lbl, cmd in self.items)
        return f"[Tkinter] tk.Menu construido con items: [{opciones}]"


class TablaResultadosTkinter(TablaResultados):
    def renderizar(self) -> str:
        cols_str = ", ".join(self.columnas)
        return f"[Tkinter] ttk.Treeview con {len(self.filas)} registros en columnas: [{cols_str}]"

class VentanaPrincipalPyQt(VentanaPrincipal):
    def mostrar(self, titulo: str, ancho: int, alto: int) -> str:
        return f"[PyQt5] QMainWindow() inicializado -> setWindowTitle('{titulo}'), resize({ancho}, {alto}), show()"

    def cerrar(self) -> str:
        return "[PyQt5] QMainWindow.close() ejecutado"


class MenuNavegacionPyQt(MenuNavegacion):
    def renderizar(self) -> str:
        opciones = ", ".join(f"QAction('{lbl}').triggered.connect({cmd})" for lbl, cmd in self.items)
        return f"[PyQt5] QMenuBar construido con acciones: [{opciones}]"


class TablaResultadosPyQt(TablaResultados):
    def renderizar(self) -> str:
        cols_str = ", ".join(self.columnas)
        return f"[PyQt5] QTableWidget({len(self.filas)}, {len(self.columnas)}) con cabeceras: [{cols_str}]"

class UIFactory(ABC):
    @abstractmethod
    def crear_ventana_principal(self) -> VentanaPrincipal:
        pass

    @abstractmethod
    def crear_menu_navegacion(self) -> MenuNavegacion:
        pass

    @abstractmethod
    def crear_tabla_resultados(self) -> TablaResultados:
        pass

    @property
    @abstractmethod
    def framework(self) -> str:
        pass


class UIFactoryTkinter(UIFactory):
    def crear_ventana_principal(self) -> VentanaPrincipal:
        return VentanaPrincipalTkinter()

    def crear_menu_navegacion(self) -> MenuNavegacion:
        return MenuNavegacionTkinter()

    def crear_tabla_resultados(self) -> TablaResultados:
        return TablaResultadosTkinter()

    @property
    def framework(self) -> str:
        return "Tkinter"


class UIFactoryPyQt5(UIFactory):
    def crear_ventana_principal(self) -> VentanaPrincipal:
        return VentanaPrincipalPyQt()

    def crear_menu_navegacion(self) -> MenuNavegacion:
        return MenuNavegacionPyQt()

    def crear_tabla_resultados(self) -> TablaResultados:
        return TablaResultadosPyQt()

    @property
    def framework(self) -> str:
        return "PyQt5"


class FormularioBusqueda:

    def __init__(self, factory: UIFactory) -> None:
        self._factory: UIFactory = factory
        self.ventana: VentanaPrincipal = factory.crear_ventana_principal()
        self.menu: MenuNavegacion = factory.crear_menu_navegacion()
        self.tabla: TablaResultados = factory.crear_tabla_resultados()

    def construir(
        self,
        titulo: str,
        opciones_menu: list[tuple[str, str]],
        columnas: list[str],
        datos: list[list[str]]
    ) -> dict[str, str]:
        for lbl, cmd in opciones_menu:
            self.menu.agregar_item(lbl, cmd)

        self.tabla.configurar_columnas(columnas)
        for fila in datos:
            self.tabla.agregar_fila(fila)

        resultado_ventana = self.ventana.mostrar(titulo, 800, 600)
        resultado_menu = self.menu.renderizar()
        resultado_tabla = self.tabla.renderizar()

        return {
            "framework": self._factory.framework,
            "ventana": resultado_ventana,
            "menu": resultado_menu,
            "tabla": resultado_tabla
        }
