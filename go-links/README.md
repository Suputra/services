# Go-Links

Short URL system using nginx + Pi-hole DNS for `*.y` domains.

## How It Works

1. Browser requests `y/pad`
2. Pi-hole DNS resolves `y` -> `10.0.0.100` (Tower)
3. nginx catches `y/<app>` and redirects to `<app>.y`
4. Pi-hole resolves `<app>.y` -> `10.0.0.100`
5. nginx proxies to the actual service

## Available Links

| Link | Domain | Service |
|------|--------|---------|
| `y/pics` | `pics.y` | Immich (reverse proxy to :2283) |
| `y/pad` | `pad.y` | Collaborative Pad (proxy to :8000) |
| `y/router` | `router.y` | Router admin (redirect) |
| `y/pihole` | `pihole.y` | Pi-hole admin (redirect) |
| `y/wiki` | `wiki.y` | Wikipedia (redirect) |
| `y/admin` | `admin.y` | Link directory (CGI) |
| `y/cam` | `cam.y` | Camera stream (proxy to :8100) |

## Config Files

- **nginx**: `/etc/nginx/sites-available/golinks` (canonical copy in this repo: `golinks.nginx.conf`)
- **DNS**: `/etc/hosts` on the Pi (custom `.y` domains)

## Link Management Scripts

| Script | Purpose |
|--------|---------|
| `add-link <name> <url>` | Add a redirect-style go-link |
| `add-file <name> <path>` | Serve a file/directory download |
| `add-page <name> [html]` | Serve a static HTML page |
| `list-links` | Show all configured go-links |
| `update-index` | Regenerate the go-links index page |

Each script automatically adds the nginx server block, DNS entry on the Pi, and reloads both.

## Adding a Link Manually

1. Add nginx server block in `/etc/nginx/sites-available/golinks`
2. Add DNS entry on Pi: `ssh pi "sudo nano /etc/hosts"`
3. Reload both:
   ```bash
   sudo nginx -t && sudo systemctl reload nginx
   ssh pi "sudo pihole reloaddns"
   ```
