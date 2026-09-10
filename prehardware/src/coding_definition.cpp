#include "fg/coding_definition.hpp"

#include <set>

namespace fg::diag {

DefinitionValidationResult validateCodingProfile(const CodingProfileDefinition& profile) {
    DefinitionValidationResult result;
    if (profile.id.empty()) result.errors.emplace_back("profile id is required");
    if (profile.manufacturer.empty()) result.errors.emplace_back("manufacturer is required");
    if (profile.parameters.empty()) result.errors.emplace_back("at least one coding parameter is required");

    std::set<std::string> keys;
    std::set<std::uint16_t> dids;
    for (const auto& parameter : profile.parameters) {
        if (parameter.key.empty()) result.errors.emplace_back("coding parameter key is required");
        if (parameter.did == 0) result.errors.emplace_back("coding parameter DID cannot be zero");
        if (parameter.exact_length == 0) result.errors.emplace_back("coding parameter length must be non-zero");
        if (!parameter.key.empty() && !keys.insert(parameter.key).second) {
            result.errors.emplace_back("duplicate coding parameter key: " + parameter.key);
        }
        if (parameter.did != 0 && !dids.insert(parameter.did).second) {
            result.errors.emplace_back("duplicate coding DID");
        }
    }
    result.valid = result.errors.empty();
    return result;
}

const CodingParameterDefinition* findCodingParameter(const CodingProfileDefinition& profile,
                                                      const std::string& key) {
    for (const auto& parameter : profile.parameters) {
        if (parameter.key == key) return &parameter;
    }
    return nullptr;
}

bool validateCodingValue(const CodingParameterDefinition& parameter,
                         const std::vector<std::uint8_t>& value,
                         std::string* error) {
    if (!parameter.writable) {
        if (error) *error = "coding parameter is read-only";
        return false;
    }
    if (value.size() != parameter.exact_length) {
        if (error) *error = "coding value length does not match definition";
        return false;
    }
    if (error) error->clear();
    return true;
}

} // namespace fg::diag
