#include "fg/coding.hpp"
#include "fg/uds.hpp"
#include "fg/vci.hpp"

#include <cstdlib>
#include <iostream>
#include <vector>

using fg::diag::CodingSession;
using fg::diag::UdsClient;
using fg::diag::VirtualVci;

namespace {

void require(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

struct VirtualEcu {
    std::vector<std::uint8_t> did_f190{0x41, 0x42, 0x43};
    bool corrupt_next_write{false};

    std::vector<std::uint8_t> handle(const std::vector<std::uint8_t>& req) {
        if (req.empty()) return {};
        switch (req[0]) {
        case 0x10:
            if (req.size() >= 2) return {0x50, req[1]};
            break;
        case 0x3E:
            return {0x7E, 0x00};
        case 0x22:
            if (req.size() >= 3 && req[1] == 0xF1 && req[2] == 0x90) {
                std::vector<std::uint8_t> out{0x62, 0xF1, 0x90};
                out.insert(out.end(), did_f190.begin(), did_f190.end());
                return out;
            }
            break;
        case 0x2E:
            if (req.size() >= 4 && req[1] == 0xF1 && req[2] == 0x90) {
                if (corrupt_next_write) {
                    did_f190 = {0xEE};
                    corrupt_next_write = false;
                } else {
                    did_f190.assign(req.begin() + 3, req.end());
                }
                return {0x6E, 0xF1, 0x90};
            }
            break;
        default:
            break;
        }
        return {0x7F, req[0], 0x31};
    }
};

} // namespace

int main() {
    VirtualEcu ecu;
    VirtualVci vci([&](const auto& req) { return ecu.handle(req); });
    require(vci.open(), "virtual VCI should open");

    UdsClient uds(vci);
    uds.diagnosticSession(0x03);
    uds.testerPresent();
    require(uds.readDataByIdentifier(0xF190) == std::vector<std::uint8_t>({0x41, 0x42, 0x43}),
            "UDS DID read should return ECU data");

    CodingSession locked(uds, [] { return 13.2; });
    const auto blocked = locked.applyDidChange(0xF190, {0x10, 0x20});
    require(!blocked.success, "coding must be blocked while write lock is enabled");
    require(ecu.did_f190 == std::vector<std::uint8_t>({0x41, 0x42, 0x43}),
            "blocked coding must not change ECU data");

    CodingSession low_voltage(uds, [] { return 10.8; });
    low_voltage.setWriteEnabled(true);
    const auto voltage_blocked = low_voltage.applyDidChange(0xF190, {0x11, 0x22});
    require(!voltage_blocked.success, "coding must be blocked at unsafe voltage");

    CodingSession coding(uds, [] { return 13.4; });
    coding.setWriteEnabled(true);
    const auto ok = coding.applyDidChange(0xF190, {0x55, 0x66});
    require(ok.success, "safe coding transaction should succeed");
    require(ok.backup == std::vector<std::uint8_t>({0x41, 0x42, 0x43}),
            "coding transaction should preserve a backup");
    require(ecu.did_f190 == std::vector<std::uint8_t>({0x55, 0x66}),
            "verified coding value should remain active");

    ecu.corrupt_next_write = true;
    const auto rolled_back = coding.applyDidChange(0xF190, {0x77, 0x88});
    require(!rolled_back.success, "verification mismatch must fail the transaction");
    require(rolled_back.rollback_attempted, "verification mismatch must attempt rollback");
    require(rolled_back.rollback_succeeded, "rollback must be verified");
    require(ecu.did_f190 == std::vector<std::uint8_t>({0x55, 0x66}),
            "rollback must restore the previous coding value");

    vci.close();
    std::cout << "FG_PREHARDWARE_TESTS_PASS\n";
    return 0;
}
