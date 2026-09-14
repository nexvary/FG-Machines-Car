#include "fg/transaction_journal.hpp"

#include <fstream>
#include <iomanip>
#include <sstream>

namespace fg::diag {

namespace {
std::string escapeField(const std::string& value) {
    std::string out;
    out.reserve(value.size());
    for (char c : value) {
        if (c == '\\' || c == '\t' || c == '\n' || c == '\r') {
            out.push_back('\\');
            switch (c) {
            case '\t': out.push_back('t'); break;
            case '\n': out.push_back('n'); break;
            case '\r': out.push_back('r'); break;
            default: out.push_back('\\'); break;
            }
        } else {
            out.push_back(c);
        }
    }
    return out;
}
} // namespace

std::string transactionStateName(TransactionState state) {
    switch (state) {
    case TransactionState::Planned: return "PLANNED";
    case TransactionState::BackupCaptured: return "BACKUP_CAPTURED";
    case TransactionState::WriteStarted: return "WRITE_STARTED";
    case TransactionState::WriteVerified: return "WRITE_VERIFIED";
    case TransactionState::RollbackStarted: return "ROLLBACK_STARTED";
    case TransactionState::RollbackVerified: return "ROLLBACK_VERIFIED";
    case TransactionState::Failed: return "FAILED";
    }
    return "UNKNOWN";
}

std::string hexEncode(const std::vector<std::uint8_t>& bytes) {
    std::ostringstream stream;
    stream << std::hex << std::setfill('0');
    for (const auto byte : bytes) stream << std::setw(2) << static_cast<unsigned int>(byte);
    return stream.str();
}

TransactionJournal::TransactionJournal(std::filesystem::path path) : path_(std::move(path)) {}

bool TransactionJournal::append(const TransactionRecord& record, std::string* error) const {
    std::error_code ec;
    if (path_.has_parent_path()) std::filesystem::create_directories(path_.parent_path(), ec);
    if (ec) {
        if (error) *error = "unable to create journal directory: " + ec.message();
        return false;
    }

    std::ofstream out(path_, std::ios::app | std::ios::binary);
    if (!out) {
        if (error) *error = "unable to open transaction journal";
        return false;
    }

    out << escapeField(record.transaction_id) << '\t'
        << escapeField(record.utc_timestamp) << '\t'
        << escapeField(record.vin) << '\t'
        << escapeField(record.ecu_name) << '\t'
        << record.did << '\t'
        << transactionStateName(record.state) << '\t'
        << hexEncode(record.before_value) << '\t'
        << hexEncode(record.after_value) << '\t'
        << escapeField(record.message) << '\n';
    out.flush();
    if (!out) {
        if (error) *error = "unable to persist transaction journal record";
        return false;
    }
    if (error) error->clear();
    return true;
}

const std::filesystem::path& TransactionJournal::path() const {
    return path_;
}

} // namespace fg::diag
