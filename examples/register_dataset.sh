#!/usr/bin/env bash
set -euo pipefail

dmatlas register \
  --dataset-id DS-EXAMPLE-001 \
  --title "Example metadata-only dataset" \
  --description "Metadata-only controlled-access pointer for future demonstration." \
  --species "Homo sapiens aggregate" \
  --institution-id INST-DMA-OPEN-001 \
  --contact maintainers@developmental-manifold.example \
  --citation "Example citation"

