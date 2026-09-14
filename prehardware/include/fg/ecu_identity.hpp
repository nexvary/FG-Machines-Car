#pragma once

#include <cstdint>
#include <string>
#include <vector>

namespace fg::diag {

struct EcuIdentity {
    std::string vin;
    std::string manufacturer;
    std::string model;
    std::string ecu_name;
    std::string hardware_number;
    std::string software_number;
    std::string calibration_id;
};

struct EcuIdentityPolicy {
    std::string expected_vin;
    std::string expected_manufacturer;
    std::string expected_ecu_name;
    std::string expected_hardware_number;
    std::string expected_software_number;
    bool require_vin{true};
    bool require_hardware_match{true};
    bool require_software_match{true};
};

struct IdentityCheckResult {
    bool allowed{false};
    std::vector<std::string> failures;
};

bool looksLikeVin(const std::string& vin);
IdentityCheckResult checkEcuIdentity(const EcuIdentity& actual,
                                     const EcuIdentityPolicy& policy);

} // namespace fg::diag
