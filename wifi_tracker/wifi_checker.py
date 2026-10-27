import socket
import psutil


class WiFiState:
    ONLINE = "online"
    CHECKING = "checking"
    DISCONNECTED = "disconnected"


INTERNET_TARGETS = [
    ("8.8.8.8", 53),
    ("1.1.1.1", 53),
    ("9.9.9.9", 53),
]

CONNECT_TIMEOUT = 1.0

VIRTUAL_KEYWORDS = [
    "vethernet",
    "hyper-v",
    "wsl",
    "vmware",
    "virtualbox",
    "loopback",
    "docker",
    "zerotier",
    "tailscale",
    "virtual",
    "tunnel",
    "tap",
    "vpn",
    "ndis",
    "wintun",
    "wireguard",
    "openvpn",
]


class ConnectivityDetector:
    def detect(self):
        if self._check_internet():
            return WiFiState.ONLINE
        if self._has_active_network():
            return WiFiState.CHECKING
        return WiFiState.DISCONNECTED

    def _check_internet(self):
        for host, port in INTERNET_TARGETS:
            try:
                with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT):
                    return True
            except OSError:
                continue
        return False

    def _is_virtual(self, name):
        lower = name.lower()
        return any(kw in lower for kw in VIRTUAL_KEYWORDS)

    def _has_active_network(self):
        try:
            for name, info in psutil.net_if_stats().items():
                if not self._is_virtual(name) and info.isup and info.speed > 0:
                    return True
        except Exception:
            pass

        try:
            for name, addr_list in psutil.net_if_addrs().items():
                if self._is_virtual(name):
                    continue
                for addr in addr_list:
                    if addr.family == socket.AF_INET and addr.address and not addr.address.startswith("127."):
                        return True
        except Exception:
            pass

        return False
