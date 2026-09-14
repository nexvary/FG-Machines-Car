#pragma once

#include <cstdint>
#include <functional>
#include <optional>
#include <string>
#include <vector>

namespace fg::diag {

enum class Protocol {
    Can,
    CanFd,
    DoIp,
    KLine,
    J1850
};

struct VciCapabilities {
    bool can{false};
    bool can_fd{false};
    bool doip{false};
    bool kline{false};
    bool j1850{false};
    bool j2534{false};
    bool rp1210{false};
    bool dpdu{false};
};

class IVci {
public:
    virtual ~IVci() = default;
    virtual bool open() = 0;
    virtual void close() = 0;
    virtual bool isOpen() const = 0;
    virtual VciCapabilities capabilities() const = 0;
    virtual std::vector<std::uint8_t> transact(const std::vector<std::uint8_t>& request,
                                               std::uint32_t timeout_ms) = 0;
};

class VirtualVci final : public IVci {
public:
    using Handler = std::function<std::vector<std::uint8_t>(const std::vector<std::uint8_t>&)>;

    explicit VirtualVci(Handler handler = {});

    bool open() override;
    void close() override;
    bool isOpen() const override;
    VciCapabilities capabilities() const override;
    std::vector<std::uint8_t> transact(const std::vector<std::uint8_t>& request,
                                       std::uint32_t timeout_ms) override;

    void setHandler(Handler handler);

private:
    bool open_{false};
    Handler handler_;
};

} // namespace fg::diag
