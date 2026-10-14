"""Prototype acquisition loop; no network or relay control in v0.1."""
import time
from inputs import AnalogInputs, SimulatedInputs
from level import LevelChannel

# Set True to test without physical sensors.
SIMULATION = False
SAMPLE_INTERVAL_MS = 1000

def main():
    source = SimulatedInputs() if SIMULATION else AnalogInputs()
    channels = [
        LevelChannel(height_m=3.0, capacity_l=10000),
        LevelChannel(height_m=2.0, capacity_l=5000),
    ]
    while True:
        try:
            currents = source.read_ma()
            for index, (channel, current) in enumerate(zip(channels, currents)):
                result = channel.update(current)
                print("AI{}: {}".format(index + 1, result))
        except Exception as exc:
            # Do not turn acquisition failures into valid zero-level readings.
            print("ACQUISITION_ERROR:", repr(exc))
        time.sleep_ms(SAMPLE_INTERVAL_MS)

if __name__ == "__main__":
    main()
