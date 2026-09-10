#pragma once

#include "fg/coding.hpp"
#include "fg/coding_definition.hpp"
#include "fg/transaction_journal.hpp"

#include <functional>
#include <string>
#include <vector>

namespace fg::diag {

struct GuardedCodingRequest {
    const CodingProfileDefinition* profile{nullptr};
    EcuIdentity actual_identity;
    std::string parameter_key;
    std::vector<std::uint8_t> new_value;
    std::string transaction_id;
    std::string utc_timestamp;
};

struct GuardedCodingResult {
    bool success{false};
    bool blocked_by_definition{false};
    bool blocked_by_identity{false};
    CodingResult coding;
    std::vector<std::string> failures;
};

class GuardedCodingEngine {
public:
    using VoltageProvider = CodingSession::VoltageProvider;

    GuardedCodingEngine(UdsClient& uds, VoltageProvider voltage_provider,
                        TransactionJournal* journal = nullptr);

    void setWriteEnabled(bool enabled);
    bool writeEnabled() const;
    GuardedCodingResult execute(const GuardedCodingRequest& request);

private:
    void journal(const GuardedCodingRequest& request,
                 std::uint16_t did,
                 TransactionState state,
                 const std::string& message,
                 const std::vector<std::uint8_t>& before = {},
                 const std::vector<std::uint8_t>& after = {}) const;

    UdsClient& uds_;
    VoltageProvider voltage_provider_;
    TransactionJournal* journal_{nullptr};
    bool write_enabled_{false};
};

} // namespace fg::diag
