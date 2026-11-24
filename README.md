# WiFi Tracker

A tiny coloured dot in your Windows system tray that tells you whether you actually have internet, not just whether you're connected to a router.

**Green** means the internet works.

**Yellow** means you're on a network, but the internet isn't getting through.

**Red** means no network at all.

Hover over the dot to see the status in words.

The Windows WiFi icon can show full bars while nothing loads. Yellow is the useful state here. It means the problem is past your router, so restarting your laptop's WiFi won't help.

It runs on Windows, needs no admin rights and no location permission, it never runs netsh, it doesn't read your network name, and it doesn't write anything to disk.

## Run

```bash
pip install -r requirements.txt
python main.py
```

The dot shows up red in the tray. Right-click it and choose **Start Monitoring**. From then on it checks every 2 seconds. **Stop Monitoring** pauses it and **Exit** closes it.

## Build an exe

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --name WiFiTracker main.py
```

You'll find it at `dist\WiFiTracker.exe`. Drop a shortcut to it in your Startup folder (press Win+R and type `shell:startup`) if you want it running every time you log in.

## How it decides the colour

**Is the internet reachable?** It tries to open a TCP connection to port 53 on Google DNS (8.8.8.8), Cloudflare (1.1.1.1) and Quad9 (9.9.9.9), one after another, with a one-second timeout each. If any of them answers, the dot is green. It only opens and closes the connection. No DNS query is ever sent.

**If not, is there a network at all?** It asks psutil whether any physical adapter is up with a link speed above zero, or has a real IPv4 address. Virtual adapters are skipped, so Hyper-V, WSL, VMware, VirtualBox, Docker, VPNs, Tailscale, ZeroTier, WireGuard and similar don't fool it into thinking you're connected. Addresses starting with 169.254 don't count either, since Windows gives itself one of those when it can't get a real address. If a real network is found the dot is yellow, otherwise red.

It never looks up the network name (SSID), because on recent versions of Windows that requires location permission.

## Files

```
main.py                         starts everything and connects the tray to the monitor
wifi_tracker/wifi_checker.py    the actual connectivity check
wifi_tracker/monitor.py         background thread that runs the check every 2 seconds
wifi_tracker/tray_icon.py       the tray dot, tooltip and menu
tests/                          unit tests
```

The monitor thread can be started and stopped from the menu as often as you like. It waits for any check that's still running before starting a new loop, and it throws away a result that comes back after you pressed Stop, so the dot never flips to a stale colour.

## Tests

```bash
python -m unittest
```

CI runs them on GitHub Actions for every push to main and every pull request. Dependency versions are pinned exactly in `requirements.txt`, and Dependabot opens pull requests when there's something newer.
