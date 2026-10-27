import time
import unittest
from unittest import mock

from wifi_tracker import monitor
from wifi_tracker.wifi_checker import ConnectivityDetector, WiFiState


class DetectorTest(unittest.TestCase):
    def test_states(self):
        d = ConnectivityDetector()
        for internet, network, expected in [
            (True, False, WiFiState.ONLINE),
            (False, True, WiFiState.CHECKING),
            (False, False, WiFiState.DISCONNECTED),
        ]:
            with mock.patch.object(d, "_check_internet", return_value=internet), \
                 mock.patch.object(d, "_has_active_network", return_value=network):
                self.assertEqual(d.detect(), expected)

    def test_virtual_filter(self):
        d = ConnectivityDetector()
        self.assertTrue(d._is_virtual("vEthernet (WSL)"))
        self.assertFalse(d._is_virtual("Wi-Fi"))

    def test_internet_check_fails_cleanly(self):
        with mock.patch("socket.create_connection", side_effect=OSError):
            self.assertFalse(ConnectivityDetector()._check_internet())


class MonitorTest(unittest.TestCase):
    def test_start_stop_restart(self):
        updates = []
        m = monitor.Monitor(updates.append)
        with mock.patch.object(m._detector, "detect", return_value=WiFiState.ONLINE), \
             mock.patch.object(monitor, "POLL_INTERVAL", 0.01):
            for _ in range(2):
                m.start()
                time.sleep(0.05)
                self.assertTrue(m.is_active)
                m.stop()
                self.assertFalse(m.is_active)
                count = len(updates)
                time.sleep(0.05)
                self.assertEqual(len(updates), count)  # no updates after stop
        self.assertIn(WiFiState.ONLINE, updates)


if __name__ == "__main__":
    unittest.main()
