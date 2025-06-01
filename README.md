Turn any folder into a browsable, QR-scannable download page.

## Installation

Save the script as `quickshare.py` and make it executable:
```bash
chmod +x quickshare.py
```

## Basic Usage

```bash
# Share current directory on port 8000
./quickshare.py

# Share a specific folder
./quickshare.py ~/Downloads

# Use a different port
./quickshare.py -p 3000

# Force a specific IP address
./quickshare.py --ip 192.168.1.42

# Serve over HTTPS with self-signed cert
./quickshare.py --tls

# Combine options (HTTPS on port 80)
sudo ./quickshare.py --tls -p 80
```

## Features

- **QR Code**: Automatically displays a QR code for easy mobile access
- **HTTPS Support**: Use `--tls` for encrypted connections
- **Auto IP Detection**: Finds your LAN IP automatically
- **Simple Interface**: Clean file browser interface
- **Cross-Platform**: Works on macOS, Linux, and Windows

## QR Code Dependencies (Optional)

For QR code display, install one of:
```bash
pip install qrcode        # Python QR library
brew install qrencode     # Command-line tool (macOS)
```

Press **Ctrl-C** to stop the server.
