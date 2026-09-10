#include "fg/coding.hpp"
#include "fg/coding_definition.hpp"
#include "fg/ecu_identity.hpp"
#include "fg/guarded_coding.hpp"
#include "fg/isotp.hpp"
#include "fg/j2534_registry.hpp"
#include "fg/transaction_journal.hpp"
#include "fg/uds.hpp"
#include "fg/vci.hpp"
#include "fg/virtual_ecu.hpp"

#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <string>
#include <vector>

using namespace fg::diag;

namespace {

void require(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "FAIL: " << message << '\n';
        std::exit(1);
    }
}

std::vector<std::uint8_t> bytes(const std::string& value) {
    return {value.begin(), value.end()};
}

} // namespace

int main() {
    // Stages 2-10: transport discovery model + ISO-TP profile validation.
    IsoTpProfile isotp;
    std::string profile_error;
    require(validateIsoTpProfile(isotp, &profile_error), "default ISO-TP profile should be valid");
    isotp.tx_id = isotp.rx_id;
    require(!validateIsoTpProfile(isotp, &profile_error), "same TX/RX CAN id must be rejected");
#ifndef _WIN32
    require(discoverJ2534Devices().empty(), "non-Windows J2534 discovery must safely return empty");
#endif

    // Stages 11-30: reusable Virtual ECU and UDS primitives.
    VirtualEcu ecu;
    const std::string vin = "WVWZZZ1JZXW000001";
    ecu.setDid(0xF190, bytes(vin));
    ecu.setDid(0xF1A0, {0x10, 0x20});

    VirtualVci vci([&](const auto& req) { return ecu.handle(req); });
    require(vci.open(), "virtual VCI should open");
    UdsClient uds(vci);

    uds.diagnosticSession(0x03);
    require(ecu.activeSession() == 0x03, "extended diagnostic session should be active");
    uds.testerPresent();
    require(uds.readDataByIdentifier(0xF190) == bytes(vin), "VIN DID read should match simulator");
    require(uds.routineControl(0x01, 0x0203).empty(), "routine control should be accepted");
    require(!uds.readDtcInformation(0x01).empty(), "read DTC service should return simulator data");
    uds.clearDiagnosticInformation();
    uds.ecuReset();
    require(ecu.activeSession() == 0x01, "ECU reset should restore default session in simulator");

    // Existing write-lock, voltage, backup, verification and rollback behavior.
    CodingSession locked(uds, [] { return 13.2; });
    const auto blocked = locked.applyDidChange(0xF1A0, {0x30, 0x40});
    require(!blocked.success, "coding must be blocked while write lock is enabled");
    require(ecu.getDid(0xF1A0) == std::vector<std::uint8_t>({0x10, 0x20}),
            "blocked coding must not change ECU data");

    CodingSession low_voltage(uds, [] { return 10.8; });
    low_voltage.setWriteEnabled(true);
    require(!low_voltage.applyDidChange(0xF1A0, {0x30, 0x40}).success,
            "coding must be blocked at unsafe voltage");

    CodingSession coding(uds, [] { return 13.4; });
    coding.setWriteEnabled(true);
    const auto direct_ok = coding.applyDidChange(0xF1A0, {0x55, 0x66});
    require(direct_ok.success, "safe direct coding transaction should succeed");
    require(direct_ok.backup == std::vector<std::uint8_t>({0x10, 0x20}),
            "direct coding transaction should preserve a backup");

    ecu.injectFault(VirtualEcuFault::CorruptWriteOnce);
    const auto rolled_back = coding.applyDidChange(0xF1A0, {0x77, 0x88});
    require(!rolled_back.success, "verification mismatch must fail the transaction");
    require(rolled_back.rollback_attempted, "verification mismatch must attempt rollback");
    require(rolled_back.rollback_succeeded, "rollback must be verified");
    require(ecu.getDid(0xF1A0) == std::vector<std::uint8_t>({0x55, 0x66}),
            "rollback must restore the previous coding value");

    // Stages 31-40: VIN / ECU / hardware / software identity gates.
    EcuIdentity actual{
        .vin = vin,
        .manufacturer = "VW",
        .model = "TestVehicle",
        .ecu_name = "BCM",
        .hardware_number = "HW-01",
        .software_number = "SW-01",
        .calibration_id = "CAL-01",
    };
    EcuIdentityPolicy identity_policy{
        .expected_vin = vin,
        .expected_manufacturer = "VW",
        .expected_ecu_name = "BCM",
        .expected_hardware_number = "HW-01",
        .expected_software_number = "SW-01",
    };
    require(looksLikeVin(vin), "test VIN should pass structural VIN validation");
    require(checkEcuIdentity(actual, identity_policy).allowed,
            "matching ECU identity must pass");
    auto wrong_identity = actual;
    wrong_identity.software_number = "SW-WRONG";
    require(!checkEcuIdentity(wrong_identity, identity_policy).allowed,
            "software mismatch must block coding identity gate");

    // Stages 41-50: coding definition schema and value validation.
    CodingProfileDefinition profile;
    profile.id = "test-bcm-profile";
    profile.manufacturer = "VW";
    profile.model = "TestVehicle";
    profile.identity_policy = identity_policy;
    profile.parameters.push_back(CodingParameterDefinition{
        .key = "test_feature",
        .display_name = "Test Feature",
        .did = 0xF1A0,
        .exact_length = 2,
        .required_session = 0x03,
        .writable = true,
        .requires_backup = true,
    });
    require(validateCodingProfile(profile).valid, "coding profile should validate");
    const auto* parameter = findCodingParameter(profile, "test_feature");
    require(parameter != nullptr, "coding parameter lookup should succeed");
    require(validateCodingValue(*parameter, {0x01, 0x02}),
            "correctly sized writable value should validate");
    require(!validateCodingValue(*parameter, {0x01}),
            "incorrect coding value length must be rejected");

    // Stages 51-65: append-only transaction journal + guarded orchestrator.
    const auto journal_path = std::filesystem::temp_directory_path() / "fg-prehardware-test.journal";
    std::error_code remove_ec;
    std::filesystem::remove(journal_path, remove_ec);
    TransactionJournal journal(journal_path);
    GuardedCodingEngine guarded(uds, [] { return 13.5; }, &journal);

    GuardedCodingRequest request;
    request.profile = &profile;
    request.actual_identity = actual;
    request.parameter_key = "test_feature";
    request.new_value = {0xA1, 0xB2};
    request.transaction_id = "tx-test-001";
    request.utc_timestamp = "2026-09-10T17:00:00Z";

    const auto globally_locked = guarded.execute(request);
    require(!globally_locked.success, "guarded coding must default to global write lock");

    guarded.setWriteEnabled(true);
    request.actual_identity = wrong_identity;
    const auto identity_blocked = guarded.execute(request);
    require(identity_blocked.blocked_by_identity,
            "guarded coding must block mismatched ECU software identity");

    request.actual_identity = actual;
    const auto guarded_ok = guarded.execute(request);
    require(guarded_ok.success, "guarded coding should succeed when every gate passes");
    require(ecu.getDid(0xF1A0) == request.new_value,
            "guarded coding should persist verified simulator value");

    ecu.injectFault(VirtualEcuFault::CorruptWriteOnce);
    request.new_value = {0xC3, 0xD4};
    request.transaction_id = "tx-test-rollback";
    const auto guarded_rollback = guarded.execute(request);
    require(!guarded_rollback.success, "guarded verification fault must fail transaction");
    require(guarded_rollback.coding.rollback_succeeded,
            "guarded verification fault must successfully restore backup");
    require(std::filesystem::exists(journal_path), "transaction journal should be created");
    require(std::filesystem::file_size(journal_path) > 0, "transaction journal should contain records");

    // Stages 66-70: explicit fault-injection responses must remain contained.
    ecu.injectFault(VirtualEcuFault::NegativeResponseOnce);
    bool saw_negative = false;
    try {
        (void)uds.readDataByIdentifier(0xF190);
    } catch (const UdsError&) {
        saw_negative = true;
    }
    require(saw_negative, "negative UDS response must surface as a controlled exception");

    ecu.injectFault(VirtualEcuFault::EmptyResponseOnce);
    bool saw_empty = false;
    try {
        (void)uds.readDataByIdentifier(0xF190);
    } catch (const UdsError&) {
        saw_empty = true;
    }
    require(saw_empty, "empty VCI response must surface as a controlled exception");

    std::filesystem::remove(journal_path, remove_ec);
    vci.close();
    std::cout << "FG_PREHARDWARE_STAGE80_TESTS_PASS\n";
    return 0;
}
