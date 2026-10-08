#!/usr/bin/env bash
# One-time setup ON the Google Cloud VM, from the repo root (.env already filled in):
#   bash scripts/gcp/setup.sh
# Takes ~20-30 min: installs system packages, two virtualenvs, all models (~20 GB) and
# ngrok, then installs and starts the "wazobia" systemd service. The service starts on
# boot and restarts the whole stack if anything crashes.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

[ -f .env ] || { echo "Copy .env.example to .env and fill it in first"; exit 1; }
set -a; source .env; set +a
: "${HF_TOKEN:?set HF_TOKEN in .env}"
if [ -z "${ID_SALT:-}" ]; then
  echo "== ID_SALT is empty: generating one and saving it to .env (never change it later)"
  SALT="$(openssl rand -hex 32)"
  if grep -q '^ID_SALT=' .env; then sed -i "s/^ID_SALT=.*/ID_SALT=$SALT/" .env; else echo "ID_SALT=$SALT" >> .env; fi
fi

echo "== GPU"
if ! nvidia-smi; then
  echo "No GPU driver yet. On a new Deep Learning VM it installs during the first ~5 min"
  echo "after boot; wait, then run this script again."
  exit 1
fi

echo "== system packages"
sudo apt-get update -q
sudo apt-get install -y -q ffmpeg python3-venv python3-dev curl

# Use the system Python, not any conda Python the image may put first on PATH.
PY=/usr/bin/python3
$PY -c 'import sys; assert sys.version_info >= (3, 10), "need Python >= 3.10"'

echo "== vLLM virtualenv"
[ -d .venv-vllm ] || $PY -m venv .venv-vllm
.venv-vllm/bin/pip install --no-cache-dir -U pip vllm

echo "== app virtualenv"
[ -d .venv ] || $PY -m venv .venv
.venv/bin/pip install --no-cache-dir -U pip
.venv/bin/pip install --no-cache-dir -r requirements.txt

echo "== downloading models"
.venv/bin/python - <<'PY'
import os

from huggingface_hub import snapshot_download

repos = [
    os.environ.get("LLM_MODEL") or "NCAIR1/N-ATLaS",
    os.environ.get("ASR_MODEL_HA") or "NCAIR1/Hausa-ASR",
    os.environ.get("ASR_MODEL_IG") or "NCAIR1/Igbo-ASR",
    os.environ.get("ASR_MODEL_YO") or "NCAIR1/Yoruba-ASR",
    os.environ.get("ASR_MODEL_EN") or "NCAIR1/NigerianAccentedEnglish",
    os.environ.get("EMBEDDING_MODEL") or "intfloat/multilingual-e5-small",
]
if os.environ.get("TTS_ENABLED") == "1":
    repos += ["facebook/mms-tts-hau", "facebook/mms-tts-ibo", "facebook/mms-tts-yor", "facebook/mms-tts-eng"]
for repo in repos:
    print("->", repo, flush=True)
    snapshot_download(repo)
PY

echo "== ngrok"
if [ ! -x bin/ngrok ]; then
  mkdir -p bin
  curl -sSL https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz | tar xz -C bin
fi
bin/ngrok version

echo "== systemd service"
sudo tee /etc/systemd/system/wazobia.service >/dev/null <<EOF
[Unit]
Description=WazobiaAssist (vLLM + app + ngrok)
After=network-online.target
Wants=network-online.target

[Service]
User=$(id -un)
WorkingDirectory=$ROOT
ExecStart=/bin/bash $ROOT/scripts/run_all.sh
Restart=always
RestartSec=10
KillMode=control-group
TimeoutStopSec=60

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable wazobia
sudo systemctl restart wazobia

echo
echo "Started. The model takes ~3-5 min to load. Useful commands:"
echo "  sudo systemctl status wazobia        # is it running?"
echo "  journalctl -u wazobia -f             # service log"
echo "  tail -f data/logs/app.log            # app log (also vllm.log, ngrok.log)"
echo "  curl localhost:8080/health           # app health and document counts"
echo "  sudo systemctl restart wazobia       # after changing .env or the domain documents"
