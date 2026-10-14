"""Run with CPython: python -m unittest discover -s reservoir_firmware/tests"""
import os
import sys
import unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from level import LevelChannel

class TestLevelChannel(unittest.TestCase):
    def setUp(self):
        self.channel = LevelChannel(5.0, 10000.0, alpha=1.0)

    def test_endpoints_and_midpoint(self):
        for current, expected in ((4, 0), (12, 50), (20, 100)):
            self.assertEqual(self.channel.update(current)["level_percent"], expected)

    def test_faults_have_no_level(self):
        for current in (3.2, 21.5, 3.8, 20.5, float("nan")):
            result = self.channel.update(current)
            self.assertIsNone(result["level_percent"])
            self.assertNotEqual(result["status"], "ok")

    def test_volume(self):
        self.assertEqual(self.channel.update(12)["volume_l"], 5000.0)

    def test_filter(self):
        channel = LevelChannel(5, 10000, alpha=0.5)
        channel.update(4)
        self.assertEqual(channel.update(12)["level_percent"], 25.0)

if __name__ == "__main__":
    unittest.main()
