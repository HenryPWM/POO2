from __future__ import annotations
from abc import ABC, abstractmethod
import os

# Producto Abstracto 
class BoletaNotas(ABC):
    def __init__(self, estudiante: str) -> None:
        self.estudiante: str = estudiante
        self._notas: list[tuple[str, float]] = []

    def agregar_nota(self, curso: str, nota: float) -> None:
        self._notas.append((curso, float(nota)))

    @abstractmethod
    def generar(self) -> str:
        pass

    @property
    @abstractmethod
    def extension(self) -> str:
        pass

    @property
    @abstractmethod
    def formato(self) -> str:
        pass

    def calcular_promedio(self) -> float:
        if not self._notas:
            return 0.0
        return sum(nota for _, nota in self._notas) / len(self._notas)

    def condicion(self) -> str:
        return "Aprobado" if self.calcular_promedio() >= 10.5 else "Desaprobado"


# Productos Concretos
class BoletaTXT(BoletaNotas):
    @property
    def extension(self) -> str:
        return ".txt"

    @property
    def formato(self) -> str:
        return "Texto Plano"

    def generar(self) -> str:
        promedio = self.calcular_promedio()
        lineas = [
            "==================================================",
            "           BOLETA DE NOTAS ACADEMICA              ",
            "==================================================",
            f"Estudiante: {self.estudiante}",
            "--------------------------------------------------",
            f"{'Curso':<35} | {'Nota':>8}",
            "--------------------------------------------------"
        ]
        for curso, nota in self._notas:
            lineas.append(f"{curso:<35} | {nota:>8.2f}")
        lineas.extend([
            "--------------------------------------------------",
            f"Promedio Ponderado: {promedio:.2f}",
            f"Condición Final   : {self.condicion()}",
            "=================================================="
        ])
        return "\n".join(lineas)


class BoletaCSV(BoletaNotas):
    @property
    def extension(self) -> str:
        return ".csv"

    @property
    def formato(self) -> str:
        return "CSV"

    def generar(self) -> str:
        lineas = ["estudiante,curso,nota,promedio,condicion"]
        promedio = self.calcular_promedio()
        condicion = self.condicion()
        for curso, nota in self._notas:
            lineas.append(f'"{self.estudiante}","{curso}",{nota:.2f},{promedio:.2f},"{condicion}"')
        return "\n".join(lineas)


class BoletaHTML(BoletaNotas):
    @property
    def extension(self) -> str:
        return ".html"

    @property
    def formato(self) -> str:
        return "HTML"

    def generar(self) -> str:
        promedio = self.calcular_promedio()
        condicion = self.condicion()
        filas = "\n".join(
            f"        <tr><td>{curso}</td><td style='text-align:right;'>{nota:.2f}</td></tr>"
            for curso, nota in self._notas
        )
        return f"""<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Boleta de Notas - {self.estudiante}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 24px; }}
        table {{ border-collapse: collapse; width: 100%; max-width: 600px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; }}
        th {{ background-color: #2b5797; color: white; text-align: left; }}
        .resumen {{ margin-top: 16px; font-size: 1.1em; }}
    </style>
</head>
<body>
    <h2>Boleta de Notas Académica</h2>
    <p><strong>Estudiante:</strong> {self.estudiante}</p>
    <table>
        <thead>
            <tr><th>Curso</th><th style='text-align:right;'>Nota</th></tr>
        </thead>
        <tbody>
{filas}
        </tbody>
    </table>
    <div class="resumen">
        <p><strong>Promedio:</strong> {promedio:.2f}</p>
        <p><strong>Condición:</strong> {condicion}</p>
    </div>
</body>
</html>"""


# Creador Base (Factory Method + Template Method)
class GeneradorBoleta(ABC):
    @abstractmethod
    def crear_boleta(self, estudiante: str) -> BoletaNotas:
        pass

    def generar_y_enviar(self, estudiante: str, notas: dict[str, float], carpeta_destino: str = ".") -> str:
        boleta = self.crear_boleta(estudiante)
        for curso, nota in notas.items():
            boleta.agregar_nota(curso, nota)

        contenido = boleta.generar()
        nombre_sanitizado = estudiante.lower().replace(" ", "_")
        nombre_archivo = f"boleta_{nombre_sanitizado}{boleta.extension}"
        ruta_archivo = os.path.join(carpeta_destino, nombre_archivo)

        with open(ruta_archivo, "w", encoding="utf-8") as f:
            f.write(contenido)

        print(f"[{boleta.formato}] Boleta generada y enviada a: {ruta_archivo}")
        return ruta_archivo


# Creadores Concretos
class GeneradorBoletaTXT(GeneradorBoleta):
    def crear_boleta(self, estudiante: str) -> BoletaTXT:
        return BoletaTXT(estudiante)


class GeneradorBoletaCSV(GeneradorBoleta):
    def crear_boleta(self, estudiante: str) -> BoletaCSV:
        return BoletaCSV(estudiante)


class GeneradorBoletaHTML(GeneradorBoleta):
    def crear_boleta(self, estudiante: str) -> BoletaHTML:
        return BoletaHTML(estudiante)


# Registro de Fabricas 
class RegistroGeneradores:

    def __init__(self) -> None:
        self._registro: dict[str, type[GeneradorBoleta]] = {}

    def registrar(self, formato: str, creador_cls: type[GeneradorBoleta]) -> None:
        self._registro[formato.lower()] = creador_cls

    def crear(self, formato: str) -> GeneradorBoleta:
        fmt = formato.lower()
        if fmt not in self._registro:
            formatos_validos = ", ".join(self._registro.keys())
            raise ValueError(f"Formato no soportado: '{formato}'. Formatos disponibles: {formatos_validos}")
        return self._registro[fmt]()
