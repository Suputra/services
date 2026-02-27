# Services on Tower (10.0.0.100)

This repository contains all home server service configurations, code, and setup documentation.

## Network Overview

```
                    Internet
                        |
                    [Router]
                    10.0.1.1
                        |
        +---------------+---------------+
        |               |               |
    [Pi-hole]       [Tower]         [Other
    10.0.0.10      10.0.0.100       devices]
    DNS server      This machine
```

**DNS Resolution**: All devices on the network use Pi-hole (10.0.0.10) for DNS. Custom `.y` domains are resolved via `/etc/hosts` on the Pi.

---

## Go-Links System

Short URLs like `y/pad` redirect to services via nginx.

**How it works**:
1. Browser requests `y/pad`
2. Pi-hole DNS resolves `y` -> `10.0.0.100`
3. nginx catches `y/<app>` and redirects to `<app>.y`
4. Pi-hole resolves `<app>.y` -> `10.0.0.100`
5. nginx proxies to the actual service

**Config files**:
- nginx: `/etc/nginx/sites-available/golinks` (copy in `go-links/golinks.nginx.conf`)
- DNS (on Pi): `/etc/hosts`

**Available go-links**:
| Link | Domain | Service | Backend |
|------|--------|---------|---------|
| `y/pics` | `pics.y` | Immich | `10.0.0.100:2283` (docker) |
| `y/pad` | `pad.y` | Collaborative Pad | `127.0.0.1:8000` (systemd) |
| `y/router` | `router.y` | Router admin | `10.0.0.1` (redirect) |
| `y/pihole` | `pihole.y` | Pi-hole admin | `10.0.0.10:8080` (redirect) |
| `y/wiki` | `wiki.y` | Wikipedia | `wikipedia.org` (redirect) |
| `y/admin` | `admin.y` | Link directory | CGI script |
| `y/cam` | `cam.y` | Camera Stream | `10.0.0.100:8100` (systemd user) |

---

## Services

### Pad (Collaborative Notepad)
Real-time shared notepad with file sharing.

- **URL**: `y/pad` or `pad.y`
- **Port**: 8000
- **Tech**: Python/FastAPI + WebSockets
- **Files**:
  - App: `pad/pad.py`
  - Uploads: `pad/media/`
  - Service: `/etc/systemd/system/pad.service`
- **Commands**:
  ```bash
  sudo systemctl status pad
  sudo systemctl restart pad
  sudo journalctl -u pad -f
  ```

### Immich (Photo Management)
Self-hosted Google Photos alternative.

- **URL**: `y/pics` or `pics.y`
- **Port**: 2283
- **Tech**: Docker Compose
- **Files**:
  - Compose: `immich/docker-compose.yml`
  - Library: `/mnt/merged/immich/library`
  - Database: `/mnt/fast/immich-postgres`
- **Containers**:
  - `immich_server` - Main app
  - `immich_machine_learning` - ML/face recognition
  - `immich_postgres` - Database
  - `immich_redis` - Cache
- **Commands**:
  ```bash
  cd ~/services/immich && docker compose ps
  cd ~/services/immich && docker compose logs -f
  cd ~/services/immich && docker compose restart
  ```

### Minecraft Server (Modded)
Modded Minecraft server.

- **Ports**: 25565 (game), 25575 (RCON)
- **Files**:
  - Scripts & config: `minecraft-server/`
  - Runtime data: `/home/saahas/minecraft-server/` (world, mods, jars - not in repo)
  - Service: `/etc/systemd/system/minecraft-server.service`
- **Commands**:
  ```bash
  sudo systemctl status minecraft-server
  sudo systemctl restart minecraft-server
  sudo journalctl -u minecraft-server -f
  # RCON commands:
  ~/services/minecraft-server/mc
  ```

### BOINC + Science United
Distributed volunteer compute with adjustable effort profiles.

- **Status**: Active service, ready for Science United account attach
- **Service**: `boinc-client` (systemd)
- **Data dir**: `/var/lib/boinc-client/`
- **Local prefs override**: `/etc/boinc-client/global_prefs_override.xml`
- **Control scripts**: `boinc/boinc-effort`, `boinc/boinc-science-united-attach`
  (installed to `/usr/local/bin/`)
- **Effort profiles**:
  - `low` - reduced heat/load
  - `medium` - balanced default
  - `high` - max heat/load
  - `pause`/`resume` - immediate stop/start
  - `for <minutes>` - temporary pause timer
