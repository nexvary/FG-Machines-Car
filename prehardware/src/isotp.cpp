#include "fg/isotp.hpp"

namespace fg::diag {

bool validateIsoTpProfile(const IsoTpProfile& profile, std::string* error) {
    const auto fail = [&](const char* message) {
        if (error) *error = message;
        return false;
    };

    if (profile.bitrate < 10000 || profile.bitrate > 5000000) {
        return fail("CAN bitrate is outside supported validation bounds");
    }
    const std::uint32_t max_id =
        profile.id_format == CanIdFormat::Standard11 ? 0x7FFU : 0x1FFFFFFFU;
    if (profile.tx_id > max_id || profile.rx_id > max_id) {
        return fail("CAN identifier exceeds selected identifier format");
    }
    if (profile.tx_id == profile.rx_id) {
        return fail("TX and RX identifiers must differ");
    }
    if (profile.can_fd && profile.bitrate < 125000) {
        return fail("CAN-FD profile requires a practical arbitration bitrate");
    }
    if (error) error->clear();
    return true;
}

} // namespace fg::diag
