import signal
from wifi_tracker.tray_icon import TrayApp
from wifi_tracker.monitor import Monitor
from wifi_tracker.wifi_checker import WiFiState


class App:
    def __init__(self):
        self.monitor = Monitor(on_status_update=self._on_update)
        self.tray = TrayApp(
            on_start=self._start,
            on_stop=self._stop,
            on_exit=self._exit,
        )
        signal.signal(signal.SIGINT, lambda s, f: self._exit())
        signal.signal(signal.SIGTERM, lambda s, f: self._exit())

    def _on_update(self, state):
        self.tray.update(state)

    def _start(self, icon=None, item=None):
        self.tray.set_monitoring(True)
        self.monitor.start()

    def _stop(self, icon=None, item=None):
        self.monitor.stop()
        self.tray.set_monitoring(False)
        self.tray.update(WiFiState.DISCONNECTED)

    def _exit(self, icon=None, item=None):
        self.monitor.shutdown()
        self.tray.stop()  # makes tray.run() return, so the process exits normally

    def run(self):
        self.tray.run()


if __name__ == "__main__":
    App().run()
