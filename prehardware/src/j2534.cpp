#include "fg/j2534.hpp"

#include <algorithm>
#include <array>
#include <cstring>
#include <stdexcept>
#include <utility>

#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#endif

namespace fg::diag {

struct J2534Vci::Impl {
    explicit Impl(J2534Config cfg) : config(std::move(cfg)) {}

    J2534Config config;
    bool opened{false};
    std::string last_error;

#ifdef _WIN32
    using PtStatus = unsigned long;
    static constexpr PtStatus StatusNoError = 0;

    struct PassThruMsg {
        unsigned long ProtocolID;
        unsigned long RxStatus;
        unsigned long TxFlags;
        unsigned long Timestamp;
        unsigned long DataSize;
        unsigned long ExtraDataIndex;
        unsigned char Data[4128];
    };

    using FnOpen = PtStatus(__stdcall*)(void*, unsigned long*);
    using FnClose = PtStatus(__stdcall*)(unsigned long);
    using FnConnect = PtStatus(__stdcall*)(unsigned long, unsigned long, unsigned long,
                                           unsigned long, unsigned long*);
    using FnDisconnect = PtStatus(__stdcall*)(unsigned long);
    using FnReadMsgs = PtStatus(__stdcall*)(unsigned long, PassThruMsg*, unsigned long*, unsigned long);
    using FnWriteMsgs = PtStatus(__stdcall*)(unsigned long, PassThruMsg*, unsigned long*, unsigned long);
    using FnGetLastError = PtStatus(__stdcall*)(char*);

    HMODULE module{nullptr};
    FnOpen pass_thru_open{nullptr};
    FnClose pass_thru_close{nullptr};
    FnConnect pass_thru_connect{nullptr};
    FnDisconnect pass_thru_disconnect{nullptr};
    FnReadMsgs pass_thru_read{nullptr};
    FnWriteMsgs pass_thru_write{nullptr};
    FnGetLastError pass_thru_last_error{nullptr};
    unsigned long device_id{0};
    unsigned long channel_id{0};

    template <typename T>
    bool bind(T& target, const char* name) {
        target = reinterpret_cast<T>(GetProcAddress(module, name));
        if (!target) {
            last_error = std::string("missing J2534 symbol: ") + name;
            return false;
        }
        return true;
    }

