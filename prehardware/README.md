# FG Machines Car — Stage 141 Pre-Hardware Coding Core

This directory contains the first hardware-independent implementation for moving FG Machines Car from read-only diagnostics toward guarded coding capability.

## Implemented now

- `IVci` hardware abstraction.
- `VirtualVci` for ECU simulation without a physical adapter.
- UDS request core with DiagnosticSessionControl (0x10), ReadDataByIdentifier (0x22), WriteDataByIdentifier (0x2E), and TesterPresent (0x3E).
- Guarded coding transaction with write-lock default OFF, voltage window validation, mandatory backup, post-write verification, and verified rollback.
- Initial Windows J2534 adapter that dynamically loads a vendor Pass-Thru DLL and binds standard PassThru open/connect/read/write functions.
- Linux and Windows CI gates for the pre-hardware core.

## Safety state

Real-vehicle writing remains disabled by default. The coding layer must be explicitly unlocked by the application and should remain simulation/bench-only until a real VCI has passed the hardware qualification gate.

## Scanmatik 3 path

The planned Windows integration path is:

`FG Machines Car -> J2534Vci -> Scanmatik J2534 DLL -> Scanmatik 3 -> OBD-II -> ECU`

The initial adapter targets standard J2534 protocols. CAN-FD and DoIP vendor-specific/extended configuration will be enabled only after the actual Scanmatik driver package and hardware are available for validation.

## Next pre-hardware milestones

1. Add J2534 registry discovery and device profile selection.
2. Add ISO-TP addressing profiles and response filtering.
3. Add ECU identity/VIN/software-version guards.
4. Add Coding Definition database schema.
5. Add transaction journal and persistent backup format.
6. Add SecurityAccess plug-in interface without embedding OEM secrets.
7. Add RoutineControl/ECUReset/communication-control primitives.
8. Add a richer Virtual ECU fault-injection suite.
9. Add a hardware qualification executable for the day the VCI arrives.

No ECU firmware flashing is enabled in this stage.
