#include "fg/uds.hpp"

#include <sstream>

namespace fg::diag {

std::vector<std::uint8_t> UdsClient::request(const std::vector<std::uint8_t>& payload,
                                             std::uint32_t timeout_ms) {
    if (payload.empty()) throw UdsError("empty UDS request");
    const auto response = vci_.transact(payload, timeout_ms);
    if (response.empty()) throw UdsError("empty UDS response");
    if (response[0] == 0x7F) {
        std::ostringstream oss;
        oss << "negative UDS response";
        if (response.size() >= 3) {
            oss << " service=0x" << std::hex << static_cast<int>(response[1])
                << " nrc=0x" << static_cast<int>(response[2]);
        }
        throw UdsError(oss.str());
    }
    const auto expected = static_cast<std::uint8_t>(payload[0] + 0x40U);
    if (response[0] != expected) throw UdsError("unexpected UDS service response");
    return response;
}

void UdsClient::diagnosticSession(std::uint8_t session) {
    const auto response = request({0x10, session});
    if (response.size() < 2 || response[1] != session) {
        throw UdsError("diagnostic session confirmation mismatch");
    }
}

void UdsClient::ecuReset(std::uint8_t reset_type) {
    const auto response = request({0x11, reset_type});
    if (response.size() < 2 || response[1] != reset_type) {
        throw UdsError("ECU reset confirmation mismatch");
    }
}

std::vector<std::uint8_t> UdsClient::readDataByIdentifier(std::uint16_t did) {
    const auto hi = static_cast<std::uint8_t>((did >> 8) & 0xFF);
    const auto lo = static_cast<std::uint8_t>(did & 0xFF);
    const auto response = request({0x22, hi, lo});
    if (response.size() < 3 || response[1] != hi || response[2] != lo) {
        throw UdsError("DID read confirmation mismatch");
    }
    return {response.begin() + 3, response.end()};
}

void UdsClient::writeDataByIdentifier(std::uint16_t did,
                                      const std::vector<std::uint8_t>& value) {
    const auto hi = static_cast<std::uint8_t>((did >> 8) & 0xFF);
    const auto lo = static_cast<std::uint8_t>(did & 0xFF);
    std::vector<std::uint8_t> payload{0x2E, hi, lo};
    payload.insert(payload.end(), value.begin(), value.end());
    const auto response = request(payload);
    if (response.size() < 3 || response[1] != hi || response[2] != lo) {
        throw UdsError("DID write confirmation mismatch");
    }
}

std::vector<std::uint8_t> UdsClient::routineControl(
    std::uint8_t control_type, std::uint16_t routine_id,
    const std::vector<std::uint8_t>& option_record) {
    const auto hi = static_cast<std::uint8_t>((routine_id >> 8) & 0xFF);
    const auto lo = static_cast<std::uint8_t>(routine_id & 0xFF);
    std::vector<std::uint8_t> payload{0x31, control_type, hi, lo};
    payload.insert(payload.end(), option_record.begin(), option_record.end());
    const auto response = request(payload);
    if (response.size() < 4 || response[1] != control_type ||
        response[2] != hi || response[3] != lo) {
        throw UdsError("routine control confirmation mismatch");
    }
    return {response.begin() + 4, response.end()};
}

void UdsClient::clearDiagnosticInformation(std::uint32_t group_of_dtc) {
    const std::vector<std::uint8_t> payload{
        0x14,
        static_cast<std::uint8_t>((group_of_dtc >> 16) & 0xFF),
        static_cast<std::uint8_t>((group_of_dtc >> 8) & 0xFF),
        static_cast<std::uint8_t>(group_of_dtc & 0xFF)};
    const auto response = request(payload);
    if (response.size() != 1) throw UdsError("clear DTC confirmation mismatch");
}

std::vector<std::uint8_t> UdsClient::readDtcInformation(
    std::uint8_t sub_function, const std::vector<std::uint8_t>& parameters) {
    std::vector<std::uint8_t> payload{0x19, sub_function};
    payload.insert(payload.end(), parameters.begin(), parameters.end());
    const auto response = request(payload);
    if (response.size() < 2 || response[1] != sub_function) {
        throw UdsError("read DTC confirmation mismatch");
    }
    return {response.begin() + 2, response.end()};
}

void UdsClient::testerPresent() {
    (void)request({0x3E, 0x00});
}

} // namespace fg::diag
