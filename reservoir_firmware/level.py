"""Pure measurement logic for 4-20 mA reservoir transmitters."""
from math import isfinite

class LevelChannel:
    def __init__(self, height_m, capacity_l, alpha=0.25, fault_low_ma=3.6,
                 fault_high_ma=21.0):
        if height_m <= 0 or capacity_l <= 0:
            raise ValueError("height_m and capacity_l must be positive")
        if not 0 < alpha <= 1:
            raise ValueError("alpha must be in (0, 1]")
        self.height_m = height_m
        self.capacity_l = capacity_l
        self.alpha = alpha
        self.fault_low_ma = fault_low_ma
        self.fault_high_ma = fault_high_ma
        self.filtered_ma = None

    def update(self, current_ma):
        if not isfinite(current_ma):
            return self._result("invalid_reading", None)
        if current_ma < self.fault_low_ma:
            return self._result("under_range", current_ma)
        if current_ma > self.fault_high_ma:
            return self._result("over_range", current_ma)
        if current_ma < 4.0 or current_ma > 20.0:
            return self._result("out_of_calibrated_range", current_ma)
        if self.filtered_ma is None:
            self.filtered_ma = current_ma
        else:
            self.filtered_ma += self.alpha * (current_ma - self.filtered_ma)
        percent = (self.filtered_ma - 4.0) * 100.0 / 16.0
        percent = max(0.0, min(100.0, percent))
        return {
            "status": "ok", "current_ma": round(current_ma, 3),
            "filtered_ma": round(self.filtered_ma, 3),
            "level_percent": round(percent, 2),
            "level_m": round(self.height_m * percent / 100.0, 3),
            "volume_l": round(self.capacity_l * percent / 100.0, 1),
        }

    def _result(self, status, current):
        return {"status": status, "current_ma": current,
                "filtered_ma": None, "level_percent": None,
                "level_m": None, "volume_l": None}
