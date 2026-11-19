# pyqt5_app.py — Actividad 2: Sistema Académico UNAP con PyQt5
import os
import sys

# Asegurar que encuentre los módulos tanto en la carpeta actual como en la carpeta superior
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))
for d in (BASE_DIR, PARENT_DIR):
    if d not in sys.path:
        sys.path.insert(0, d)

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QLineEdit,
    QLabel, QPushButton, QTableWidget,
    QTableWidgetItem, QMessageBox, QHeaderView,
    QFileDialog
)
from PyQt5.QtCore import pyqtSignal, QObject, Qt
from PyQt5.QtGui import QColor

from estudiante import Estudiante


# ── Modelo ───────────────────────────────────────────
class ModeloAcademico(QObject):
    """Envuelve ServicioEstudiante y emite señales Qt (Patrón Observer)."""

    estudiante_guardado = pyqtSignal(object)
    estudiante_eliminado = pyqtSignal(int)

    def __init__(self, svc) -> None:
        super().__init__()
        self._svc = svc

    def registrar(self, e: Estudiante) -> None:
        self._svc.registrar(e)
        self.estudiante_guardado.emit(e)

    def eliminar(self, cod: int) -> None:
        self._svc.eliminar(cod)
        self.estudiante_eliminado.emit(cod)

    def listar(self):
        return self._svc.listar()

    def buscar(self, cod: int):
        return self._svc.buscar(cod)

    def exportar_excel(self, ruta: str) -> None:
        self._svc.exportar_excel(ruta)

    def importar_excel(self, ruta: str) -> int:
        return self._svc.importar_excel(ruta)


