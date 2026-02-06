# iwscan

A simple Python script that parses the output of the `iw` command and exposes WiFi network data as Prometheus metrics.

![iwscan grafana](https://user-images.githubusercontent.com/2038195/236711840-6d818868-b787-4f71-935d-475c5d25bb57.png)

## Use Cases

- Detect polluting WiFi networks or interference
- Select optimal channels for your access points
- Monitor signal strength over time

## Setup

### Docker Compose (Recommended)

```yaml
services:
  iwscan:
    build: .
    privileged: true
    network_mode: host
    restart: unless-stopped
    environment:
      - INTERFACE=wlan0
      - PORT=5024
```

```bash
docker compose up -d
```

### Docker Run

```bash
docker run -d --privileged --network host \
  -e INTERFACE=wlan0 \
  -e PORT=5024 \
  alexlepape/iwscan:latest
```

### Direct

```bash
# Default: wlan0, port 5024
sudo python3 iwscan.py

# Custom interface and port
sudo python3 iwscan.py -i wlan1 -p 8080
```

Note: `sudo` may be required depending on your setup.

## Configuration

| Environment Variable | CLI Flag | Default | Description |
|---------------------|----------|---------|-------------|
| `INTERFACE` | `-i, --interface` | `wlan0` | WiFi interface to scan |
| `PORT` | `-p, --port` | `5024` | HTTP server port |

## Prometheus Integration

Add to your `prometheus.yml`:

```yaml
scrape_configs:
  - job_name: 'wifiscan'
    static_configs:
      - targets: ['<RPI_IP>:5024']
```

## Grafana

An example dashboard is available in [grafana.json](grafana.json).

## Requirements

- Docker needs `privileged: true` and `network_mode: host` to access WiFi hardware
- The `iw` command must be available (included in Docker image)
- Typically used on Raspberry Pi with ethernet as primary connection, leaving WiFi free for scanning