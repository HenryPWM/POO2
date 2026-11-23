# test_json_persistencia.py
import os
from estudiante import Estudiante
from repositorio_json import RepositorioJSON

RUTA = "/tmp/estudiantes_test.json"


def test_persistencia_entre_instancias() -> None:
    if os.path.exists(RUTA):
        os.remove(RUTA)

    # Primera instancia: guardar
    r1 = RepositorioJSON(RUTA)
    r1.guardar(Estudiante(1001, "Ana Quispe", 15.5, [14.0, 18.0, 14.5]))
    r1.guardar(Estudiante(1002, "Juan Mamani", 12.0, [10.0, 12.0, 14.0]))

    # Segunda instancia: verificar que los datos persisten
    r2 = RepositorioJSON(RUTA)
    ana = r2.buscar(1001)
    assert ana is not None, "Ana debe existir en r2"
    assert ana.nombre == "Ana Quispe"
    assert abs(ana.ppa - 15.5) < 0.01

    juan = r2.buscar(1002)
    assert juan is not None, "Juan debe existir en r2"
    assert len(r2.listar()) == 2

    # Ejecutar dos veces seguidas sin borrar el JSON: verificar cantidad de estudiantes
    r3 = RepositorioJSON(RUTA)
    r3.guardar(Estudiante(1001, "Ana Quispe", 15.5, [14.0, 18.0, 14.5]))
    assert len(r3.listar()) == 2, "La re-ejecución mantiene 2 estudiantes (no duplica)"

    # ADICIONAL: Implementar eliminar(cod) y verificar actualización persistente
    r3.eliminar(1001)
    r4 = RepositorioJSON(RUTA)
    assert r4.buscar(1001) is None, "El código 1001 debe haber sido eliminado del archivo"
    assert len(r4.listar()) == 1

    if os.path.exists(RUTA):
        os.remove(RUTA)  # limpiar


if __name__ == "__main__":
    test_persistencia_entre_instancias()
    print("RepositorioJSON: persistencia verificada ✓")
