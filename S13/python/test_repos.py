# test_repos.py — prueba de sustitucion LSP
#
# ¿ServicioEstudiante cambió alguna línea?
# RESPUESTA: NO. ServicioEstudiante no cambió absolutamente ninguna línea de código.
# Esto se debe a que cumple estrictamente con el Principio de Inversión de Dependencias (DIP):
# depende únicamente del contrato abstracto IRepositorioEstudiante y de IEstrategiaCalculo.
# Gracias al Principio de Sustitución de Liskov (LSP), cualquier implementación concreta
# (RepositorioMemoria, RepositorioJSON, RepositorioCSV, RepositorioSQLite o MockRepositorio)
# puede sustituir a la abstracción sin alterar la corrección del servicio ni requerir cambios en él.

import os
import pytest
from estudiante import Estudiante
from estrategias import PromedioSimple
from repositorios import (
    IRepositorioEstudiante,
    MockRepositorio,
    RepositorioCSV,
    RepositorioJSON,
    RepositorioMemoria,
    RepositorioSQLite,
)
from servicios import ServicioEstudiante


@pytest.mark.parametrize(
    "RepoClass,kwargs,cleanup",
    [
        (RepositorioMemoria, {}, None),
        (RepositorioJSON, {"ruta": "/tmp/t.json"}, "/tmp/t.json"),
        (RepositorioCSV, {"ruta": "/tmp/t.csv"}, "/tmp/t.csv"),
        (RepositorioSQLite, {"ruta": "/tmp/t.db"}, "/tmp/t.db"),
        (MockRepositorio, {}, None),  # ADICIONAL: 5° parámetro con MockRepositorio
    ],
)
def test_servicio_con_cualquier_repo(RepoClass, kwargs, cleanup):
    if cleanup and os.path.exists(cleanup):
        os.remove(cleanup)

    repo = RepoClass(**kwargs)
    svc = ServicioEstudiante(repo, PromedioSimple())
    e1 = Estudiante(1001, "Ana", 0.0, [15.0, 18.0, 14.0])
    e2 = Estudiante(1002, "Juan", 0.0, [10.0, 12.0, 14.0])
    svc.registrar(e1)
    svc.registrar(e2)

    assert svc.buscar(1001).nombre == "Ana"
    assert svc.buscar(1002) is not None
    assert len(repo.listar()) == 2

    # Verificación del mock adicional
    if isinstance(repo, MockRepositorio):
        assert repo.llamadas_guardar == 2

    if hasattr(repo, "cerrar"):
        repo.cerrar()

    if cleanup and os.path.exists(cleanup):
        os.remove(cleanup)
