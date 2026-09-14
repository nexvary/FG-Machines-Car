#pragma once

#include "fg/uds.hpp"

#include <cstdint>
#include <functional>
#include <string>
#include <vector>

namespace fg::diag {

struct CodingSafetyPolicy {
    double min_voltage{12.0};
    double max_voltage{15.5};
    bool require_backup{true};
    bool verify_after_write{true};
};

struct CodingResult {
    bool success{false};
    bool rollback_attempted{false};
    bool rollback_succeeded{false};
    std::string message;
    std::vector<std::uint8_t> backup;
};

class CodingSession {
public:
    using VoltageProvider = std::function<double()>;

    CodingSession(UdsClient& uds, VoltageProvider voltage_provider,
                  CodingSafetyPolicy policy = {});

    void setWriteEnabled(bool enabled);
    bool writeEnabled() const;

    CodingResult applyDidChange(std::uint16_t did,
                                const std::vector<std::uint8_t>& new_value);

private:
    UdsClient& uds_;
    VoltageProvider voltage_provider_;
    CodingSafetyPolicy policy_;
    bool write_enabled_{false};
};

} // namespace fg::diag
