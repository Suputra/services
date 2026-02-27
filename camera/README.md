# camera-mux

Persistent MJPEG relay that keeps a DroidCam phone camera alive and serves frames locally.

- **URL**: `y/cam` or `cam.y`
- **Port**: 8100
- **Source**: `http://10.0.44.199:4747/video?640x480` (DroidCam)

## Endpoints

- `/` - Live stream page
- `/frame` - Single JPEG snapshot
- `/stream` - MJPEG stream (for OpenCV / browser)
- `/health` - JSON status

## Setup

```bash
cd ~/services/camera
./install.sh
```

This symlinks the systemd user service and starts it. See `install.sh` for the manual nginx/DNS steps.

## Commands

```bash
systemctl --user status camera-mux
systemctl --user restart camera-mux
journalctl --user -u camera-mux -f
curl localhost:8100/health
```
