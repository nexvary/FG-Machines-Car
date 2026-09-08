# FG Machines Car — Stage 140000 Project Handoff

## Handoff status

Project status: `HANDOFF_TO_PROJECT_MAINTAINER`

This document is the continuation handoff for the next project maintainer.

## Verified software gates

- Stage 140000 source integrity audit
- Route/function audit: 159/159
- Native test suite: 40/40 on Linux release gate
- Windows release pipeline includes MSVC build, 40 native tests, self-test, Visual QA, installer packaging, and SHA-256 generation
- Transport archive is protected by SHA-256 verification before build

## Hardware continuation scope

The following physical validation work is transferred to the receiving maintainer for continuation:

1. Real VCI interface connection and protocol validation
2. Real vehicle / bench connection validation
3. CGDI K2 SDK and physical hardware integration validation
4. Document hardware/driver versions used during validation
5. Record reproducible test steps and results in the repository

These items are intentionally labeled as handoff scope rather than completed CI checks, because they require the physical hardware.

## Safety / operating mode

The current software release scope is READ ONLY diagnostics. Keep hardware testing isolated and controlled until protocol behavior is verified on bench hardware before any vehicle use.

## Release artifacts

The Windows Release Gate publishes, when all automated gates pass:

- `FG-Machines-Car-Setup.exe`
- `FG-Machines-Car-Stage140000-Screenshot.png`
- `visual-qa-screenshots.zip`
- `release-metadata.json`
- `HARDWARE-HANDOFF.md`
- `SHA256SUMS.txt`

## Recommended continuation order

1. Complete the current Windows Release Gate and preserve the successful artifact SHA-256.
2. Validate VCI drivers and enumeration on a dedicated Windows machine.
3. Run bench-level communication tests before connecting to a real vehicle.
4. Validate CGDI K2 SDK/device detection separately.
5. Add hardware-specific automated smoke checks where possible.
6. Only after repeatable bench validation, document supported hardware/vehicle combinations.
