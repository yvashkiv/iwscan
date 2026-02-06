#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, HTTPServer
import re
import subprocess
import argparse

# Precompiled regex patterns
PATTERNS = {
    'bss': re.compile(r'^BSS ([0-9a-f]{2}(?:[:-][0-9a-f]{2}){5})'),
    'ssid': re.compile(r'^\tSSID: (.*)'),
    'signal': re.compile(r'^\tsignal: ([\d.-]+)'),
    'freq': re.compile(r'^\tfreq: (\d+)'),
    'channel': re.compile(r'^[\s\t]*\* primary channel: (\d+)'),
}

DEFAULT_PORT = 5024
DEFAULT_INTERFACE = 'wlan0'


def parse_iw_scan(iw_output: str) -> dict:
    """Parse iw scan output into structured dict."""
    networks = {}
    current_bss = None

    for line in iw_output.splitlines():
        if match := PATTERNS['bss'].match(line):
            current_bss = match.group(1)
            networks[current_bss] = {}
            continue

        if current_bss is None:
            continue

        for field in ('ssid', 'signal', 'freq', 'channel'):
            if match := PATTERNS[field].match(line):
                networks[current_bss][field] = match.group(1)
                break

    return networks


def to_prometheus_format(networks: dict) -> str:
    """Convert parsed networks to Prometheus text format."""
    lines = [
        "# HELP wifi_ssids All scanned SSIDs with their signal quality.",
        "# TYPE wifi_ssids gauge",
    ]

    for mac, data in networks.items():
        ssid = data.get('ssid', '')
        freq = data.get('freq', '')
        channel = data.get('channel', '?')
        signal = data.get('signal', '0')

        lines.append(
            f'wifi_ssids{{mac="{mac}",ssid="{ssid}",freq="{freq}",channel="{channel}"}} {signal}'
        )

    return '\n'.join(lines) + '\n'


def scan_wifi(interface: str = DEFAULT_INTERFACE) -> str:
    """Execute iw scan and return output."""
    result = subprocess.run(
        ['iw', interface, 'scan'],
        capture_output=True,
        text=True,
    )
    return result.stdout


class MetricsHandler(BaseHTTPRequestHandler):
    interface = DEFAULT_INTERFACE

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def _send_response(self, content: str, status: int = 200):
        self.send_response(status)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()
        self.wfile.write(content.encode('utf-8'))

    def do_GET(self):
        iw_output = scan_wifi(self.interface)
        networks = parse_iw_scan(iw_output)
        metrics = to_prometheus_format(networks)
        self._send_response(metrics)

    def do_HEAD(self):
        self.send_response(200)
        self.send_header('Content-Type', 'text/plain; charset=utf-8')
        self.end_headers()


def main():
    parser = argparse.ArgumentParser(description='WiFi scan Prometheus exporter')
    parser.add_argument('-p', '--port', type=int, default=DEFAULT_PORT,
                        help=f'Port to listen on (default: {DEFAULT_PORT})')
    parser.add_argument('-i', '--interface', default=DEFAULT_INTERFACE,
                        help=f'WiFi interface (default: {DEFAULT_INTERFACE})')
    args = parser.parse_args()

    MetricsHandler.interface = args.interface

    server = HTTPServer(('', args.port), MetricsHandler)
    print(f'Starting server on port {args.port} (interface: {args.interface})')
    server.serve_forever()


if __name__ == '__main__':
    main()