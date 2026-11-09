#include <iostream>
#include <string>
#include <memory>
#include <utility>
#include <cassert>

// 1. Abstracción del Logger (DIP)
class ILogger {
public:
    virtual ~ILogger() = default;
    virtual void info(const std::string& modulo, const std::string& mensaje) = 0;
};

class LoggerConsolaMock : public ILogger {
public:
    void info(const std::string& modulo, const std::string& mensaje) override {
        std::cout << "[MOCK_LOG][" << modulo << "] " << mensaje << std::endl;
    }
};

// 2. Abstracción de la Conexión de Base de Datos (DIP)
class IConexionBD {
public:
    virtual ~IConexionBD() = default;
    virtual void ejecutar(const std::string& sql) = 0;
    virtual const std::string& url() const noexcept = 0;
};

// 3. Implementación concreta desacoplada (OCP, SRP, Thread-Safe)
class ConexionBD : public IConexionBD {
private:
    std::string url_;
    std::shared_ptr<ILogger> logger_;

    explicit ConexionBD(std::string url, std::shared_ptr<ILogger> logger)
        : url_(std::move(url)), logger_(std::move(logger)) {}

public:
    ConexionBD(const ConexionBD&) = delete;
    ConexionBD& operator=(const ConexionBD&) = delete;
    ConexionBD(ConexionBD&&) = delete;
    ConexionBD& operator=(ConexionBD&&) = delete;

    static ConexionBD& instancia(const std::string& url = "sqlite:///datos.db",
                                 std::shared_ptr<ILogger> logger = nullptr) {
        static ConexionBD inst(url, std::move(logger));
        return inst;
    }

    void ejecutar(const std::string& sql) override {
        if (logger_) {
            logger_->info("BD", "Ejecutando consulta: " + sql);
        }
        std::cout << "[ConexionBD][" << url_ << "] SQL ejecutado: " << sql << std::endl;
    }

    const std::string& url() const noexcept override {
        return url_;
    }
};

int main() {
    std::cout << "=== ACTIVIDAD 4: PRUEBA CONEXION BD MEJORADA ===" << std::endl;
    auto logger = std::make_shared<LoggerConsolaMock>();

    // Obtener la instancia Singleton inyectando el logger abstracto
    ConexionBD& db1 = ConexionBD::instancia("sqlite:///universidad.db", logger);
    ConexionBD& db2 = ConexionBD::instancia();

    assert(&db1 == &db2);
    std::cout << "[OK] Assert unicidad de instancia verificado: &db1 == &db2" << std::endl;

    db1.ejecutar("SELECT * FROM estudiantes WHERE promedio >= 14.0;");
    std::cout << "[OK] Consulta ejecutada con exito." << std::endl;
    return 0;
}
