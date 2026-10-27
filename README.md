# WiFi Tracker

Permission-free Windows tray WiFi monitor. No location services, no admin, no netsh, no logging.

## Colors
- **Green** = Internet reachable
- **Yellow** = Network active but no internet
- **Red** = No network connection

## How it works
1. **Internet check**: TCP connect to DNS servers (8.8.8.8:53, 1.1.1.1:53)
2. **Network check**: `psutil` reads physical interface status (virtual adapters filtered out)
3. No SSID, no location services, no admin, no disk writes

## Run
```bash
pip install -r requirements.txt
python main.py
```

## Build EXE
```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name WiFiTracker main.py
```
Output: `dist\WiFiTracker.exe`

## Test
```bash
python -m unittest
```

## Files
```
main.py                     - Entry point (wires tray + monitor)
wifi_tracker/monitor.py     - Polling thread (start/stop, thread-safe)
wifi_tracker/wifi_checker.py - Connectivity detection (psutil + socket)
wifi_tracker/tray_icon.py   - System tray dot + menu + tooltip
tests/                      - Unit tests
```
