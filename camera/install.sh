#!/usr/bin/env bash
set -euo pipefail

SERVICE_NAME="camera-mux"
SERVICE_FILE="$(dirname "$(realpath "$0")")/${SERVICE_NAME}.service"
USER_SYSTEMD_DIR="$HOME/.config/systemd/user"

echo "==> Installing ${SERVICE_NAME} user service"

mkdir -p "$USER_SYSTEMD_DIR"
ln -sf "$SERVICE_FILE" "$USER_SYSTEMD_DIR/${SERVICE_NAME}.service"

systemctl --user daemon-reload
systemctl --user enable --now "$SERVICE_NAME"

echo "==> Service installed and started"
echo ""
systemctl --user status "$SERVICE_NAME" --no-pager || true
echo ""
echo "--- Manual steps (require sudo) ---"
echo ""
echo "1. Add nginx server block to /etc/nginx/sites-available/golinks:"
echo ""
cat <<'NGINX'
    server {
        listen 80;
        server_name cam.y;
        location / {
            proxy_pass http://127.0.0.1:8100;
            proxy_buffering off;
            proxy_cache off;
            proxy_set_header Connection '';
            proxy_http_version 1.1;
            chunked_transfer_encoding off;
        }
    }
NGINX
echo ""
echo "2. Add DNS entry on Pi:"
echo "   ssh pi \"echo '10.0.0.100 cam.y' | sudo tee -a /etc/hosts\""
echo "   ssh pi \"sudo pihole reloaddns\""
echo ""
echo "3. Reload nginx:"
echo "   sudo nginx -t && sudo systemctl reload nginx"
