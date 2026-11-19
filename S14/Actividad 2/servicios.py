# servicios.py — Capa de Servicio (Lógica de Negocio)
from __future__ import annotations
import os

from estudiante import Estudiante
from repositorios import IRepositorioEstudiante
from estrategias import IEstrategiaPromedio


class ServicioEstudiante:
    """Coordina las operaciones de negocio entre el modelo, la estrategia y el repositorio."""

    def __init__(
        self,
        repositorio: IRepositorioEstudiante,
        estrategia: IEstrategiaPromedio
    ) -> None:
        self._repo = repositorio
        self._estrategia = estrategia

    @property
    def estrategia(self) -> IEstrategiaPromedio:
        return self._estrategia

    @estrategia.setter
    def estrategia(self, nueva_estrategia: IEstrategiaPromedio) -> None:
        self._estrategia = nueva_estrategia

    def registrar(self, estudiante: Estudiante) -> None:
        """Calcula el PPA mediante la estrategia inyectada y almacena al estudiante."""
        estudiante.ppa = self._estrategia.calcular(estudiante.notas)
        self._repo.guardar(estudiante)

    def eliminar(self, codigo: int) -> None:
        """Elimina al estudiante identificado por su código."""
        self._repo.eliminar(codigo)

    def listar(self) -> list[Estudiante]:
        """Devuelve el listado completo de estudiantes registrados."""
        return self._repo.listar()

    def buscar(self, codigo: int) -> Estudiante | None:
        """Recupera un estudiante por su código."""
        return self._repo.buscar(codigo)

    def exportar_excel(self, ruta_archivo: str) -> None:
        """Exporta la lista de estudiantes a Excel (.xlsx) con columna de Estado y formato condicional."""
        estudiantes = self.listar()

        if not ruta_archivo.lower().endswith((".xlsx", ".csv")):
            ruta_archivo += ".xlsx"

        try:
            import openpyxl
            from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
            from openpyxl.utils import get_column_letter

            wb = openpyxl.Workbook()
            ws = wb.active
            ws.title = "Estudiantes"

            # Título institucional que abarca las 5 columnas
            ws.merge_cells("A1:E1")
            title_cell = ws["A1"]
            title_cell.value = "SISTEMA ACADÉMICO UNAP — REPORTE DE ESTUDIANTES"
            title_cell.font = Font(name="Segoe UI", size=13, bold=True, color="1F497D")
            title_cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.row_dimensions[1].height = 28

            # Encabezados de tabla (5 columnas)
            headers = ["Código", "Nombre y Apellidos", "PPA", "Notas Registradas", "Estado"]
            ws.append([])  # Fila 2 vacía
            ws.append(headers)  # Fila 3 encabezados
            ws.row_dimensions[3].height = 22

            header_fill = PatternFill(start_color="1F497D", end_color="1F497D", fill_type="solid")
            header_font = Font(name="Segoe UI", size=11, bold=True, color="FFFFFF")
            thin_border = Border(
                left=Side(style="thin", color="CCCCCC"),
                right=Side(style="thin", color="CCCCCC"),
                top=Side(style="thin", color="CCCCCC"),
                bottom=Side(style="thin", color="CCCCCC")
            )

            for col_idx in range(1, len(headers) + 1):
                cell = ws.cell(row=3, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal="center", vertical="center")

            # Estilos de resaltado condicional
            fill_desaprobado = PatternFill(start_color="FFC7CE", end_color="FFC7CE", fill_type="solid")  # Rojo claro
            font_desaprobado = Font(name="Segoe UI", size=10, bold=True, color="9C0006")                # Rojo oscuro

            fill_aprobado = PatternFill(start_color="C6EFCE", end_color="C6EFCE", fill_type="solid")     # Verde claro
            font_aprobado = Font(name="Segoe UI", size=10, bold=True, color="006100")                   # Verde oscuro

            # Filas de datos
            for row_idx, e in enumerate(estudiantes, start=4):
                notas_str = ", ".join(f"{n:g}" for n in e.notas) if e.notas else "Sin notas"
                aprobado = e.ppa >= 10.5 if e.notas else False
                estado_str = "Aprobado" if aprobado else "Desaprobado"

                ws.append([
                    f"{e.codigo:04d}",
                    e.nombre,
                    round(e.ppa, 2),
                    notas_str,
                    estado_str
                ])

                ws.row_dimensions[row_idx].height = 20

                # Formato y bordes de las celdas
                for c in range(1, len(headers) + 1):
                    cell = ws.cell(row=row_idx, column=c)
                    cell.border = thin_border
                    cell.font = Font(name="Segoe UI", size=10)

                # Alineaciones
                ws.cell(row=row_idx, column=1).alignment = Alignment(horizontal="center", vertical="center")
                ws.cell(row=row_idx, column=3).alignment = Alignment(horizontal="right", vertical="center")
                ws.cell(row=row_idx, column=5).alignment = Alignment(horizontal="center", vertical="center")

                # Resaltado condicional en PPA y en la columna de Estado
                if not aprobado:
                    # Desaprobado: resaltado rojo
                    cell_estado = ws.cell(row=row_idx, column=5)
                    cell_estado.fill = fill_desaprobado
                    cell_estado.font = font_desaprobado

                    cell_ppa = ws.cell(row=row_idx, column=3)
                    cell_ppa.fill = fill_desaprobado
                    cell_ppa.font = font_desaprobado
                else:
                    # Aprobado: resaltado verde suave
                    cell_estado = ws.cell(row=row_idx, column=5)
                    cell_estado.fill = fill_aprobado
                    cell_estado.font = font_aprobado

            # Ajuste de anchos de columnas
            for col in ws.columns:
                col_letter = get_column_letter(col[0].column)
                max_len = max(len(str(cell.value or "")) for cell in col)
                ws.column_dimensions[col_letter].width = max(max_len + 4, 14)

            wb.save(ruta_archivo)

        except ImportError:
            # Fallback a CSV compatible con Excel
            import csv
            with open(ruta_archivo, "w", newline="", encoding="utf-8-sig") as f:
                writer = csv.writer(f, delimiter=";")
                writer.writerow(["Código", "Nombre y Apellidos", "PPA", "Notas Registradas", "Estado"])
                for e in estudiantes:
                    notas_str = ", ".join(f"{n:g}" for n in e.notas) if e.notas else "Sin notas"
                    estado_str = "Aprobado" if e.ppa >= 10.5 else "Desaprobado"
                    writer.writerow([f"{e.codigo:04d}", e.nombre, f"{e.ppa:.2f}", notas_str, estado_str])

    def importar_excel(self, ruta_archivo: str) -> int:
        """
        Importa estudiantes desde un archivo de Excel (.xlsx o .csv).
        Calcula su PPA y los registra en el repositorio.
        Retorna la cantidad de estudiantes importados con éxito.
        """
        if not os.path.exists(ruta_archivo):
            raise FileNotFoundError(f"El archivo no existe: {ruta_archivo}")

        filas_datos: list[list] = []

        if ruta_archivo.lower().endswith(".csv"):
            import csv
            try:
                with open(ruta_archivo, "r", encoding="utf-8-sig") as f:
                    sample = f.read(2048)
                    f.seek(0)
                    dialect = csv.Sniffer().sniff(sample, delimiters=";,\t")
                    reader = csv.reader(f, dialect)
                    filas_datos = list(reader)
            except Exception:
                with open(ruta_archivo, "r", encoding="latin-1") as f:
                    sample = f.read(2048)
                    f.seek(0)
                    delimitador = ";" if ";" in sample else ","
                    reader = csv.reader(f, delimiter=delimitador)
                    filas_datos = list(reader)
        else:
            import openpyxl
            wb = openpyxl.load_workbook(ruta_archivo, data_only=True)
            ws = wb.active
            for row in ws.iter_rows(values_only=True):
                if any(c is not None and str(c).strip() != "" for c in row):
                    filas_datos.append(list(row))

        if not filas_datos:
            return 0

        # Identificar la fila de encabezados y la correspondencia de columnas
        idx_cod = 0
        idx_nom = 1
        idx_notas = 3
        fila_inicio = 0

        for r_idx, fila in enumerate(filas_datos):
            fila_str = [str(c or "").strip().lower() for c in fila]
            if any("código" in c or "codigo" in c for c in fila_str):
                fila_inicio = r_idx + 1
                for c_idx, c_val in enumerate(fila_str):
                    if "código" in c_val or "codigo" in c_val:
                        idx_cod = c_idx
                    elif "nombre" in c_val:
                        idx_nom = c_idx
                    elif "nota" in c_val:
                        idx_notas = c_idx
                break

        def _parsear_notas(val) -> list[float]:
            if val is None:
                return []
            if isinstance(val, (int, float)):
                return [float(val)]
            s = str(val).strip().strip("[]()").replace(";", ",")
            if not s or s.lower() in ("sin notas", "none"):
                return []
            res = []
            for p in s.split(","):
                p_limpio = p.strip()
                if p_limpio:
                    try:
                        res.append(float(p_limpio))
                    except ValueError:
                        pass
            return res

        contador = 0
        for fila in filas_datos[fila_inicio:]:
            if len(fila) <= max(idx_cod, idx_nom):
                continue

            val_cod = fila[idx_cod]
            val_nom = fila[idx_nom]

            if val_cod is None or str(val_cod).strip() == "":
                continue

            # Extraer solo dígitos del código
            cod_str = "".join(filter(str.isdigit, str(val_cod)))
            if not cod_str:
                continue

            codigo = int(cod_str)
            nombre = str(val_nom).strip() if val_nom is not None else f"Estudiante {codigo}"
            if not nombre:
                nombre = f"Estudiante {codigo}"

            val_notas = fila[idx_notas] if idx_notas < len(fila) else None
            notas = _parsear_notas(val_notas)

            e = Estudiante(codigo=codigo, nombre=nombre, ppa=0.0, notas=notas)
            self.registrar(e)
            contador += 1

        return contador
