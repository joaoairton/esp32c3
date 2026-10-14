# Reservoir Monitor — firmware prototype v0.1

Isolated prototype for the EBYTE ECM50-A07, based on the vendor MicroPython examples in `02_Sources`. This is **not yet a validated production firmware**.

## Included
- Two 4–20 mA inputs (AI1/AI2) via GPIO 6 and 7, per `02_Sources/AI.py`.
- Raw current conversion following the vendor example (`read_uv() / 150000`).
- Per-channel first-order filter, level percentage, height and volume for constant-cross-section tanks.
- Explicit fault states for currents below 3.6 mA, above 21 mA, outside 4–20 mA calibration, and nonfinite readings.
- Simulation source and CPython unit tests.
- No relays, pump control, cloud, or credentials.

## Testing without hardware
Run `python -m unittest discover -s reservoir_firmware/tests -v` from repository root. On MicroPython, upload `level.py`, `inputs.py`, `main.py` to the device filesystem and set `SIMULATION = True` in `main.py`.

## Hardware test
Confirm firmware build, ADC pins, actual shunt resistor, input wiring and loop power against the ECM50-A07 manual. Set `SIMULATION = False` only after verification. Use a calibrated current source at 4, 12 and 20 mA and compare reported values; do not connect an unverified field loop.

## Limitations / next steps
- Volume calculation assumes a tank with constant cross-section; non-linear tanks require a geometry table.
- No per-channel two-point ADC calibration, median filtering, persistent settings, logging, MQTT/TLS or OTA yet.
- Fault thresholds are initial design assumptions, not a certified diagnostic standard.
- Fault values are never represented as valid zero level. A future deployment must also define stale-data handling and watchdog behavior.
