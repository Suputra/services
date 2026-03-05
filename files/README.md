# files — HTTP file service for s-term

Lightweight HTTP service that lets the s-term (ESP32 e-ink device) read/write files on the lab PC via named "mounts", with git push support.

## Run

```bash
uv run files.py
```

Port 8200.

## Mounts

Configured in `MOUNTS` dict at top of `files.py`:

```python
MOUNTS = {
    "daily": "/home/saahas/saah.as/content/private/daily",
}
```

## Endpoints

- `GET /mounts` — list mount names
- `GET /m/{mount}/files` — list files in mount
- `GET /m/{mount}/files/{name}` — read file (200 empty for new)
- `PUT /m/{mount}/files/{name}` — write file (plain text body)
- `POST /m/{mount}/push` — git add + commit + push

## Systemd

```ini
# /etc/systemd/system/files.service
[Unit]
Description=HTTP File Service
After=network.target

[Service]
Type=simple
User=saahas
WorkingDirectory=/home/saahas/services/files
ExecStart=/home/saahas/.local/bin/uv run files.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now files.service
```

## Nginx

Add to `go-links/golinks.nginx.conf`:

```nginx
# files.y -> HTTP File Service
server {
    listen 80;
    listen [::]:80;
    server_name files.y;

    location / {
        proxy_pass http://127.0.0.1:8200;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
sudo nginx -t && sudo systemctl reload nginx
```

## DNS

Pi-hole: add CNAME `files.y` -> `10.0.0.100` (or A record).
