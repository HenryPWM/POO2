import json
import os
from boletas import (
    RegistroGeneradores,
    GeneradorBoletaTXT,
    GeneradorBoletaCSV,
    GeneradorBoletaHTML
)


def ejecutar_desde_config(ruta_config: str = "config.json") -> list[str]:
    if not os.path.exists(ruta_config):
        ruta_directorio = os.path.dirname(os.path.abspath(__file__))
        ruta_config = os.path.join(ruta_directorio, ruta_config)

    with open(ruta_config, "r", encoding="utf-8") as f:
        config = json.load(f)

    estudiante = config["estudiante"]
    notas = config["notas"]
    formatos = config["formatos"]

    registro = RegistroGeneradores()
    registro.registrar("txt", GeneradorBoletaTXT)
    registro.registrar("csv", GeneradorBoletaCSV)
    registro.registrar("html", GeneradorBoletaHTML)

    archivos_generados = []
    carpeta_salida = os.path.dirname(ruta_config)

    print(f"=== Generando boletas para: {estudiante} ===")
    for fmt in formatos:
        creador = registro.crear(fmt)
        archivo = creador.generar_y_enviar(estudiante, notas, carpeta_destino=carpeta_salida)
        archivos_generados.append(archivo)

    return archivos_generados


if __name__ == "__main__":
    generados = ejecutar_desde_config()
    print("\nProceso finalizado. Archivos generados:")
    for a in generados:
        print(f" - {a}")
