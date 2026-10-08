#!/usr/bin/env bash
# Serve N-ATLaS with vLLM (OpenAI-compatible API on :8000), from the repo root:
#   bash scripts/serve_llm.sh
# Needs the .venv-vllm virtualenv (scripts/gcp/setup.sh creates it) and HF_TOKEN.
#
# Memory: the 8B model in bf16 needs ~16 GB for weights. GPU_MEM is the fraction of
# VRAM vLLM may take; the rest is for the ASR / embedding / TTS models in the app.
#   L4 24 GB (Google Cloud g2) -> GPU_MEM=0.80, MAX_MODEL_LEN=4096
#   40-48 GB cards             -> GPU_MEM=0.60, MAX_MODEL_LEN=8192
# If vLLM runs out of memory on a 24 GB card, set VLLM_EXTRA_ARGS="--quantization fp8"
# (halves the weights; small quality cost).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="$ROOT/.venv-vllm/bin:$PATH"
: "${HF_TOKEN:?set HF_TOKEN (account must have access to NCAIR1/N-ATLaS)}"

# shellcheck disable=SC2086  # VLLM_EXTRA_ARGS is intentionally word-split
exec vllm serve "${LLM_MODEL:-NCAIR1/N-ATLaS}" \
  --dtype bfloat16 \
  --max-model-len "${MAX_MODEL_LEN:-4096}" \
  --gpu-memory-utilization "${GPU_MEM:-0.80}" \
  --host 127.0.0.1 --port 8000 \
  ${VLLM_EXTRA_ARGS:-}
