# Immich

Self-hosted Google Photos alternative.

- **URL**: `y/pics` or `pics.y`
- **Port**: 2283
- **Tech**: Docker Compose

## Storage Layout

| Path | Purpose |
|------|---------|
| `/mnt/merged/immich/library` | Photo/video library (mergerfs pool spanning storage+media drives) |
| `/mnt/fast/immich-postgres` | PostgreSQL database (NVMe) |

## Setup

1. Install Docker and Docker Compose
2. Copy `.env.example` to `.env` and fill in secrets:
   ```bash
   cp .env.example .env
   nano .env
   ```
3. Start the stack:
   ```bash
   docker compose up -d
   ```

## Commands

```bash
cd ~/services/immich
docker compose ps          # container status
docker compose logs -f     # follow logs
docker compose restart     # restart all
docker compose pull && docker compose up -d  # update
```

## Containers

- `immich_server` - Main app
- `immich_machine_learning` - ML/face recognition
- `immich_postgres` - Database
- `immich_redis` - Cache
