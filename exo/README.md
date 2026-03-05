# Exo - Distributed AI Inference

Distributed inference cluster using [exo](https://github.com/exo-explore/exo). Exposes an OpenAI-compatible API for running LLMs across multiple devices.

- **API Port**: 52415 (default)
- **Dashboard**: http://localhost:52415
- **Tech**: Python 3.13 + Rust (pyo3 bindings) + CUDA
- **Install dir**: `repo/` (cloned from GitHub, built with `uv sync`)
- **Service**: `/etc/systemd/system/exo.service`

## API Usage

exo exposes an OpenAI-compatible endpoint:

```bash
curl http://localhost:52415/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model": "llama-3.2-3b", "messages": [{"role": "user", "content": "Hello"}]}'
```

## Commands

```bash
sudo systemctl status exo
sudo systemctl restart exo
sudo journalctl -u exo -f
```

## Updating

```bash
cd ~/services/exo/repo
git pull
cd dashboard && npm install && npm run build && cd ..
PATH="$HOME/.cargo/bin:$PATH" uv sync --python 3.13
sudo systemctl restart exo
```
