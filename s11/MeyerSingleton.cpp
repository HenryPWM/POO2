// ✅ Singleton Meyers — thread-safe desde C++11 por garantía del estándar

#include <string>

#include <iostream>

#include <fstream>

#include <mutex>

#include <chrono>

#include <iomanip>

#include <sstream>
enum class NivelLog { DEBUG, INFO, WARN, ERROR };

class Logger {

private:

std::ofstream archivo_;

std::mutex mtx_;

NivelLog nivelMinimo_;


// Constructor privado: nadie puede crear instancias directamente

explicit Logger(const std::string& ruta = "app.log",

NivelLog nivel = NivelLog::INFO)

: nivelMinimo_(nivel) {

archivo_.open(ruta, std::ios::app);

if (!archivo_.is_open())

throw std::runtime_error("No se puede abrir " + ruta);

}


// Eliminar copia y movimiento — garantiza unicidad

Logger(const Logger&) = delete;

Logger& operator=(const Logger&) = delete;

Logger(Logger&&) = delete;

Logger& operator=(Logger&&) = delete;


std::string timestamp() const {

auto now = std::chrono::system_clock::now();

auto t = std::chrono::system_clock::to_time_t(now);

std::ostringstream oss;

oss << std::put_time(std::localtime(&t), "%Y-%m-%d %H:%M:%S");

return oss.str();

}


static std::string nivelStr(NivelLog n) {

switch(n) {

case NivelLog::DEBUG: return "DEBUG";

case NivelLog::INFO: return "INFO ";

case NivelLog::WARN: return "WARN ";

case NivelLog::ERROR: return "ERROR";

}

return "?????";

}


public:

// Punto de acceso único — static local: inicialización thread-safe (C++11)

static Logger& instancia(const std::string& ruta = "app.log") {

static Logger inst(ruta); // se crea UNA sola vez, garantía C++11

return inst;

}


void log(NivelLog nivel, const std::string& modulo,

const std::string& mensaje) {

if (nivel < nivelMinimo_) return;

std::lock_guard<std::mutex> lock(mtx_);

std::string entrada = "[" + timestamp() + "] [" +

nivelStr(nivel) + "] [" + modulo + "] " + mensaje;

archivo_ << entrada << "\n";

archivo_.flush();

std::cout << entrada << "\n";

}


void info (const std::string& mod, const std::string& msg)

{ log(NivelLog::INFO, mod, msg); }

void warn (const std::string& mod, const std::string& msg)

{ log(NivelLog::WARN, mod, msg); }

void error(const std::string& mod, const std::string& msg)

{ log(NivelLog::ERROR, mod, msg); }

};


// ── Uso: mismo objeto en cualquier parte del sistema ──

class ServicioMatricula {

public:

void matricular(const std::string& est, const std::string& curso) {

Logger::instancia().info("ServicioMatricula",

"Matriculando " + est + " en " + curso);

// ... lógica de matrícula

Logger::instancia().info("ServicioMatricula", "Matrícula exitosa");

}

};


int main() {

Logger::instancia().info("Main", "Sistema iniciado");

ServicioMatricula svc;

svc.matricular("2023001", "SIS206");

Logger::instancia().warn("Main", "Carga alta detectada");

// &Logger::instancia() == &Logger::instancia() → true siempre

std::cout << "Misma instancia: " << std::boolalpha

<< (&Logger::instancia() == &Logger::instancia()) << std::endl;

return 0;

}