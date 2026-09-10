#include "fg/uds.hpp"

#include <sstream>

namespace fg::diag {

std::vector<std::uint8_t> UdsClient::request(const std::vector<std::uint8_t>& payload,
                                             std::uint32_t timeout_ms) {
    if (payload.empty()) {
        throw UdsError("empty UDS request");
    }
    const auto response = vci_.transact(payload, timeout_ms);
    if (response.empty()) {
        throw UdsError("empty UDS response");
    }
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
    if (response[0] != expected) {
        throw UdsError("unexpected UDS service response");
    }
    return response;
}

void UdsClient::diagnosticSession(std::uint8_t session) {
    const auto response = request({0x10, session});
    if (response.size() < 2 || response[1] != session) {
        throw UdsError("diagnostic session confirmation mismatch");
    }
}

std::vector<std::uint8_t> UdsClient::readDataByIdentifier(std::uint16_t did) {
    const std::uint8_t hi = static_cast<std::uint8_t>((did >> 8) & 0xFF);
    const std::uint8_t lo = static_cast<std::uint8_t>(did & 0xFF);
    const auto response = request({0x22, hi, lo});
    if (response.size() < 3 || response[1] != hi || response[2] != lo) {
        throw UdsError("DID read confirmation mismatch");
    }
    return {response.begin() + 3, response.end()};
}

void UdsClient::writeDataByIdentifier(std::uint16_t did,
                                      const std::vector<std::uint8_t>& value) {
    const std::uint8_t hi = static_cast<std::uint8_t>((did >> 8) & 0xFF);
    const std::uint8_t lo = static_cast<std::uint8_t>(did & 0xFF);
    std::vector<std::uint8_t> request_payload{0x2E, hi, lo};
    request_payload.insert(request_payload.end(), value.begin(), value.end());
    const auto response = request(request_payload);
    if (response.size() < 3 || response[1] != hi || response[2] != lo) {
        throw UdsError("DID write confirmation mismatch");
    }
}

void UdsClient::testerPresent() {
    (void)request({0x3E, 0x00});
}

} // namespace fg::diag
