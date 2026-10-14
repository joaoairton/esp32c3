"""ECM50 analog input adapter. Pin mapping based on 02_Sources/AI.py."""
try:
    from machine import ADC, Pin
except ImportError:
    ADC = None
    Pin = None

class AnalogInputs:
    def __init__(self):
        if ADC is None:
            raise RuntimeError("Hardware ADC requires MicroPython")
        self.channels = [ADC(Pin(6)), ADC(Pin(7))]
        for channel in self.channels:
            channel.atten(ADC.ATTN_11DB)

    def read_ma(self):
        # Vendor example: voltage in microvolts / 150 ohms / 1000 = mA.
        # Must verify resistor value and calibrate against a reference.
        return [channel.read_uv() / 150000.0 for channel in self.channels]

class SimulatedInputs:
    def __init__(self):
        self.index = 0
        self.samples = [(4.0, 20.0), (8.0, 16.0), (12.0, 12.0),
                        (16.0, 8.0), (20.0, 4.0), (3.2, 22.0)]
    def read_ma(self):
        value = self.samples[self.index % len(self.samples)]
        self.index += 1
        return value
