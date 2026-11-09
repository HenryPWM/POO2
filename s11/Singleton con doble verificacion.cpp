// Singleton con atomic + mutex para control fino (uso avanzado)

#include <atomic>

#include <memory>


class ConfiguracionApp {

private:

static std::atomic<ConfiguracionApp*> instancia_;

static std::mutex mtx_;

std::string dbUrl_;

int maxConexiones_;


ConfiguracionApp() : dbUrl_("sqlite:///app.db"), maxConexiones_(10) {}

ConfiguracionApp(const ConfiguracionApp&) = delete;


public:

static ConfiguracionApp* obtener() {

ConfiguracionApp* p = instancia_.load(std::memory_order_acquire);

if (!p) {

std::lock_guard<std::mutex> lock(mtx_);

p = instancia_.load(std::memory_order_relaxed);

if (!p) {

p = new ConfiguracionApp();

instancia_.store(p, std::memory_order_release);

}

}

return p;

}

[[nodiscard]] const std::string& dbUrl() const noexcept { return dbUrl_; }

[[nodiscard]] int maxConexiones() const noexcept { return maxConexiones_; }

};

std::atomic<ConfiguracionApp*> ConfiguracionApp::instancia_{nullptr};

std::mutex ConfiguracionApp::mtx_;