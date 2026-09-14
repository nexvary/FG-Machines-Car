#include "fg/guarded_coding.hpp"

namespace fg::diag {

GuardedCodingEngine::GuardedCodingEngine(UdsClient& uds, VoltageProvider voltage_provider,
                                         TransactionJournal* journal)
    : uds_(uds), voltage_provider_(std::move(voltage_provider)), journal_(journal) {}

void GuardedCodingEngine::setWriteEnabled(bool enabled) {
    write_enabled_ = enabled;
}

bool GuardedCodingEngine::writeEnabled() const {
    return write_enabled_;
}

void GuardedCodingEngine::journal(const GuardedCodingRequest& request,
                                  std::uint16_t did,
                                  TransactionState state,
                                  const std::string& message,
                                  const std::vector<std::uint8_t>& before,
                                  const std::vector<std::uint8_t>& after) const {
    if (!journal_) return;
    TransactionRecord record;
    record.transaction_id = request.transaction_id;
    record.utc_timestamp = request.utc_timestamp;
    record.vin = request.actual_identity.vin;
    record.ecu_name = request.actual_identity.ecu_name;
    record.did = did;
    record.state = state;
    record.message = message;
    record.before_value = before;
    record.after_value = after;
    (void)journal_->append(record);
}

GuardedCodingResult GuardedCodingEngine::execute(const GuardedCodingRequest& request) {
    GuardedCodingResult result;
    if (!request.profile) {
        result.blocked_by_definition = true;
        result.failures.emplace_back("coding profile is missing");
        return result;
    }

    const auto profile_validation = validateCodingProfile(*request.profile);
    if (!profile_validation.valid) {
        result.blocked_by_definition = true;
        result.failures = profile_validation.errors;
        return result;
    }

    const auto* parameter = findCodingParameter(*request.profile, request.parameter_key);
    if (!parameter) {
        result.blocked_by_definition = true;
        result.failures.emplace_back("coding parameter is not defined for this profile");
        return result;
    }

    std::string value_error;
    if (!validateCodingValue(*parameter, request.new_value, &value_error)) {
        result.blocked_by_definition = true;
        result.failures.push_back(value_error);
        return result;
    }

    const auto identity = checkEcuIdentity(request.actual_identity,
                                           request.profile->identity_policy);
    if (!identity.allowed) {
        result.blocked_by_identity = true;
        result.failures = identity.failures;
        journal(request, parameter->did, TransactionState::Failed,
                "ECU identity guard rejected coding request");
        return result;
    }

    if (!write_enabled_) {
        result.failures.emplace_back("global guarded-coding write lock is enabled");
        journal(request, parameter->did, TransactionState::Failed,
                "global write lock blocked coding request");
        return result;
    }

    journal(request, parameter->did, TransactionState::Planned,
            "coding transaction accepted by pre-write guards");

    try {
        uds_.diagnosticSession(parameter->required_session);
    } catch (const std::exception& ex) {
        result.failures.emplace_back(ex.what());
        journal(request, parameter->did, TransactionState::Failed,
                "unable to enter required diagnostic session");
        return result;
    }

    CodingSafetyPolicy policy;
    policy.require_backup = parameter->requires_backup;
    CodingSession coding(uds_, voltage_provider_, policy);
    coding.setWriteEnabled(true);
    result.coding = coding.applyDidChange(parameter->did, request.new_value);

    if (!result.coding.backup.empty()) {
        journal(request, parameter->did, TransactionState::BackupCaptured,
                "pre-write backup captured", result.coding.backup);
    }

    if (result.coding.success) {
        result.success = true;
        journal(request, parameter->did, TransactionState::WriteVerified,
                result.coding.message, result.coding.backup, request.new_value);
        return result;
    }

    if (result.coding.rollback_attempted) {
        journal(request, parameter->did, TransactionState::RollbackStarted,
                "rollback attempted", request.new_value, result.coding.backup);
        if (result.coding.rollback_succeeded) {
            journal(request, parameter->did, TransactionState::RollbackVerified,
                    "rollback verified", request.new_value, result.coding.backup);
        }
    }

    result.failures.push_back(result.coding.message);
    journal(request, parameter->did, TransactionState::Failed,
            result.coding.message, result.coding.backup, request.new_value);
    return result;
}

} // namespace fg::diag
