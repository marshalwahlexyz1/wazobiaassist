#!/usr/bin/env bash
# Creates the WazobiaAssist GPU server: one NVIDIA L4 (24 GB) on a g2-standard-8.
# Run it in Google Cloud Shell (or anywhere gcloud is logged in) AFTER the L4 quota
# request in us-central1 has been approved.
#
#   bash scripts/gcp/create_vm.sh
#   ZONE=us-central1-b bash scripts/gcp/create_vm.sh     # if the first zone has no L4s free
set -euo pipefail

PROJECT=${PROJECT:-$(gcloud config get-value project 2>/dev/null)}
ZONE=${ZONE:-us-central1-a}
NAME=${NAME:-wazobia}

# Newest Deep Learning VM image with CUDA 12 on Ubuntu (comes with the NVIDIA driver).
IMAGE_FAMILY=${IMAGE_FAMILY:-$(gcloud compute images list --project deeplearning-platform-release \
  --filter="family~^common-cu12.*ubuntu" --format="value(family)" | sort -V | tail -1)}
if [ -z "$IMAGE_FAMILY" ]; then
  echo "Could not find a Deep Learning VM image. List them with:"
  echo "  gcloud compute images list --project deeplearning-platform-release --format='value(family)' | sort -u"
  echo "then run again with IMAGE_FAMILY=<family>."
  exit 1
fi

echo "Creating $NAME in $PROJECT / $ZONE with image family $IMAGE_FAMILY"
# g2-standard-8 comes with one L4 GPU attached.
gcloud compute instances create "$NAME" \
  --project "$PROJECT" --zone "$ZONE" \
  --machine-type g2-standard-8 \
  --maintenance-policy TERMINATE --provisioning-model STANDARD \
  --image-family "$IMAGE_FAMILY" --image-project deeplearning-platform-release \
  --boot-disk-size 150GB --boot-disk-type pd-balanced \
  --metadata install-nvidia-driver=True

cat <<MSG

Done. Next:
  gcloud compute ssh $NAME --zone $ZONE
  git clone https://github.com/marshalwahlexyz1/wazobiaassist && cd wazobiaassist
  bash scripts/gcp/setup.sh

To stop paying when nobody is testing:  gcloud compute instances stop $NAME --zone $ZONE
MSG
