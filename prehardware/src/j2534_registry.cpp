#include "fg/j2534_registry.hpp"

#ifdef _WIN32
#define NOMINMAX
#include <windows.h>
#endif

#include <array>
#include <string>
#include <vector>

namespace fg::diag {

#ifdef _WIN32
namespace {

std::string readString(HKEY key, const char* value_name) {
    std::array<char, 2048> buffer{};
    DWORD type = 0;
    DWORD size = static_cast<DWORD>(buffer.size());
    if (RegQueryValueExA(key, value_name, nullptr, &type,
                         reinterpret_cast<LPBYTE>(buffer.data()), &size) != ERROR_SUCCESS) {
        return {};
    }
    if (type != REG_SZ && type != REG_EXPAND_SZ) return {};
    if (type == REG_EXPAND_SZ) {
        std::array<char, 4096> expanded{};
        const auto written = ExpandEnvironmentStringsA(buffer.data(), expanded.data(),
                                                        static_cast<DWORD>(expanded.size()));
        if (written > 0 && written < expanded.size()) return expanded.data();
    }
    return buffer.data();
}

void enumerateRoot(const char* path, std::vector<J2534DeviceInfo>& out) {
    HKEY root = nullptr;
    if (RegOpenKeyExA(HKEY_LOCAL_MACHINE, path, 0, KEY_READ, &root) != ERROR_SUCCESS) return;

    DWORD index = 0;
    for (;;) {
        std::array<char, 512> subkey_name{};
        DWORD subkey_len = static_cast<DWORD>(subkey_name.size());
        const auto status = RegEnumKeyExA(root, index++, subkey_name.data(), &subkey_len,
                                          nullptr, nullptr, nullptr, nullptr);
        if (status == ERROR_NO_MORE_ITEMS) break;
        if (status != ERROR_SUCCESS) continue;

        HKEY subkey = nullptr;
        if (RegOpenKeyExA(root, subkey_name.data(), 0, KEY_READ, &subkey) != ERROR_SUCCESS) continue;

        J2534DeviceInfo info;
        info.name = readString(subkey, "Name");
        info.vendor = readString(subkey, "Vendor");
        info.function_library = readString(subkey, "FunctionLibrary");
        info.protocol_version = readString(subkey, "ProtocolVersion");
        if (info.name.empty()) info.name.assign(subkey_name.data(), subkey_len);
        if (!info.function_library.empty()) out.push_back(std::move(info));
        RegCloseKey(subkey);
    }
    RegCloseKey(root);
}

} // namespace
#endif

std::vector<J2534DeviceInfo> discoverJ2534Devices() {
    std::vector<J2534DeviceInfo> devices;
#ifdef _WIN32
    enumerateRoot("SOFTWARE\\PassThruSupport.04.04", devices);
    enumerateRoot("SOFTWARE\\WOW6432Node\\PassThruSupport.04.04", devices);
#endif
    return devices;
}

} // namespace fg::diag
