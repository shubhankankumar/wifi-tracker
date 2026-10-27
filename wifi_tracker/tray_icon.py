import threading
from PIL import Image, ImageDraw
import pystray


COLORS = {
    "online": (0, 210, 0),
    "checking": (240, 190, 0),
    "disconnected": (230, 30, 30),
}

LABELS = {
    "online": "Connected",
    "checking": "No Internet",
    "disconnected": "Disconnected",
}

ICON_SIZE = 16
DOT_RADIUS = 6


def _make_icon(status):
    rgb = COLORS.get(status, COLORS["disconnected"])
    img = Image.new("RGBA", (ICON_SIZE, ICON_SIZE), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    c = ICON_SIZE // 2
    r = DOT_RADIUS
    draw.ellipse([c - r, c - r, c + r, c + r], fill=rgb)
    return img


ICONS = {status: _make_icon(status) for status in COLORS}  # drawn once, reused on every update


class TrayApp:
    def __init__(self, on_start, on_stop, on_exit):
        self.icon = None
        self.on_start = on_start
        self.on_stop = on_stop
        self.on_exit = on_exit
        self._monitoring = False
        self._state = "disconnected"
        self._last_key = None
        self._lock = threading.Lock()  # update() is called from the monitor thread and the UI thread

    def _menu(self):
        return pystray.Menu(
            pystray.MenuItem("Start Monitoring", self.on_start,
                             enabled=lambda _: not self._monitoring),
            pystray.MenuItem("Stop Monitoring", self.on_stop,
                             enabled=lambda _: self._monitoring),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Exit", self.on_exit),
        )

    def update(self, state):
        with self._lock:
            self._state = state
            key = (state, self._monitoring)
            if self.icon is None or self._last_key == key:
                return
            self._last_key = key
            label = LABELS.get(state, state)
            try:
                self.icon.icon = ICONS.get(state, ICONS["disconnected"])
                self.icon.title = f"WiFi: {label}\nMonitoring: {'ON' if self._monitoring else 'OFF'}"
            except Exception:
                pass

    def set_monitoring(self, active):
        self._monitoring = active
        if self.icon:
            try:
                self.icon.update_menu()  # only the Start/Stop enabled state depends on this
            except Exception:
                pass
        self.update(self._state)

    def run(self):
        self.icon = pystray.Icon("wifi_tracker", ICONS["disconnected"],
                                 "WiFi: Disconnected\nMonitoring: OFF", self._menu())
        self.icon.run()

    def stop(self):
        if self.icon:
            try:
                self.icon.stop()
            except Exception:
                pass
