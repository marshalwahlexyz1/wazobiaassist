#!/usr/bin/env bash
# Create the GPU server on Google Cloud: one NVIDIA L4 (24 GB) on a g2-standard-8 VM,
# with the NVIDIA driver preinstalled. Run in Google Cloud Shell (console.cloud.google.com,
# ">_" button top right) or anywhere the gcloud CLI is logged in:
#   bash create_vm.sh
#
# Before this works:
#   1. The billing account must be upgraded from free trial (free-trial accounts get no GPUs).
#   2. Quota approved for "GPUs (all regions)" >= 1 and "NVIDIA L4 GPUs" >= 1 in your region.
# Cost: about $0.85/hour while running. Stop it with:
#   gcloud compute instances stop wazobia --zone <zone>
set -euo pipefail

VM="${VM:-wazobia}"
# L4s are often sold out in one zone; we try each in turn. Put the zones of the region
# where your L4 quota was approved first.
ZONES="${ZONES:-us-central1-a us-central1-b us-central1-c europe-west4-a europe-west4-b europe-west4-c}"
PROJECT="$(gcloud config get-value project 2>/dev/null)"
[ -n "$PROJECT" ] || { echo "Run: gcloud config set project <your-project-id>"; exit 1; }

echo "== project $PROJECT: enabling the Compute Engine API"
gcloud services enable compute.googleapis.com

# Newest Google Deep Learning VM image with CUDA 12 on Ubuntu 22.04 / Debian 12 (Python >= 3.10).
IMAGE_FAMILY="${IMAGE_FAMILY:-$(gcloud compute images list --project deeplearning-platform-release \
  --filter="family~^common-cu12 AND (family~ubuntu-2204 OR family~debian-12) AND NOT family~arm" \
  --sort-by=~creationTimestamp --limit=1 --format='value(family)')}"
[ -n "$IMAGE_FAMILY" ] || { echo "No Deep Learning VM image found; set IMAGE_FAMILY by hand"; exit 1; }
echo "== image family: $IMAGE_FAMILY"

for ZONE in $ZONES; do
  echo "== trying $ZONE"
  if gcloud compute instances create "$VM" \
      --zone "$ZONE" \
      --machine-type g2-standard-8 \
      --maintenance-policy TERMINATE \
      --restart-on-failure \
      --image-project deeplearning-platform-release \
      --image-family "$IMAGE_FAMILY" \
      --boot-disk-size 200GB \
      --boot-disk-type pd-balanced \
      --metadata install-nvidia-driver=True; then
    echo
    echo "Created $VM in $ZONE. Next:"
    echo "  gcloud compute ssh $VM --zone $ZONE"
    echo "  (wait ~5 min on first login while the NVIDIA driver installs; check with: nvidia-smi)"
    echo "Then copy the code and .env onto the VM and run:  bash scripts/gcp/setup.sh"
    exit 0
  fi
done

echo "Could not create the VM in any zone. Usually: no L4 quota in that region yet, or L4s"
echo "sold out. Check IAM & Admin -> Quotas, or try other zones: ZONES=\"us-east4-a ...\" bash $0"
exit 1
