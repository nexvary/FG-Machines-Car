#pragma once

#include "fg/ecu_identity.hpp"

#include <cstddef>
#include <cstdint>
#include <optional>
#include <string>
#include <vector>

namespace fg::diag {

struct CodingParameterDefinition {
    std::string key;
    std::string display_name;
    std::uint16_t did{0};
    std::size_t exact_length{0};
    std::uint8_t required_session{0x03};
    bool writable{false};
    bool requires_backup{true};
};

struct CodingProfileDefinition {
    std::string id;
    std::string manufacturer;
    std::string model;
    EcuIdentityPolicy identity_policy;
    std::vector<CodingParameterDefinition> parameters;
};

struct DefinitionValidationResult {
    bool valid{false};
    std::vector<std::string> errors;
};

DefinitionValidationResult validateCodingProfile(const CodingProfileDefinition& profile);
const CodingParameterDefinition* findCodingParameter(const CodingProfileDefinition& profile,
                                                      const std::string& key);
bool validateCodingValue(const CodingParameterDefinition& parameter,
                         const std::vector<std::uint8_t>& value,
                         std::string* error = nullptr);

} // namespace fg::diag
