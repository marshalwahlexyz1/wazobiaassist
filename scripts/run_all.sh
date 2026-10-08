#!/usr/bin/env bash
# Start vLLM (N-ATLaS) + the app + ngrok on the GPU server, then wait.
# Exits (stopping everything) as soon as any of them dies; the systemd service installed
# by scripts/gcp/setup.sh then restarts the whole stack. Can also be run by hand.
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
set -a; source .env; set +a

LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR"
stamp() { date "+%F %T"; }

cleanup() {
  echo "$(stamp) stopping all processes"
  pkill -P $$ 2>/dev/null
  wait 2>/dev/null
}
trap cleanup EXIT
trap 'exit 0' INT TERM

echo "$(stamp) starting vLLM"
bash scripts/serve_llm.sh >>"$LOG_DIR/vllm.log" 2>&1 &

for _ in $(seq 1 120); do
  curl -sf http://127.0.0.1:8000/v1/models >/dev/null && break
  sleep 5
done
if ! curl -sf http://127.0.0.1:8000/v1/models >/dev/null; then
  echo "$(stamp) vLLM did not start within 10 min; see $LOG_DIR/vllm.log"
  exit 1
fi
echo "$(stamp) vLLM ready"

.venv/bin/uvicorn app.server:app --host 127.0.0.1 --port 8080 >>"$LOG_DIR/app.log" 2>&1 &
echo "$(stamp) app started (log: $LOG_DIR/app.log)"

if [ -n "${NGROK_DOMAIN:-}" ]; then
  # NGROK_AUTHTOKEN is read from the environment (.env).
  bin/ngrok http 8080 --url "https://$NGROK_DOMAIN" --log stdout >>"$LOG_DIR/ngrok.log" 2>&1 &
  echo "$(stamp) ngrok started: https://$NGROK_DOMAIN"
fi

wait -n
echo "$(stamp) a process exited; see logs in $LOG_DIR"
exit 1
