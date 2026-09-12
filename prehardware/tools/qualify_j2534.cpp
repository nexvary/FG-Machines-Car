#include "fg/j2534.hpp"
#include "fg/j2534_registry.hpp"
#include "fg/uds.hpp"

#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <string>

namespace {
std::uint32_t parseNumber(const char* text) {
    return static_cast<std::uint32_t>(std::stoul(text, nullptr, 0));
}
}

int main(int argc, char** argv) {
    using namespace fg::diag;

    if (argc == 2 && std::string(argv[1]) == "--list") {
        const auto devices = discoverJ2534Devices();
        std::cout << "FG_J2534_DISCOVERY count=" << devices.size() << '\n';
        for (const auto& device : devices) {
            std::cout << device.name << "\t" << device.vendor << "\t"
                      << device.function_library << '\n';
        }
        return 0;
    }

    if (argc < 4) {
        std::cerr << "Usage: fg_j2534_qualify --list\n"
                  << "   or: fg_j2534_qualify <dll> <tx_id> <rx_id> [baud]\n"
                  << "This tool is read-only and performs open/session/VIN-read checks only.\n";
        return 2;
    }

    J2534Config config;
    config.dll_path = argv[1];
    config.tx_id = parseNumber(argv[2]);
    config.rx_id = parseNumber(argv[3]);
    if (argc >= 5) config.baud = parseNumber(argv[4]);

    J2534Vci vci(config);
    if (!vci.open()) {
        std::cerr << "FG_J2534_OPEN_FAIL " << vci.lastError() << '\n';
        return 3;
    }

    try {
        UdsClient uds(vci);
        uds.diagnosticSession(0x01);
        const auto vin = uds.readDataByIdentifier(0xF190);
        std::cout << "FG_J2534_READONLY_QUALIFICATION_PASS vin_bytes=" << vin.size() << " vin=";
        for (const auto byte : vin) {
            if (byte >= 32 && byte <= 126) std::cout << static_cast<char>(byte);
            else std::cout << '.';
        }
        std::cout << '\n';
        vci.close();
        return 0;
    } catch (const std::exception& ex) {
        std::cerr << "FG_J2534_READONLY_QUALIFICATION_FAIL " << ex.what() << '\n';
        vci.close();
        return 4;
    }
}
