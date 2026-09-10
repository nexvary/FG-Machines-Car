#pragma once

#include <cstdint>
#include <filesystem>
#include <string>
#include <vector>

namespace fg::diag {

enum class TransactionState {
    Planned,
    BackupCaptured,
    WriteStarted,
    WriteVerified,
    RollbackStarted,
    RollbackVerified,
    Failed
};

struct TransactionRecord {
    std::string transaction_id;
    std::string utc_timestamp;
    std::string vin;
    std::string ecu_name;
    std::uint16_t did{0};
    TransactionState state{TransactionState::Planned};
    std::string message;
    std::vector<std::uint8_t> before_value;
    std::vector<std::uint8_t> after_value;
};

std::string transactionStateName(TransactionState state);
std::string hexEncode(const std::vector<std::uint8_t>& bytes);

class TransactionJournal {
public:
    explicit TransactionJournal(std::filesystem::path path);
    bool append(const TransactionRecord& record, std::string* error = nullptr) const;
    const std::filesystem::path& path() const;

private:
    std::filesystem::path path_;
};

} // namespace fg::diag
