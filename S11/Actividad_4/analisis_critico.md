# Actividad 4: Integración GoF + SOLID — Análisis Crítico

## Código Analizado

```cpp
// ¿Qué patrón es esto? ¿Qué principios SOLID cumple?
class ConexionBD {
    static ConexionBD* _inst;
    std::string url_;
    ConexionBD() : url_("sqlite:///datos.db") {}
public:
    static ConexionBD* get() {
        if (!_inst) _inst = new ConexionBD();
        return _inst;
    }
    void ejecutar(const std::string& sql) {
        Logger::instancia().info("BD", "Ejecutando: " + sql);
        std::cout << "SQL: " << sql << std::endl;
    }
};
ConexionBD* ConexionBD::_inst = nullptr;
```

---

## Tabla de Análisis Crítico

| Pregunta | Tu respuesta |
| :--- | :--- |
| **¿Qué patrón GoF es?** | **Patrón Singleton** (creacional), implementado mediante instanciación perezosa clásica (*lazy initialization*) con puntero estático crudo (`raw pointer`). Adicionalmente, actúa como cliente acoplado de otro Singleton (`Logger::instancia()`). |
| **¿Es thread-safe? ¿Por qué?** | **NO es thread-safe.** La condición `if (!_inst)` seguida de `_inst = new ConexionBD();` es una sección crítica sin sincronización (`std::mutex` o primitivas atómicas). Si dos o más hilos ejecutan concurrentemente `get()` cuando `_inst == nullptr`, ambos hilos evaluarán la condición como verdadera y crearán instancias separadas en memoria, provocando una condición de carrera (*race condition*), fugas de memoria (*memory leaks*) y violando la garantía fundamental de unicidad del Singleton. |
| **¿Qué principio SOLID aplica?** | Aplica intencionalmente **SRP (Single Responsibility Principle)** en cuanto a centralizar la ejecución de comandos SQL hacia una base de datos específica, aunque esta responsabilidad se ve comprometida al mezclarse con el control de su propio ciclo de vida e instanciación global. |
| **¿Qué principio SOLID viola?** | 1. **DIP (Dependency Inversion Principle):** Viola flagrantemente DIP en dos niveles: (a) depende directamente de una clase concreta global (`Logger::instancia()`) en vez de una interfaz abstracta (`ILogger`), y (b) obliga a los módulos de alto nivel que usan la base de datos a acoplarse directamente a `ConexionBD::get()` en lugar de depender de una abstracción (`IConexionBD`).<br>2. **OCP (Open/Closed Principle):** Está rígidamente acoplado a una URL cableada (*hardcoded* `sqlite:///datos.db`) y no admite extensión a otros motores de base de datos sin modificar su código fuente.<br>3. **SRP (Single Responsibility Principle):** Viola SRP al asumir dos responsabilidades incompatibles: gestionar la lógica de base de datos y controlar su ciclo de vida/acceso global. |
| **¿Cómo lo mejorarías?** | 1. **Thread-safety idiomático (C++11/C++17):** Reemplazar el puntero crudo y la verificación no atómica por un **Meyers Singleton** (`static ConexionBD inst; return inst;`), garantizando inicialización única y segura según el estándar.<br>2. **Aplicar DIP (Inversión de Dependencias):** Definir una interfaz abstracta `IConexionBD` e inyectar el logger como abstracción (`std::shared_ptr<ILogger>`) a través del constructor.<br>3. **Eliminar copia y movimiento:** Declarar explícitamente `= delete` para el constructor de copia, operador de asignación, constructor y asignación por movimiento.<br>4. **Configurabilidad (OCP):** Parametrizar la cadena de conexión `url` para no dejarla cableada en el código. |

---

## Implementación Mejorada en C++17

La versión refactorizada cumple con los principios SOLID (DIP, OCP, SRP) y garantiza thread-safety según el estándar C++17:

```cpp
#include <iostream>
#include <string>
#include <memory>
#include <utility>

// 1. Abstracción del Logger (DIP)
class ILogger {
public:
    virtual ~ILogger() = default;
    virtual void info(const std::string& modulo, const std::string& mensaje) = 0;
};

// 2. Abstracción de la Conexión de Base de Datos (DIP e ISP)
class IConexionBD {
public:
    virtual ~IConexionBD() = default;
    virtual void ejecutar(const std::string& sql) = 0;
    virtual const std::string& url() const noexcept = 0;
};

// 3. Implementación concreta desacoplada (OCP, SRP)
class ConexionBD : public IConexionBD {
private:
    std::string url_;
    std::shared_ptr<ILogger> logger_;

    // Constructor privado: inyecta la abstracción ILogger y parametriza la URL
    explicit ConexionBD(std::string url, std::shared_ptr<ILogger> logger)
        : url_(std::move(url)), logger_(std::move(logger)) {}

public:
    // Eliminar copia y movimiento para garantizar la semántica de instancia controlada
    ConexionBD(const ConexionBD&) = delete;
    ConexionBD& operator=(const ConexionBD&) = delete;
    ConexionBD(ConexionBD&&) = delete;
    ConexionBD& operator=(ConexionBD&&) = delete;

    // Singleton Meyers Thread-Safe (C++11/C++17)
    static ConexionBD& instancia(const std::string& url = "sqlite:///datos.db",
                                 std::shared_ptr<ILogger> logger = nullptr) {
        static ConexionBD inst(url, std::move(logger));
        return inst;
    }

    void ejecutar(const std::string& sql) override {
        if (logger_) {
            logger_->info("BD", "Ejecutando: " + sql);
        }
        std::cout << "[ConexionBD][" << url_ << "] SQL: " << sql << std::endl;
    }

    const std::string& url() const noexcept override {
        return url_;
    }
};
```
