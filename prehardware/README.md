# FG Machines Car — Pre-Hardware Coding Core through Stage 80

This directory is the hardware-independent foundation for moving FG Machines Car from read-only diagnostics toward guarded ECU coding. It is intentionally isolated from the stable Stage 140000 release until real VCI and bench qualification are complete.

## Stage map

| Range | Delivered capability |
| --- | --- |
| 2–10 | VCI abstraction, Windows J2534 dynamic adapter, installed J2534 registry discovery, ISO-TP addressing/profile validation |
| 11–20 | reusable Virtual VCI/Virtual ECU transport, CAN/ISO-TP profile safety checks |
| 21–30 | UDS request core: sessions, ECU reset, DID read/write, RoutineControl, DTC read/clear, TesterPresent |
| 31–40 | VIN/ECU/manufacturer/hardware/software identity guards |
| 41–50 | coding profile and parameter definition schema, duplicate/length/read-only validation |
| 51–60 | append-only transaction journal, backup value recording, deterministic state names |
| 61–70 | guarded coding orchestrator plus Virtual ECU fault injection for empty, negative, rejected and corrupted writes |
| 71–80 | Linux/Windows build and test gate, read-only J2534 qualification CLI, Scanmatik-ready integration path |

## Safety state

Real-vehicle writing remains disabled by default. There are two independent write locks: the low-level `CodingSession` lock and the higher-level `GuardedCodingEngine` lock. A coding request must also pass voltage, coding-definition, VIN/ECU identity, hardware-number and software-number checks before a write can be issued.

The coding transaction captures a backup before writing, reads the value back after writing, and attempts a verified rollback if post-write verification fails. The transaction journal records planned, backup, verified, rollback and failed states.

## Scanmatik 3 / J2534 path

The intended Windows path is:

`FG Machines Car -> GuardedCodingEngine -> UDS -> J2534Vci -> vendor Pass-Thru DLL -> VCI -> OBD-II -> ECU`

`discoverJ2534Devices()` enumerates installed SAE J2534 04.04 providers from the Windows registry. The supplied `fg_j2534_qualify` executable is read-only and is intended for the day hardware arrives:

- `fg_j2534_qualify --list` lists detected Pass-Thru providers.
- `fg_j2534_qualify <dll> <tx_id> <rx_id> [baud]` opens the interface, enters the default diagnostic session and reads VIN DID `F190` only.

## Test coverage at Stage 80

The automated suite exercises ISO-TP configuration rejection, Virtual VCI/ECU transport, expanded UDS services, global and low-level write locks, unsafe-voltage rejection, backup, verification, rollback, VIN/ECU identity mismatch, coding profile validation, value-length rejection, journal persistence, and injected negative/empty/corrupt responses.

## Still hardware-dependent

The following cannot be truthfully marked complete before physical hardware arrives:

- vendor driver installation and real J2534 enumeration;
- CAN/CAN-FD/DoIP/K-Line electrical/protocol validation;
- timing and reconnect behavior on a real VCI;
- bench ECU identity and DID verification;
- manufacturer-specific coding definitions and authorized security-access implementations;
- any real-vehicle coding write.

No ECU firmware flashing/programming is enabled in this stage. Manufacturer security algorithms or secrets are not embedded in the repository.
