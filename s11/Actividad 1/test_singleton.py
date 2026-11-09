import unittest
import threading
from configuracion import ConfiguracionApp, SingletonMeta


class TestConfiguracionSingleton(unittest.TestCase):
    def test_misma_instancia_referencial(self):
        cfg1 = ConfiguracionApp()
        cfg2 = ConfiguracionApp()
        assert cfg1 is cfg2, "Las instancias de ConfiguracionApp no son identicas"
        self.assertIs(cfg1, cfg2)
        self.assertEqual(id(cfg1), id(cfg2))

    def test_parametros_cargados_desde_env(self):
        cfg = ConfiguracionApp()
        self.assertEqual(cfg.obtener("DB_URL"), "sqlite:///app_academica.db")
        self.assertEqual(cfg.obtener_entero("MAX_CONEXIONES"), 15)
        self.assertEqual(cfg.obtener("APP_ENV"), "development")
        self.assertEqual(cfg.obtener("NIVEL_LOG"), "INFO")

    def test_unicidad_en_hilos_concurrentes(self):
        instancias = []
        bloqueo = threading.Lock()

        def trabajador():
            inst = ConfiguracionApp()
            with bloqueo:
                instancias.append(inst)

        hilos = [threading.Thread(target=trabajador) for _ in range(10)]
        for h in hilos:
            h.start()
        for h in hilos:
            h.join()

        self.assertEqual(len(instancias), 10)
        primera = instancias[0]
        for inst in instancias:
            assert inst is primera, "Se creo una instancia diferente en un hilo concurrente"
            self.assertIs(inst, primera)
            self.assertEqual(id(inst), id(primera))

if __name__ == "__main__":
    unittest.main()
