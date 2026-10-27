import threading
from .wifi_checker import ConnectivityDetector, WiFiState


POLL_INTERVAL = 2


class Monitor:
    def __init__(self, on_status_update):
        self._detector = ConnectivityDetector()
        self._on_status_update = on_status_update
        self._thread = None
        self._stop_event = threading.Event()
        self._lock = threading.Lock()

    @property
    def is_active(self):
        return self._thread is not None and self._thread.is_alive() and not self._stop_event.is_set()

    def start(self):
        with self._lock:
            if self.is_active:
                return
            # A previous thread may still be finishing a check; wait so two loops never run.
            if self._thread and self._thread.is_alive():
                self._thread.join()
            self._stop_event = threading.Event()
            self._thread = threading.Thread(target=self._loop, args=(self._stop_event,),
                                            daemon=True, name="WiFiMonitor")
            self._thread.start()

    def stop(self):
        with self._lock:
            self._stop_event.set()
            if self._thread and self._thread.is_alive():
                self._thread.join(timeout=5)

    shutdown = stop

    def _loop(self, stop_event):
        while not stop_event.is_set():
            try:
                state = self._detector.detect()
            except Exception:
                state = WiFiState.DISCONNECTED
            # Don't report a result that finished after the user pressed Stop.
            if stop_event.is_set():
                break
            self._on_status_update(state)
            stop_event.wait(timeout=POLL_INTERVAL)
