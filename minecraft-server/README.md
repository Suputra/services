# Minecraft Modded Server

Modded Minecraft 1.20.1 server with Forge.

- **Ports**: 25565 (game), 25575 (RCON)
- **Forge Version**: 47.4.10
- **Memory**: 16GB (`user_jvm_args.txt`)
- **Server dir**: `/home/saahas/minecraft-server/` (runtime data lives here, not in this repo)

## What's in This Repo

Only scripts and config tracked here. Runtime data (world, mods, logs, jars) lives in the server directory.

| File | Purpose |
|------|---------|
| `run.sh` | Forge launch script |
| `user_jvm_args.txt` | JVM memory settings |
| `minecraft-server.service` | systemd unit file |
| `mc` | RCON helper (`./mc "command"` or `./mc` for interactive) |
| `download_mods.py` | Downloads mods from CurseForge manifest |

## Commands

```bash
sudo systemctl status minecraft-server
sudo systemctl restart minecraft-server
sudo journalctl -u minecraft-server -f

# RCON (interactive or one-shot):
./mc
./mc "list"
```

## Setup

1. Install Java 17
2. Run the Forge installer
3. Install the systemd service:
   ```bash
   sudo cp minecraft-server.service /etc/systemd/system/
   sudo systemctl daemon-reload
   sudo systemctl enable --now minecraft-server
   ```
