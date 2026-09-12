#pragma once

#include <string>
#include <vector>

namespace fg::diag {

struct J2534DeviceInfo {
    std::string name;
    std::string vendor;
    std::string function_library;
    std::string protocol_version;
};

std::vector<J2534DeviceInfo> discoverJ2534Devices();

} // namespace fg::diag
