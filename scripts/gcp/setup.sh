#!/usr/bin/env bash
# Sets up WazobiaAssist on the GPU server and installs it as three always-on
# services that restart themselves if they crash:
#   wazobia-vllm   N-ATLaS served by vLLM on localhost:8000
#   wazobia-app    the bot + web page on localhost:8080 (waits for vLLM)
#   wazobia-ngrok  the fixed public https address -> localhost:8080
#
# Run from the repository folder on the server:  bash scripts/gcp/setup.sh
# Safe to run again (e.g. after editing .env).
set -euo pipefail
cd "$(dirname "$0")/../.."
DIR=$(pwd)
ME=$(whoami)

echo "== Checking the GPU"
nvidia-smi --query-gpu=name,memory.total --format=csv || {
  echo "No GPU driver yet. Wait a few minutes after first boot (the driver installs itself) and run again."; exit 1; }

echo "== System packages"
sudo apt-get update -q
sudo apt-get install -y -q ffmpeg python3-venv git curl
if ! command -v ngrok >/dev/null; then
  curl -sSL https://ngrok-agent.s3.amazonaws.com/ngrok.asc | sudo tee /etc/apt/trusted.gpg.d/ngrok.asc >/dev/null
  echo "deb https://ngrok-agent.s3.amazonaws.com buster main" | sudo tee /etc/apt/sources.list.d/ngrok.list >/dev/null
  sudo apt-get update -q && sudo apt-get install -y -q ngrok
fi

echo "== Python environments (this takes a while the first time)"
[ -d .venv ] || /usr/bin/python3 -m venv .venv
.venv/bin/pip install -q --upgrade pip
.venv/bin/pip install -q -r requirements.txt
[ -d .venv-vllm ] || /usr/bin/python3 -m venv .venv-vllm
.venv-vllm/bin/pip install -q --upgrade pip
.venv-vllm/bin/pip install -q vllm

echo "== Settings"
[ -f .env ] || cp .env.example .env
# The app refuses to start without a salt. Generate one if it's empty (never change it later).
if ! grep -q '^ID_SALT=.' .env; then
  SALT=$(openssl rand -hex 16)
  if grep -q '^ID_SALT=' .env; then sed -i "s/^ID_SALT=.*/ID_SALT=$SALT/" .env; else echo "ID_SALT=$SALT" >> .env; fi
fi
missing=""
for key in HF_TOKEN NGROK_AUTHTOKEN NGROK_DOMAIN; do
  grep -q "^$key=." .env || missing="$missing $key"
done
if [ -n "$missing" ]; then
  echo "Fill in these values in $DIR/.env, then run this script again:$missing"
  exit 1
fi

echo "== Installing services"
for unit in wazobia-vllm wazobia-app wazobia-ngrok; do
  sed "s#__DIR__#$DIR#g; s#__USER__#$ME#g" "scripts/gcp/$unit.service" | sudo tee "/etc/systemd/system/$unit.service" >/dev/null
done
sudo systemctl daemon-reload
sudo systemctl enable wazobia-vllm wazobia-app wazobia-ngrok
sudo systemctl restart wazobia-vllm wazobia-app wazobia-ngrok

DOMAIN=$(grep '^NGROK_DOMAIN=' .env | cut -d= -f2)
cat <<MSG

Started. The model takes a few minutes to load the first time (it downloads ~16 GB).
  Watch it:        journalctl -u wazobia-vllm -u wazobia-app -f
  Check it:        curl -s localhost:8080/health
  Public address:  https://$DOMAIN   (WhatsApp webhook: https://$DOMAIN/whatsapp)
  After a code or .env change:  git pull && sudo systemctl restart wazobia-app
MSG
