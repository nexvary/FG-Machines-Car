#pragma once

#include <cstdint>
#include <map>
#include <vector>

namespace fg::diag {

enum class VirtualEcuFault {
    None,
    EmptyResponseOnce,
    NegativeResponseOnce,
    CorruptWriteOnce,
    RejectWriteOnce
};

class VirtualEcu {
public:
    void setDid(std::uint16_t did, std::vector<std::uint8_t> value);
    std::vector<std::uint8_t> getDid(std::uint16_t did) const;
    void injectFault(VirtualEcuFault fault);
    std::vector<std::uint8_t> handle(const std::vector<std::uint8_t>& request);

    std::uint8_t activeSession() const;
    std::size_t requestCount() const;

private:
    std::map<std::uint16_t, std::vector<std::uint8_t>> dids_;
    VirtualEcuFault fault_{VirtualEcuFault::None};
    std::uint8_t session_{0x01};
    std::size_t request_count_{0};
};

} // namespace fg::diag
