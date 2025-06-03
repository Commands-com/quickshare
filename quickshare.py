#!/usr/bin/env python3
"""
quickshare  —  turn any folder into a browsable, QR-scannable download page.

Tested on MacOS.

Usage examples
--------------
# Share current directory on port 8000 (default)
quickshare

# Force Wi-Fi IP and use port 80 (stays plain HTTP on phones)
sudo quickshare --ip 192.168.1.42 -p 80

# Serve ~/Downloads over HTTPS with a throw-away cert
quickshare ~/Downloads --tls
"""
import argparse, http.server, os, socket, socketserver, ssl, subprocess, sys, tempfile, pathlib, time

# ---------- helpers ----------------------------------------------------------
def lan_ip() -> str:
    """Best-effort, cross-platform non-loopback IPv4."""
    # 1) UDP trick to public IP (no packets leave the host)
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except OSError:
        pass
    # 2) Walk interface addresses
    for info in socket.getaddrinfo(socket.gethostname(), None, socket.AF_INET):
        ip = info[4][0]
        if not ip.startswith(("127.", "0.")):
            return ip
    # 3) Fallback
    return "127.0.0.1"

def maybe_print_qr(url: str) -> None:
    """ASCII QR via `qrcode` or `qrencode`; else text fallback."""
    try:
        import qrcode
        qrcode.QRCode(border=1, box_size=1).add_data(url)
        qrcode.make().print_ascii(invert=True)
    except ModuleNotFoundError:
        if os.system("command -v qrencode >/dev/null") == 0:
            os.system(f'qrencode -t ANSI256 "{url}"')
        else:
            print(f"(Install `pip install qrcode` or `brew install qrencode` for a QR code)\n{url}")

def make_temp_cert() -> pathlib.Path:
    """Create a 24-hour self-signed cert and return its path."""
    pem = pathlib.Path(tempfile.gettempdir()) / "quickshare.pem"
    if pem.exists() and (time.time() - pem.stat().st_mtime) < 86400:  # <24 h old
        return pem
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048", "-days", "1",
            "-nodes", "-subj", "/CN=quickshare.local",
            "-keyout", pem, "-out", pem,
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    return pem

# ---------- main -------------------------------------------------------------
def main() -> None:
    p = argparse.ArgumentParser(
        description="Instantly share a directory over your LAN (QR included)."
    )
    p.add_argument("dir", nargs="?", default=".", help="Directory to share (default: .)")
    p.add_argument("-p", "--port", type=int, default=8000, help="Port to bind (default: 8000)")
    p.add_argument("--ip", help="Force a specific LAN IP")
    p.add_argument("--tls", action="store_true", help="Serve over HTTPS with a self-signed cert")
    args = p.parse_args()

    ip = args.ip or lan_ip()
    scheme = "https" if args.tls else "http"
    url = f"{scheme}://{ip}{'' if args.port in (80, 443) else f':{args.port}'}/"

    maybe_print_qr(url)

    os.chdir(args.dir)
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", args.port), handler) as httpd:
        if args.tls:
            cert = make_temp_cert()
            # Use modern SSL context instead of deprecated wrap_socket
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(str(cert))
            httpd.socket = context.wrap_socket(httpd.socket, server_side=True)
        print(f"\n📡  Sharing '{os.path.abspath(args.dir)}' → {url}")
        print("Press Ctrl-C to stop.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n👋  Done.")

if __name__ == "__main__":
    if sys.version_info < (3, 8):
        sys.exit("Python 3.8+ required")
    main()
