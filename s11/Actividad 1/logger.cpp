#include <iostream>
#include <fstream>
#include <string>
#include <mutex>
#include <chrono>
#include <iomanip>
#include <sstream>
#include <thread>
#include <vector>
#include <cassert>

enum class NivelLog {
    DEBUG,
    INFO,
    WARN,
    ERROR
};

class Logger {
private:
    std::ofstream archivo_;
    std::mutex mtx_;
    NivelLog nivelMinimo_;

    explicit Logger(const std::string& ruta = "app.log", NivelLog nivelMinimo = NivelLog::DEBUG)
        : nivelMinimo_(nivelMinimo) {
        archivo_.open(ruta, std::ios::app);
        if (!archivo_.is_open()) {
            throw std::runtime_error("No se pudo abrir el archivo de log: " + ruta);
        }
    }

    ~Logger() {
        if (archivo_.is_open()) {
            archivo_.close();
        }
    }

    Logger(const Logger&) = delete;
    Logger& operator=(const Logger&) = delete;

    Logger(Logger&&) = delete;
    Logger& operator=(Logger&&) = delete;

    std::string timestamp() const {
        auto now = std::chrono::system_clock::now();
        auto t = std::chrono::system_clock::to_time_t(now);
        std::tm tmBuffer{};
#if defined(_WIN32) || defined(_WIN64)
        localtime_s(&tmBuffer, &t);
#else
        localtime_r(&t, &tmBuffer);
#endif
        std::ostringstream oss;
        oss << std::put_time(&tmBuffer, "%Y-%m-%d %H:%M:%S");
        return oss.str();
    }

    static std::string nivelStr(NivelLog nivel) {
        switch (nivel) {
            case NivelLog::DEBUG: return "DEBUG";
            case NivelLog::INFO:  return "INFO ";
            case NivelLog::WARN:  return "WARN ";
            case NivelLog::ERROR: return "ERROR";
            default:              return "UNKNOWN";
        }
    }

public:
    static Logger& instancia(const std::string& ruta = "app.log") {
        static Logger inst(ruta);
        return inst;
    }

    void setNivelMinimo(NivelLog nivel) {
        std::lock_guard<std::mutex> lock(mtx_);
        nivelMinimo_ = nivel;
    }

    void log(NivelLog nivel, const std::string& modulo, const std::string& mensaje) {
        if (nivel < nivelMinimo_) return;

        std::lock_guard<std::mutex> lock(mtx_);
        std::string entrada = "[" + timestamp() + "] [" + nivelStr(nivel) + "] [" + modulo + "] " + mensaje;
        
        if (archivo_.is_open()) {
            archivo_ << entrada << "\n";
            archivo_.flush();
        }
        std::cout << entrada << "\n";
    }

    void debug(const std::string& modulo, const std::string& mensaje) {
        log(NivelLog::DEBUG, modulo, mensaje);
    }

    void info(const std::string& modulo, const std::string& mensaje) {
        log(NivelLog::INFO, modulo, mensaje);
    }

    void warn(const std::string& modulo, const std::string& mensaje) {
        log(NivelLog::WARN, modulo, mensaje);
    }

    void error(const std::string& modulo, const std::string& mensaje) {
        log(NivelLog::ERROR, modulo, mensaje);
    }
};

int main() {
    std::cout << "=== ACTIVIDAD 1: VERIFICACION SINGLETON LOGGER (C++17) ===" << std::endl;

    Logger& log1 = Logger::instancia();
    Logger& log2 = Logger::instancia();

    assert(&log1 == &log2);
    std::cout << "[OK] Assert unicidad: &log1 == &log2 (" << &log1 << " == " << &log2 << ")" << std::endl;

    log1.debug("PruebaC++", "Mensaje de depuracion (DEBUG)");
    log1.info("PruebaC++", "Mensaje informativo del sistema (INFO)");
    log2.warn("PruebaC++", "Advertencia de consumo de recursos (WARN)");
    log2.error("PruebaC++", "Error simulado en subsistema (ERROR)");

    std::cout << "Iniciando prueba con hilos concurrentes..." << std::endl;
    std::vector<std::thread> hilos;
    for (int i = 0; i < 5; ++i) {
        hilos.emplace_back([i]() {
            Logger& logHilo = Logger::instancia();
            assert(&logHilo == &Logger::instancia());
            logHilo.info("Hilo-" + std::to_string(i), "Log concurrente desde hilo secundario.");
        });
    }

    for (auto& h : hilos) {
        h.join();
    }

    std::cout << "[OK] Todos los hilos finalizaron exitosamente." << std::endl;
    std::cout << "[OK] Verificacion completada: Singleton C++17 implementado correctamente." << std::endl;

    return 0;
}
