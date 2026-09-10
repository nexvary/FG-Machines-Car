#pragma once

#include "fg/vci.hpp"

#include <cstdint>
#include <memory>
#include <string>

namespace fg::diag {

enum class J2534Protocol : std::uint32_t {
    J1850Vpw = 1,
    J1850Pwm = 2,
    Iso9141 = 3,
    Iso14230 = 4,
    Can = 5,
    Iso15765 = 6
};

struct J2534Config {
    std::string dll_path;
    J2534Protocol protocol{J2534Protocol::Iso15765};
    std::uint32_t baud{500000};
    std::uint32_t connect_flags{0};
};

class J2534Vci final : public IVci {
public:
    explicit J2534Vci(J2534Config config);
    ~J2534Vci() override;

    J2534Vci(const J2534Vci&) = delete;
    J2534Vci& operator=(const J2534Vci&) = delete;

    bool open() override;
    void close() override;
    bool isOpen() const override;
    VciCapabilities capabilities() const override;
    std::vector<std::uint8_t> transact(const std::vector<std::uint8_t>& request,
                                       std::uint32_t timeout_ms) override;

    const std::string& lastError() const;

private:
    struct Impl;
    std::unique_ptr<Impl> impl_;
};

} // namespace fg::diag
