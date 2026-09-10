#include "fg/virtual_ecu.hpp"

namespace fg::diag {

void VirtualEcu::setDid(std::uint16_t did, std::vector<std::uint8_t> value) {
    dids_[did] = std::move(value);
}

std::vector<std::uint8_t> VirtualEcu::getDid(std::uint16_t did) const {
    const auto it = dids_.find(did);
    return it == dids_.end() ? std::vector<std::uint8_t>{} : it->second;
}

void VirtualEcu::injectFault(VirtualEcuFault fault) {
    fault_ = fault;
}

std::vector<std::uint8_t> VirtualEcu::handle(const std::vector<std::uint8_t>& request) {
    ++request_count_;
    if (request.empty()) return {};

    if (fault_ == VirtualEcuFault::EmptyResponseOnce) {
        fault_ = VirtualEcuFault::None;
        return {};
    }
    if (fault_ == VirtualEcuFault::NegativeResponseOnce) {
        fault_ = VirtualEcuFault::None;
        return {0x7F, request[0], 0x22};
    }

    switch (request[0]) {
    case 0x10:
        if (request.size() < 2) break;
        session_ = request[1];
        return {0x50, session_};
    case 0x11:
        if (request.size() < 2) break;
        session_ = 0x01;
        return {0x51, request[1]};
    case 0x3E:
        return {0x7E, request.size() > 1 ? request[1] : static_cast<std::uint8_t>(0)};
    case 0x22: {
        if (request.size() < 3) break;
        const auto did = static_cast<std::uint16_t>((request[1] << 8) | request[2]);
        const auto it = dids_.find(did);
        if (it == dids_.end()) return {0x7F, 0x22, 0x31};
        std::vector<std::uint8_t> out{0x62, request[1], request[2]};
        out.insert(out.end(), it->second.begin(), it->second.end());
        return out;
    }
    case 0x2E: {
        if (request.size() < 4) break;
        if (fault_ == VirtualEcuFault::RejectWriteOnce) {
            fault_ = VirtualEcuFault::None;
            return {0x7F, 0x2E, 0x72};
        }
        const auto did = static_cast<std::uint16_t>((request[1] << 8) | request[2]);
        if (fault_ == VirtualEcuFault::CorruptWriteOnce) {
            dids_[did] = {0xEE};
            fault_ = VirtualEcuFault::None;
        } else {
            dids_[did] = {request.begin() + 3, request.end()};
        }
        return {0x6E, request[1], request[2]};
    }
    case 0x31:
        if (request.size() < 4) break;
        return {0x71, request[1], request[2], request[3]};
    case 0x14:
        return {0x54};
    case 0x19:
        if (request.size() < 2) break;
        return {0x59, request[1], 0xFF};
    default:
        break;
    }
    return {0x7F, request[0], 0x13};
}

std::uint8_t VirtualEcu::activeSession() const {
    return session_;
}

std::size_t VirtualEcu::requestCount() const {
    return request_count_;
}

} // namespace fg::diag
