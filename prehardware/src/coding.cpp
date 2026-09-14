#include "fg/coding.hpp"

#include <exception>

namespace fg::diag {

CodingSession::CodingSession(UdsClient& uds, VoltageProvider voltage_provider,
                             CodingSafetyPolicy policy)
    : uds_(uds), voltage_provider_(std::move(voltage_provider)), policy_(policy) {}

void CodingSession::setWriteEnabled(bool enabled) {
    write_enabled_ = enabled;
}

bool CodingSession::writeEnabled() const {
    return write_enabled_;
}

CodingResult CodingSession::applyDidChange(std::uint16_t did,
                                           const std::vector<std::uint8_t>& new_value) {
    CodingResult result;

    if (!write_enabled_) {
        result.message = "write lock is enabled; coding is blocked";
        return result;
    }

    if (new_value.empty()) {
        result.message = "new coding value is empty";
        return result;
    }

    const double voltage = voltage_provider_ ? voltage_provider_() : 0.0;
    if (voltage < policy_.min_voltage || voltage > policy_.max_voltage) {
        result.message = "vehicle voltage is outside the allowed coding window";
        return result;
    }

    try {
        if (policy_.require_backup) {
            result.backup = uds_.readDataByIdentifier(did);
            if (result.backup.empty()) {
                result.message = "backup read returned empty data";
                return result;
            }
        }

        uds_.writeDataByIdentifier(did, new_value);

        if (!policy_.verify_after_write) {
            result.success = true;
            result.message = "coding write completed without verification";
            return result;
        }

        const auto verify = uds_.readDataByIdentifier(did);
        if (verify == new_value) {
            result.success = true;
            result.message = "coding write verified";
            return result;
        }

        result.message = "verification mismatch after coding write";
        if (!result.backup.empty()) {
            result.rollback_attempted = true;
            try {
                uds_.writeDataByIdentifier(did, result.backup);
                result.rollback_succeeded =
                    (uds_.readDataByIdentifier(did) == result.backup);
            } catch (...) {
                result.rollback_succeeded = false;
            }
        }
        return result;
    } catch (const std::exception& ex) {
        result.message = ex.what();
        if (!result.backup.empty()) {
            result.rollback_attempted = true;
            try {
                uds_.writeDataByIdentifier(did, result.backup);
                result.rollback_succeeded =
                    (uds_.readDataByIdentifier(did) == result.backup);
            } catch (...) {
                result.rollback_succeeded = false;
            }
        }
        return result;
    }
}

} // namespace fg::diag
