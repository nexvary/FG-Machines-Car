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
    void ecuReset(std::uint8_t reset_type = 0x01);
    std::vector<std::uint8_t> readDataByIdentifier(std::uint16_t did);
    void writeDataByIdentifier(std::uint16_t did, const std::vector<std::uint8_t>& value);
    std::vector<std::uint8_t> routineControl(std::uint8_t control_type,
                                             std::uint16_t routine_id,
                                             const std::vector<std::uint8_t>& option_record = {});
    void clearDiagnosticInformation(std::uint32_t group_of_dtc = 0xFFFFFF);
    std::vector<std::uint8_t> readDtcInformation(std::uint8_t sub_function,
                                                 const std::vector<std::uint8_t>& parameters = {});
    void testerPresent();

private:
    IVci& vci_;
};

} // namespace fg::diag