# ── Vista ────────────────────────────────────────────
class VistaEstudiantes(QMainWindow):

    def __init__(self, modelo: ModeloAcademico) -> None:
        super().__init__()
        self._mod = modelo
        self.setWindowTitle("SIS206 — Sistema Académico UNAP (PyQt5)")
        self.resize(920, 560)
        self._construir_ui()

        # Observer: señal → slot
        self._mod.estudiante_guardado.connect(self._on_estudiante_guardado)
        self._mod.estudiante_eliminado.connect(self._on_estudiante_eliminado)
        self._recargar_tabla()

    def _construir_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)

        # Barra de entrada de datos
        hbox = QHBoxLayout()
        hbox.addWidget(QLabel("Código:"))
        self._ed_cod = QLineEdit()
        self._ed_cod.setMaximumWidth(80)
        hbox.addWidget(self._ed_cod)

        hbox.addWidget(QLabel("Nombre:"))
        self._ed_nom = QLineEdit()
        hbox.addWidget(self._ed_nom)

        hbox.addWidget(QLabel("Notas (,):"))
        self._ed_notas = QLineEdit()
        self._ed_notas.setMaximumWidth(140)
        hbox.addWidget(self._ed_notas)

        btn_reg = QPushButton("Registrar")
        btn_reg.clicked.connect(self._registrar)
        hbox.addWidget(btn_reg)

        btn_buscar = QPushButton("Buscar")
        btn_buscar.clicked.connect(self._buscar)
        hbox.addWidget(btn_buscar)

        btn_todos = QPushButton("Ver Todos")
        btn_todos.clicked.connect(self._recargar_tabla)
        hbox.addWidget(btn_todos)

        btn_elim = QPushButton("Eliminar")
        btn_elim.clicked.connect(self._eliminar)
        hbox.addWidget(btn_elim)

        btn_export = QPushButton("Exportar Excel")
        btn_export.clicked.connect(self._exportar_excel)
        hbox.addWidget(btn_export)

        btn_import = QPushButton("Importar Excel")
        btn_import.clicked.connect(self._importar_excel)
        hbox.addWidget(btn_import)

        layout.addLayout(hbox)

        # Tabla de estudiantes
        self._tbl = QTableWidget(0, 4)
        self._tbl.setHorizontalHeaderLabels(["Código", "Nombre", "PPA", "Notas"])
        self._tbl.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self._tbl.setEditTriggers(QTableWidget.NoEditTriggers)
        self._tbl.setSelectionBehavior(QTableWidget.SelectRows)
        self._tbl.setSelectionMode(QTableWidget.SingleSelection)
        self._tbl.cellClicked.connect(self._on_fila_seleccionada)
        layout.addWidget(self._tbl)

    def _registrar(self) -> None:
        try:
            raw_cod = self._ed_cod.text().strip()
            if not raw_cod:
                raise ValueError("Debe ingresar un código")
            cod = int(raw_cod)

            nom = self._ed_nom.text().strip()
            if not nom:
                raise ValueError("El nombre no puede estar vacío")

            raw_notas = self._ed_notas.text().strip()
            notas = [float(x) for x in raw_notas.split(",") if x.strip()] if raw_notas else []

            self._mod.registrar(Estudiante(cod, nom, 0.0, notas))
            self._limpiar_campos()
            QMessageBox.information(self, "Éxito", f"Estudiante [{cod:04d}] guardado correctamente.")
        except ValueError as ex:
            QMessageBox.critical(self, "Error", str(ex))

    def _buscar(self) -> None:
        raw_cod = self._ed_cod.text().strip()
        if not raw_cod:
            QMessageBox.warning(self, "Aviso", "Ingrese un código para buscar.")
            self._ed_cod.setFocus()
            return
        try:
            cod = int(raw_cod)
        except ValueError:
            QMessageBox.critical(self, "Error", "El código debe ser un número entero.")
            return

        e = self._mod.buscar(cod)
        if e:
            self._ed_nom.setText(e.nombre)
            self._ed_notas.setText(", ".join(f"{n:g}" for n in e.notas))
            self._mostrar_en_tabla([e])
        else:
            QMessageBox.warning(self, "No encontrado", f"No se encontró al estudiante con código {cod}.")

    def _eliminar(self) -> None:
        row = self._tbl.currentRow()
        cod = None

        if row >= 0:
            item = self._tbl.item(row, 0)
            if item:
                try:
                    cod = int(item.text())
                except ValueError:
                    pass
        else:
            raw_cod = self._ed_cod.text().strip()
            if raw_cod.isdigit():
                cod = int(raw_cod)

        if cod is None:
            QMessageBox.warning(self, "Aviso", "Seleccione un estudiante de la tabla o ingrese su código.")
            return

        resp = QMessageBox.question(
            self,
            "Confirmar eliminación",
            f"¿Está seguro de eliminar al estudiante [{cod:04d}]?",
            QMessageBox.Yes | QMessageBox.No
        )
        if resp == QMessageBox.Yes:
            self._mod.eliminar(cod)
            self._limpiar_campos()

    def _exportar_excel(self) -> None:
        estudiantes = self._mod.listar()
        if not estudiantes:
            QMessageBox.warning(self, "Aviso", "No hay estudiantes registrados para exportar.")
            return

        ruta, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar lista de estudiantes",
            "estudiantes_unap.xlsx",
            "Archivos de Excel (*.xlsx);;Archivos CSV (*.csv);;Todos los archivos (*.*)"
        )
        if not ruta:
            return

        try:
            self._mod.exportar_excel(ruta)
            QMessageBox.information(self, "Éxito", f"Lista exportada exitosamente en:\n{ruta}")
        except Exception as ex:
            QMessageBox.critical(self, "Error al exportar", f"No se pudo exportar:\n{ex}")

    def _importar_excel(self) -> None:
        """Permite seleccionar un archivo Excel (.xlsx o .csv) y cargar los estudiantes."""
        ruta, _ = QFileDialog.getOpenFileName(
            self,
            "Importar lista de estudiantes desde Excel",
            "",
            "Archivos de Excel (*.xlsx);;Archivos CSV (*.csv);;Todos los archivos (*.*)"
        )
        if not ruta:
            return

        try:
            total = self._mod.importar_excel(ruta)
            self._recargar_tabla()
            nombre_archivo = os.path.basename(ruta)
            QMessageBox.information(
                self,
                "Importación exitosa",
                f"Se importaron {total} estudiante(s) correctamente desde:\n{nombre_archivo}"
            )
        except Exception as ex:
            QMessageBox.critical(self, "Error al importar", f"Ocurrió un error al importar el archivo:\n{ex}")

    def _on_fila_seleccionada(self, row: int, col: int) -> None:
        item_cod = self._tbl.item(row, 0)
        if not item_cod:
            return
        try:
            cod = int(item_cod.text())
            e = self._mod.buscar(cod)
            if e:
                self._ed_cod.setText(str(e.codigo))
                self._ed_nom.setText(e.nombre)
                self._ed_notas.setText(", ".join(f"{n:g}" for n in e.notas))
        except Exception:
            pass

    def _limpiar_campos(self) -> None:
        self._ed_cod.clear()
        self._ed_nom.clear()
        self._ed_notas.clear()
        self._ed_cod.setFocus()

    def _on_estudiante_guardado(self, e) -> None:
        self._recargar_tabla()

    def _on_estudiante_eliminado(self, cod: int) -> None:
        self._recargar_tabla()

    def _mostrar_en_tabla(self, lista_estudiantes) -> None:
        self._tbl.setRowCount(0)
        for e in lista_estudiantes:
            r = self._tbl.rowCount()
            self._tbl.insertRow(r)

            it_cod = QTableWidgetItem(f"{e.codigo:04d}")
            it_cod.setTextAlignment(Qt.AlignCenter)
            self._tbl.setItem(r, 0, it_cod)

            self._tbl.setItem(r, 1, QTableWidgetItem(e.nombre))

            ppa_item = QTableWidgetItem(f"{e.ppa:.2f}")
            ppa_item.setTextAlignment(Qt.AlignCenter)
            if e.ppa < 10.5:
                ppa_item.setForeground(QColor("#C00000"))
            self._tbl.setItem(r, 2, ppa_item)

            notas_str = f"[{', '.join(f'{n:g}' for n in e.notas)}]" if e.notas else "[]"
            self._tbl.setItem(r, 3, QTableWidgetItem(notas_str))

    def _recargar_tabla(self) -> None:
        self._mostrar_en_tabla(self._mod.listar())


if __name__ == "__main__":
    from servicios import ServicioEstudiante
    from estrategias import PromedioSimple
    from repositorios import RepositorioJSON

    app = QApplication(sys.argv)

    ruta_datos = "datos.json"
    if not os.path.exists(ruta_datos) and os.path.exists(os.path.join("..", "datos.json")):
        ruta_datos = os.path.join("..", "datos.json")

    svc = ServicioEstudiante(RepositorioJSON(ruta_datos), PromedioSimple())
    mod = ModeloAcademico(svc)
    vista = VistaEstudiantes(mod)
    vista.show()
    sys.exit(app.exec_())
