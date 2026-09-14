#pragma once

#include <cstdint>
#include <string>

namespace fg::diag {

enum class CanIdFormat {
    Standard11,
    Extended29
};

enum class IsoTpAddressingMode {
    Normal,
    Extended,
    Mixed
};

struct IsoTpProfile {
    std::uint32_t tx_id{0x7E0};
    std::uint32_t rx_id{0x7E8};
    std::uint32_t bitrate{500000};
    CanIdFormat id_format{CanIdFormat::Standard11};
    IsoTpAddressingMode addressing{IsoTpAddressingMode::Normal};
    std::uint8_t source_address{0};
    std::uint8_t target_address{0};
    bool can_fd{false};
};

bool validateIsoTpProfile(const IsoTpProfile& profile, std::string* error = nullptr);

} // namespace fg::diag
