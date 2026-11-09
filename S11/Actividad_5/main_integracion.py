import sys
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from singleton.logger import Logger, NivelLog
from singleton.config import ConfiguracionApp
from factory.repository_factory import FabricaRepositorioEntorno
from ui_factory.factories import SelectorUIFactory


class ServicioGestionAcademica:
    def __init__(self) -> None:
        self.logger = Logger()
        self.config = ConfiguracionApp()
        self.logger.info("ServicioGestionAcademica", "Iniciando servicio del sistema academico...")

        self.repositorio = FabricaRepositorioEntorno.obtener_repositorio()

        self.ui_factory = SelectorUIFactory.obtener_fabrica()

    def registrar_estudiante(self, codigo: str, nombre: str, promedio: float) -> None:
        estudiante = {"codigo": codigo, "nombre": nombre, "promedio": promedio}
        self.repositorio.guardar(estudiante)
        self.logger.info("ServicioGestionAcademica", f"Estudiante {nombre} ({codigo}) registrado en repo '{self.repositorio.tipo}'.")

    def desplegar_ui_reporte(self) -> None:
        estudiantes = self.repositorio.listar_todos()
        ventana = self.ui_factory.crear_ventana_principal()
        menu = self.ui_factory.crear_menu_navegacion()
        tabla = self.ui_factory.crear_tabla_resultados()

        menu.agregar_item("Nuevo Estudiante", "cmd_nuevo")
        menu.agregar_item("Exportar", "cmd_exportar")

        tabla.configurar_columnas(["Codigo", "Nombre", "Promedio"])
        for e in estudiantes:
            tabla.agregar_fila([e["codigo"], e["nombre"], f"{e['promedio']:.2f}"])

        print("\n--- Despliegue de Interfaz de Usuario ---")
        print(ventana.mostrar("Sistema de Gestion Academica", 900, 650))
        print(menu.renderizar())
        print(tabla.renderizar())


if __name__ == "__main__":
    servicio = ServicioGestionAcademica()
    servicio.registrar_estudiante("2023001", "Maria Quispe", 17.5)
    servicio.registrar_estudiante("2023002", "Juan Carlos Condori", 15.0)
    servicio.desplegar_ui_reporte()
