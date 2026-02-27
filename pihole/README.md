# Pi-hole

Network-wide DNS and ad-blocking running on the Raspberry Pi (10.0.0.10).

- **Admin UI**: `y/pihole` or `10.0.0.10:8080/admin`
- **SSH**: `ssh pi`

## Setup

Pi-hole was installed via the official installer:

```bash
curl -sSL https://install.pi-hole.net | bash
```

All devices on the network use the Pi (10.0.0.10) as their DNS server, configured via DHCP on the router.

## Custom `.y` Domains

Go-links use custom DNS entries in `/etc/hosts` on the Pi. Each `.y` domain resolves to Tower (10.0.0.100).

To view current entries:
```bash
ssh pi "grep '\.y' /etc/hosts"
```

To add a new one:
```bash
ssh pi "echo '10.0.0.100 newapp.y' | sudo tee -a /etc/hosts"
ssh pi "sudo pihole reloaddns"
```

## Commands

```bash
ssh pi "pihole status"          # check status
ssh pi "pihole -up"             # update Pi-hole
ssh pi "sudo pihole reloaddns"  # reload DNS after /etc/hosts changes
ssh pi "pihole -t"              # tail the query log
```
