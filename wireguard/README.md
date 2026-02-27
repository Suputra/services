# WireGuard VPN

Remote access to the home network via PiVPN, running on the Raspberry Pi (10.0.0.10).

## Network

- **Port**: 51820/UDP (forwarded on router to 10.0.0.10)
- **Subnet**: `10.207.102.0/24`
- **Config**: `/etc/wireguard/wg0.conf` (on Pi)
- **Service**: `wg-quick@wg0`

## Peers

| Name | IP |
|------|----|
| iphone | `10.207.102.2` |
| saahas-mac | `10.207.102.3` |
| nanna-phone | `10.207.102.4` |

## Setup (PiVPN)

PiVPN was installed on the Pi for easy WireGuard management:

```bash
ssh pi
curl -L https://install.pivpn.io | bash
```

During setup: select WireGuard, port 51820, use the Pi's local IP.

## Router Port Forwarding

Forward UDP port 51820 from WAN to `10.0.0.10:51820` on the router.

## Commands

```bash
ssh pi "sudo wg show"                        # status & peer info
ssh pi "sudo systemctl status wg-quick@wg0"  # service status
ssh pi "pivpn add"                            # add new peer
ssh pi "pivpn list"                           # list peers
ssh pi "pivpn remove"                         # remove a peer
ssh pi "pivpn -qr"                            # show QR code for mobile
```
