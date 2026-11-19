# app_tkinter.py — versión completa con búsqueda, listado, exportación e importación de Excel
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

from servicios import ServicioEstudiante
from estrategias import PromedioSimple
from repositorios import RepositorioJSON
from estudiante import Estudiante


class AppEstudiantes(tk.Tk):

    def __init__(self) -> None:
        super().__init__()
        self.title("SIS206 — Sistema Académico UNAP")
        self.geometry("920x560")
        self.minsize(750, 480)

        # Modelo (Servicio)
        self._svc = ServicioEstudiante(
            RepositorioJSON("datos.json"),
            PromedioSimple()
        )

        self._construir_ui()
        self._actualizar_lista()

    # ── UI ───────────────────────────────────
    def _construir_ui(self) -> None:
        # Barra superior de formulario y acciones
        frm_top = ttk.LabelFrame(self, text="Gestión de Estudiantes", padding=10)
        frm_top.pack(fill="x", padx=10, pady=6)

        # Fila 0: Entradas de datos
        ttk.Label(frm_top, text="Código:").grid(row=0, column=0, sticky="e", padx=(0, 2), pady=4)
        self._ent_cod = ttk.Entry(frm_top, width=10)
        self._ent_cod.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")

        ttk.Label(frm_top, text="Nombre:").grid(row=0, column=2, sticky="e", padx=(0, 2), pady=4)
        self._ent_nom = ttk.Entry(frm_top, width=28)
        self._ent_nom.grid(row=0, column=3, padx=(0, 10), pady=4, sticky="w")

        ttk.Label(frm_top, text="Notas (,):").grid(row=0, column=4, sticky="e", padx=(0, 2), pady=4)
        self._ent_notas = ttk.Entry(frm_top, width=18)
        self._ent_notas.grid(row=0, column=5, padx=(0, 10), pady=4, sticky="w")

        # Fila 1: Botonera de acciones
        frm_botones = ttk.Frame(frm_top)
        frm_botones.grid(row=1, column=0, columnspan=6, pady=(8, 2), sticky="w")

        ttk.Button(frm_botones, text="Registrar", command=self._registrar).pack(side="left", padx=3)
        ttk.Button(frm_botones, text="Buscar por Código", command=self._buscar).pack(side="left", padx=3)
        ttk.Button(frm_botones, text="Ver Todos", command=self._ver_todos).pack(side="left", padx=3)
        ttk.Button(frm_botones, text="Eliminar", command=self._eliminar).pack(side="left", padx=3)
        ttk.Button(frm_botones, text="Limpiar Campos", command=self._limpiar_campos).pack(side="left", padx=3)
        ttk.Button(frm_botones, text="Exportar a Excel", command=self._exportar_excel).pack(side="left", padx=3)
        ttk.Button(frm_botones, text="Importar de Excel", command=self._importar_excel).pack(side="left", padx=3)

        # Panel inferior: Lista de estudiantes
        frm_bot = ttk.LabelFrame(self, text="Lista de Estudiantes", padding=8)
        frm_bot.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        # Encabezado informativo de la lista
        lbl_info = ttk.Label(
            frm_bot,
            text="[Código]  Nombre y Apellidos                     PPA          Notas",
            font=("Courier New", 10, "bold")
        )
        lbl_info.pack(anchor="w", padx=2, pady=(0, 4))

        # Contenedor con Listbox y Scrollbar
        frm_lista = ttk.Frame(frm_bot)
        frm_lista.pack(fill="both", expand=True)

        self._lb = tk.Listbox(
            frm_lista,
            font=("Courier New", 10),
            selectmode=tk.SINGLE
        )
        sb = ttk.Scrollbar(frm_lista, orient="vertical", command=self._lb.yview)
        self._lb.configure(yscrollcommand=sb.set)

        self._lb.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

        # Evento al seleccionar un estudiante de la lista
        self._lb.bind("<<ListboxSelect>>", self._on_seleccionar)

        # Barra de estado inferior
        self._lbl_estado = ttk.Label(self, text="Listo", relief="sunken", anchor="w", padding=(6, 2))
        self._lbl_estado.pack(side="bottom", fill="x")

    # ── Handlers (Controlador) ───────────
    def _registrar(self) -> None:
        try:
            raw_cod = self._ent_cod.get().strip()
            if not raw_cod:
                raise ValueError("Debe ingresar un código")
            cod = int(raw_cod)

            nom = self._ent_nom.get().strip()
            if not nom:
                raise ValueError("El nombre no puede estar vacío")

            raw_notas = self._ent_notas.get().strip()
            notas = [float(x) for x in raw_notas.split(",") if x.strip()] if raw_notas else []

            e = Estudiante(cod, nom, 0.0, notas)
            self._svc.registrar(e)
            self._actualizar_lista()
            self._limpiar_campos()
            self._set_estado(f"Estudiante [{cod:04d}] registrado exitosamente.")
            messagebox.showinfo("Éxito", f"Estudiante [{cod:04d}] guardado correctamente.")
        except ValueError as ex:
            messagebox.showerror("Error", str(ex))

    def _buscar(self) -> None:
        """Busca un estudiante por su código y carga sus datos."""
        raw_cod = self._ent_cod.get().strip()
        if not raw_cod:
            messagebox.showwarning("Aviso", "Ingrese el código en el campo de texto para buscar.")
            self._ent_cod.focus_set()
            return

        try:
            cod = int(raw_cod)
        except ValueError:
            messagebox.showerror("Error", "El código debe ser un número entero.")
            return

        e = self._svc.buscar(cod)
        if e:
            # Rellenar campos con sus datos
            self._ent_nom.delete(0, "end")
            self._ent_nom.insert(0, e.nombre)
            self._ent_notas.delete(0, "end")
            self._ent_notas.insert(0, ", ".join(f"{n:g}" for n in e.notas))

            # Mostrar al estudiante en la lista
            self._mostrar_en_lista([e])
            self._set_estado(f"Estudiante encontrado: [{e.codigo:04d}] {e.nombre}")
        else:
            self._set_estado(f"No se encontró ningún estudiante con el código {cod}.")
            messagebox.showwarning("No encontrado", f"No se encontró ningún estudiante con el código {cod}.")

    def _ver_todos(self) -> None:
        """Restablece y muestra la lista completa de todos los estudiantes."""
        self._actualizar_lista()
        total = len(self._svc.listar())
        self._set_estado(f"Mostrando lista completa ({total} estudiante(s) registrado(s)).")

    def _eliminar(self) -> None:
        sel = self._lb.curselection()
        cod = None

        if sel:
            texto = self._lb.get(sel[0])
            try:
                cod = int(texto[1:5])
            except ValueError:
                pass
        else:
            raw_cod = self._ent_cod.get().strip()
            if raw_cod.isdigit():
                cod = int(raw_cod)

        if cod is None:
            messagebox.showwarning("Aviso", "Seleccione un estudiante de la lista o ingrese su código.")
            return

        confirmar = messagebox.askyesno(
            "Confirmar eliminación",
            f"¿Está seguro de eliminar al estudiante con código [{cod:04d}]?"
        )
        if confirmar:
            self._svc.eliminar(cod)
            self._actualizar_lista()
            self._limpiar_campos()
            self._set_estado(f"Estudiante [{cod:04d}] eliminado.")

    def _exportar_excel(self) -> None:
        """Exporta la lista de estudiantes a un archivo de Excel (.xlsx)."""
        estudiantes = self._svc.listar()
        if not estudiantes:
            messagebox.showwarning("Aviso", "No hay estudiantes registrados para exportar.")
            return

        ruta = filedialog.asksaveasfilename(
            title="Exportar lista de estudiantes",
            defaultextension=".xlsx",
            initialfile="estudiantes_unap.xlsx",
            filetypes=[
                ("Archivos de Excel (*.xlsx)", "*.xlsx"),
                ("Archivos CSV (*.csv)", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not ruta:
            return

        try:
            self._svc.exportar_excel(ruta)
            self._set_estado(f"Archivo exportado: {ruta}")
            messagebox.showinfo("Éxito", f"La lista de estudiantes fue exportada correctamente en:\n{ruta}")
        except Exception as ex:
            messagebox.showerror("Error al exportar", f"Ocurrió un error al exportar el archivo:\n{ex}")

    def _importar_excel(self) -> None:
        """Importa estudiantes desde un archivo de Excel (.xlsx o .csv)."""
        ruta = filedialog.askopenfilename(
            title="Importar lista de estudiantes",
            filetypes=[
                ("Archivos de Excel (*.xlsx)", "*.xlsx"),
                ("Archivos CSV (*.csv)", "*.csv"),
                ("Todos los archivos", "*.*")
            ]
        )
        if not ruta:
            return

        try:
            total = self._svc.importar_excel(ruta)
            self._actualizar_lista()
            nombre = os.path.basename(ruta)
            self._set_estado(f"Se importaron {total} estudiantes desde: {nombre}")
            messagebox.showinfo("Éxito", f"Se importaron {total} estudiante(s) correctamente desde:\n{nombre}")
        except Exception as ex:
            messagebox.showerror("Error al importar", f"Ocurrió un error al importar el archivo:\n{ex}")

    def _on_seleccionar(self, event) -> None:
        """Al seleccionar un estudiante de la lista, carga sus datos en los campos de texto."""
        sel = self._lb.curselection()
        if not sel:
            return
        texto = self._lb.get(sel[0])
        try:
            cod = int(texto[1:5])
            e = self._svc.buscar(cod)
            if e:
                self._ent_cod.delete(0, "end")
                self._ent_cod.insert(0, str(e.codigo))
                self._ent_nom.delete(0, "end")
                self._ent_nom.insert(0, e.nombre)
                self._ent_notas.delete(0, "end")
                self._ent_notas.insert(0, ", ".join(f"{n:g}" for n in e.notas))
                self._set_estado(f"Seleccionado: [{e.codigo:04d}] {e.nombre} | PPA: {e.ppa:.2f}")
        except Exception:
            pass

    def _mostrar_en_lista(self, estudiantes: list[Estudiante]) -> None:
        self._lb.delete(0, "end")
        for e in estudiantes:
            ppa_str = f"{e.ppa:.2f}" if e.notas else "sin notas"
            notas_str = f"[{', '.join(f'{n:g}' for n in e.notas)}]" if e.notas else "[]"
            self._lb.insert(
                "end",
                f"[{e.codigo:04d}]  {e.nombre:<32} PPA: {ppa_str:<8} {notas_str}"
            )
        if estudiantes:
            self._lb.selection_set(0)

    def _actualizar_lista(self) -> None:
        self._mostrar_en_lista(self._svc.listar())

    def _limpiar_campos(self) -> None:
        self._ent_cod.delete(0, "end")
        self._ent_nom.delete(0, "end")
        self._ent_notas.delete(0, "end")
        self._ent_cod.focus_set()

    def _set_estado(self, mensaje: str) -> None:
        self._lbl_estado.config(text=mensaje)


if __name__ == "__main__":
    AppEstudiantes().mainloop()
