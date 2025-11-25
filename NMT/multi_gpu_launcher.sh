#!/bin/bash
# ============================================================
# Multi-GPU launcher for NMT experiments
# This script runs one language per GPU in parallel
# ============================================================

# Language list (adjust as needed)
LANGS=("sw" "zu" "am" "ur")

# GPU IDs to use (corresponding to LANGS order)
GPUS=(0 1 2 3)

# Sanity check
if [ ${#LANGS[@]} -ne ${#GPUS[@]} ]; then
  echo "❌ Number of LANGS and GPUS must match!"
  exit 1
fi

# Loop over each language and GPU
for ((i=0; i<${#LANGS[@]}; i++)); do
  lang=${LANGS[$i]}
  gpu=${GPUS[$i]}
  log_file="run_${lang}.log"

  echo "🚀 Launching ${lang} on GPU ${gpu} (log: ${log_file})"
  CUDA_VISIBLE_DEVICES=${gpu} nohup ./run_all_experiment.sh ${lang} > ${log_file} 2>&1 &
done

echo "✅ All experiments launched in parallel!"
