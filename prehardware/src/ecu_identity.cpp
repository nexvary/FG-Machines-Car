#include "fg/ecu_identity.hpp"

#include <algorithm>
#include <cctype>

namespace fg::diag {

bool looksLikeVin(const std::string& vin) {
    if (vin.size() != 17) return false;
    return std::all_of(vin.begin(), vin.end(), [](unsigned char c) {
        if (!std::isalnum(c)) return false;
        const char u = static_cast<char>(std::toupper(c));
        return u != 'I' && u != 'O' && u != 'Q';
    });
}

IdentityCheckResult checkEcuIdentity(const EcuIdentity& actual,
                                     const EcuIdentityPolicy& policy) {
    IdentityCheckResult result;
    const auto mismatch = [&](bool condition, const char* message) {
        if (condition) result.failures.emplace_back(message);
    };

    if (policy.require_vin) {
        mismatch(!looksLikeVin(actual.vin), "actual VIN is missing or malformed");
        if (!policy.expected_vin.empty()) {
            mismatch(actual.vin != policy.expected_vin, "VIN mismatch");
        }
    }
    if (!policy.expected_manufacturer.empty()) {
        mismatch(actual.manufacturer != policy.expected_manufacturer, "manufacturer mismatch");
    }
    if (!policy.expected_ecu_name.empty()) {
        mismatch(actual.ecu_name != policy.expected_ecu_name, "ECU name mismatch");
    }
    if (policy.require_hardware_match && !policy.expected_hardware_number.empty()) {
        mismatch(actual.hardware_number != policy.expected_hardware_number,
                 "ECU hardware number mismatch");
    }
    if (policy.require_software_match && !policy.expected_software_number.empty()) {
        mismatch(actual.software_number != policy.expected_software_number,
                 "ECU software number mismatch");
    }

    result.allowed = result.failures.empty();
    return result;
}

} // namespace fg::diag
