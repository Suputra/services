# Cloudflare DDNS

Updates a Cloudflare DNS record with the current public IP. Runs on the Pi via cron.

## Setup

1. Create a Cloudflare API token with `Zone:DNS:Edit` permissions
2. Create the env file on the Pi:
   ```bash
   mkdir -p ~/.config/ddns
   cat > ~/.config/ddns/ddns.env << 'EOF'
   CF_API_TOKEN=your-token-here
   CF_ZONE_ID=your-zone-id
   CF_RECORD_NAME=home.example.com
   EOF
   chmod 600 ~/.config/ddns/ddns.env
   ```
3. Copy the script to the Pi:
   ```bash
   scp cloudflare-ddns.sh pi:~/ddns/
   ```
4. Add a cron job on the Pi:
   ```bash
   ssh pi "crontab -e"
   # Add: */5 * * * * /home/pi/ddns/cloudflare-ddns.sh
   ```

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CF_API_TOKEN` | Yes | | Cloudflare API token |
| `CF_ZONE_ID` | Yes | | Cloudflare zone ID |
| `CF_RECORD_NAME` | Yes | | DNS record (e.g., `home.example.com`) |
| `CF_RECORD_TYPE` | No | `A` | Record type |
| `CF_TTL` | No | `300` | TTL in seconds |
| `CF_PROXIED` | No | `false` | Cloudflare proxy |
| `DDNS_ENV_FILE` | No | `~/.config/ddns/ddns.env` | Path to env file |
| `DDNS_LOG_FILE` | No | `~/ddns/ddns.log` | Path to log file |
