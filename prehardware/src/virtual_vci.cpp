#include "fg/vci.hpp"

#include <stdexcept>

namespace fg::diag {

VirtualVci::VirtualVci(Handler handler) : handler_(std::move(handler)) {}

bool VirtualVci::open() {
    open_ = true;
    return true;
}

void VirtualVci::close() {
    open_ = false;
}

bool VirtualVci::isOpen() const {
    return open_;
}

VciCapabilities VirtualVci::capabilities() const {
    return VciCapabilities{
        .can = true,
        .can_fd = true,
        .doip = true,
        .kline = true,
        .j1850 = true,
        .j2534 = true,
        .rp1210 = true,
        .dpdu = true,
    };
}

std::vector<std::uint8_t> VirtualVci::transact(const std::vector<std::uint8_t>& request,
                                               std::uint32_t /*timeout_ms*/) {
    if (!open_) {
        throw std::runtime_error("VCI is not open");
    }
    if (!handler_) {
        return {};
    }
    return handler_(request);
}

void VirtualVci::setHandler(Handler handler) {
    handler_ = std::move(handler);
}

} // namespace fg::diag