- **Commands**:
  ```bash
  # service
  sudo systemctl status boinc-client
  sudo systemctl restart boinc-client
  sudo journalctl -u boinc-client -f

  # effort controls
  boinc-effort status
  boinc-effort low
  boinc-effort medium
  boinc-effort high
  boinc-effort pause
  boinc-effort resume
  boinc-effort for 90
  boinc-effort custom 50 75 50

  # attach/sync Science United
  boinc-science-united-attach
  sudo boinccmd --acct_mgr info
  sudo boinccmd --acct_mgr sync

  # work/status checks
  sudo boinccmd --get_project_status
  sudo boinccmd --get_task_summary
  sudo boinccmd --get_messages 0 | tail -n 80
  ```

### Folding@home (currently disabled)
Fallback distributed computing service (stopped + disabled at boot).

- **Service**: `fah-client`
- **Port**: 7396 (local web UI at `localhost:7396`)
- **Config**: `/etc/fah-client/config.xml`
- **Logs**: `/var/log/fah-client/`
- **Commands**:
  ```bash
  sudo systemctl status fah-client
  sudo systemctl start fah-client
  sudo systemctl stop fah-client
  sudo systemctl enable fah-client
  sudo systemctl disable fah-client
  ```

### Camera Mux (IP Camera Relay)
Persistent MJPEG relay that keeps the DroidCam phone camera alive.

- **URL**: `y/cam` or `cam.y`
- **Port**: 8100
- **Source**: `http://10.0.44.199:4747/video?640x480` (DroidCam)
- **Tech**: Python/OpenCV + http.server (systemd user service)
- **Files**:
  - App: `camera/camera_mux.py`
  - Service: `~/.config/systemd/user/camera-mux.service`
- **Endpoints**:
  - `/` - Live stream page (cam.y frontend)
  - `/frame` - Single JPEG snapshot
  - `/stream` - MJPEG stream (for OpenCV / browser)
  - `/health` - JSON status
- **Commands**:
  ```bash
  systemctl --user status camera-mux
  systemctl --user restart camera-mux
  journalctl --user -u camera-mux -f
  curl localhost:8100/health
  ```

### GNOME Remote Desktop
RDP access to desktop.

- **Port**: 3389
- **Service**: `gnome-remote-desktop.service`

---

## nginx

Reverse proxy handling all `.y` domains.

- **Config**: `/etc/nginx/sites-available/golinks` (copy in `go-links/golinks.nginx.conf`)
- **Enabled**: `/etc/nginx/sites-enabled/golinks`
- **SSL certs**: `/etc/nginx/ssl/golinks.{crt,key}`
- **Commands**:
  ```bash
  sudo nginx -t                    # test config
  sudo systemctl reload nginx      # apply changes
  sudo journalctl -u nginx -f      # logs
  ```

---

## Storage

| Mount | Device | Size | Purpose |
|-------|--------|------|---------|
| `/` | `/dev/sda2` | 219G | System |
| `/mnt/fast` | `/dev/nvme0n1p1` | 469G | Fast storage (NVMe) |
| `/mnt/media` | `/dev/sdb1` | 915G | Media files |
| `/mnt/storage` | `/dev/sdc1` | 3.6T | Bulk storage |
| `/mnt/merged/immich` | mergerfs pool | 4.5T | Immich library (spans storage+media) |

---

## Raspberry Pi (10.0.0.10)

The Pi runs Pi-hole for network-wide DNS and ad-blocking, and a WireGuard VPN server for remote access.

- **SSH**: `ssh pi`
- **DNS entries**: `/etc/hosts` (custom `.y` domains)
- **Pi-hole admin**: `y/pihole` or `10.0.0.10:8080/admin`
- **Reload DNS**: `ssh pi "sudo pihole reloaddns"`

### WireGuard VPN
Remote access to the home network via PiVPN.

- **Port**: 51820/UDP (forward on router to 10.0.0.10)
- **Subnet**: `10.207.102.0/24`
- **Config**: `/etc/wireguard/wg0.conf`
- **Service**: `wg-quick@wg0`
- **Peers**:
  | Name | IP |
  |------|----|
  | iphone | `10.207.102.2` |
  | saahas-mac | `10.207.102.3` |
  | nanna-phone | `10.207.102.4` |
- **Commands**:
  ```bash
  ssh pi "sudo wg show"                        # status & peer info
  ssh pi "sudo systemctl status wg-quick@wg0"  # service status
  ssh pi "pivpn add"                            # add new peer
  ssh pi "pivpn list"                           # list peers
  ```

### Adding a new go-link
1. Add nginx server block in `/etc/nginx/sites-available/golinks`
2. Add DNS entry on Pi: `ssh pi "sudo nano /etc/hosts"`
3. Reload both:
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ssh pi "sudo pihole reloaddns"
   ```

Or use the management scripts in `go-links/`.

---

## Quick Reference

```bash
# Check what's listening
ss -tlnp | grep LISTEN

# All running services
systemctl list-units --type=service --state=running

# Docker containers
docker ps

# System resources
htop
nvidia-smi  # GPU usage
```