    std::string driverError(const char* prefix) {
        if (pass_thru_last_error) {
            std::array<char, 256> buffer{};
            if (pass_thru_last_error(buffer.data()) == StatusNoError && buffer[0] != '\0') {
                return std::string(prefix) + ": " + buffer.data();
            }
        }
        return prefix;
    }
#endif
};

J2534Vci::J2534Vci(J2534Config config)
    : impl_(std::make_unique<Impl>(std::move(config))) {}

J2534Vci::~J2534Vci() {
    close();
}

bool J2534Vci::open() {
#ifdef _WIN32
    close();
    impl_->last_error.clear();

    impl_->module = LoadLibraryA(impl_->config.dll_path.c_str());
    if (!impl_->module) {
        impl_->last_error = "unable to load J2534 DLL: " + impl_->config.dll_path;
        return false;
    }

    if (!impl_->bind(impl_->pass_thru_open, "PassThruOpen") ||
        !impl_->bind(impl_->pass_thru_close, "PassThruClose") ||
        !impl_->bind(impl_->pass_thru_connect, "PassThruConnect") ||
        !impl_->bind(impl_->pass_thru_disconnect, "PassThruDisconnect") ||
        !impl_->bind(impl_->pass_thru_read, "PassThruReadMsgs") ||
        !impl_->bind(impl_->pass_thru_write, "PassThruWriteMsgs") ||
        !impl_->bind(impl_->pass_thru_last_error, "PassThruGetLastError")) {
        close();
        return false;
    }

    auto status = impl_->pass_thru_open(nullptr, &impl_->device_id);
    if (status != Impl::StatusNoError) {
        impl_->last_error = impl_->driverError("PassThruOpen failed");
        close();
        return false;
    }

    status = impl_->pass_thru_connect(
        impl_->device_id,
        static_cast<unsigned long>(impl_->config.protocol),
        impl_->config.connect_flags,
        impl_->config.baud,
        &impl_->channel_id);
    if (status != Impl::StatusNoError) {
        impl_->last_error = impl_->driverError("PassThruConnect failed");
        impl_->pass_thru_close(impl_->device_id);
        impl_->device_id = 0;
        close();
        return false;
    }

    impl_->opened = true;
    return true;
#else
    impl_->last_error = "J2534 hardware transport is available on Windows only";
    return false;
#endif
}

void J2534Vci::close() {
#ifdef _WIN32
    if (impl_->channel_id != 0 && impl_->pass_thru_disconnect) {
        impl_->pass_thru_disconnect(impl_->channel_id);
        impl_->channel_id = 0;
    }
    if (impl_->device_id != 0 && impl_->pass_thru_close) {
        impl_->pass_thru_close(impl_->device_id);
        impl_->device_id = 0;
    }
    if (impl_->module) {
        FreeLibrary(impl_->module);
        impl_->module = nullptr;
    }
#endif
    impl_->opened = false;
}

bool J2534Vci::isOpen() const {
    return impl_->opened;
}

VciCapabilities J2534Vci::capabilities() const {
    VciCapabilities caps;
    caps.j2534 = true;
    switch (impl_->config.protocol) {
    case J2534Protocol::Can:
    case J2534Protocol::Iso15765:
        caps.can = true;
        break;
    case J2534Protocol::Iso9141:
    case J2534Protocol::Iso14230:
        caps.kline = true;
        break;
    case J2534Protocol::J1850Vpw:
    case J2534Protocol::J1850Pwm:
        caps.j1850 = true;
        break;
    }
    return caps;
}

std::vector<std::uint8_t> J2534Vci::transact(const std::vector<std::uint8_t>& request,
                                              std::uint32_t timeout_ms) {
#ifdef _WIN32
    if (!impl_->opened) {
        throw std::runtime_error("J2534 VCI is not open");
    }
    if (request.empty()) {
        throw std::runtime_error("J2534 request is empty");
    }
    if (request.size() + 4 > 4128) {
        throw std::runtime_error("J2534 request exceeds PASSTHRU_MSG capacity");
    }

    Impl::PassThruMsg tx{};
    tx.ProtocolID = static_cast<unsigned long>(impl_->config.protocol);
    tx.Data[0] = static_cast<unsigned char>((impl_->config.tx_id >> 24) & 0xFF);
    tx.Data[1] = static_cast<unsigned char>((impl_->config.tx_id >> 16) & 0xFF);
    tx.Data[2] = static_cast<unsigned char>((impl_->config.tx_id >> 8) & 0xFF);
    tx.Data[3] = static_cast<unsigned char>(impl_->config.tx_id & 0xFF);
    std::copy(request.begin(), request.end(), tx.Data + 4);
    tx.DataSize = static_cast<unsigned long>(request.size() + 4);

    unsigned long count = 1;
    auto status = impl_->pass_thru_write(impl_->channel_id, &tx, &count, timeout_ms);
    if (status != Impl::StatusNoError || count != 1) {
        throw std::runtime_error(impl_->driverError("PassThruWriteMsgs failed"));
    }

    const auto deadline_slice = std::max<std::uint32_t>(timeout_ms, 1U);
    for (unsigned int attempt = 0; attempt < 8; ++attempt) {
        Impl::PassThruMsg rx{};
        count = 1;
        status = impl_->pass_thru_read(impl_->channel_id, &rx, &count, deadline_slice);
        if (status != Impl::StatusNoError || count == 0 || rx.DataSize < 4) {
            continue;
        }

        const std::uint32_t rx_id =
            (static_cast<std::uint32_t>(rx.Data[0]) << 24) |
            (static_cast<std::uint32_t>(rx.Data[1]) << 16) |
            (static_cast<std::uint32_t>(rx.Data[2]) << 8) |
            static_cast<std::uint32_t>(rx.Data[3]);
        if (rx_id != impl_->config.rx_id) {
            continue;
        }

        return {rx.Data + 4, rx.Data + rx.DataSize};
    }

    throw std::runtime_error("no matching J2534 response before timeout");
#else
    (void)request;
    (void)timeout_ms;
    throw std::runtime_error("J2534 hardware transport is available on Windows only");
#endif
}

const std::string& J2534Vci::lastError() const {
    return impl_->last_error;
}

} // namespace fg::diag
