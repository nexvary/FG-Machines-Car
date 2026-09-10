#pragma once

#include "fg/vci.hpp"

#include <cstdint>
#include <stdexcept>
#include <vector>

namespace fg::diag {

class UdsError : public std::runtime_error {
public:
    using std::runtime_error::runtime_error;
};

class UdsClient {
public:
    explicit UdsClient(IVci& vci) : vci_(vci) {}

    std::vector<std::uint8_t> request(const std::vector<std::uint8_t>& payload,
                                      std::uint32_t timeout_ms = 1500);
    void diagnosticSession(std::uint8_t session);
    std::vector<std::uint8_t> readDataByIdentifier(std::uint16_t did);
    void writeDataByIdentifier(std::uint16_t did, const std::vector<std::uint8_t>& value);
    void testerPresent();

private:
    IVci& vci_;
};

} // namespace fg::diag
