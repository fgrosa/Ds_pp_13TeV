#!/bin/bash

# RunEfficiencies.sh
# Usage: bash RunEfficiencies.sh [TRIAL_DIR]

# Get trial directory (default to current directory if not provided)
TRIAL_DIR=${1:-.}

# Path to efficiency evaluation script
EFF_SCRIPT="../../Efficiency/evaluate_efficiency_sparse.py"

# Max retries for each failed run
MAX_RETRIES=3

# Config and output directories
EffConfigDir="${TRIAL_DIR}/configs/Efficiencies"
EffResultsDir="${TRIAL_DIR}/Efficiencies"

# Create output directory if it doesn't exist
mkdir -p "${EffResultsDir}"

echo "=== Running Efficiency Evaluations ==="
echo "Trial directory: ${TRIAL_DIR}"
echo "Efficiency output: ${EffResultsDir}"

# Build list of efficiency configs
declare -a EffConfigs=()
for filename in "${EffConfigDir}"/*.yml; do
    if [[ -f "$filename" ]]; then
        tmp_name="$(basename -- "${filename}" .yml)"
        tmp_name=${tmp_name:10}  # Adjust this based on your config naming
        EffConfigs+=("${tmp_name}")
    fi
done

echo "Found ${#EffConfigs[@]} efficiency configs"

# Run in parallel with retries
if [[ ${#EffConfigs[@]} -gt 0 ]]; then
    echo "Launching parallel jobs..."
    nice -n 15 parallel --retries ${MAX_RETRIES} -j10 \
        --joblog "${EffResultsDir}/parallel_efficiency_joblog.txt" \
        --results "${EffResultsDir}/logs" \
        python3 "${EFF_SCRIPT}" "${EffConfigDir}/config_eff{1}.yml" \
        ::: "${EffConfigs[@]}"
    echo "Efficiency evaluation complete. Logs in ${EffResultsDir}/parallel_efficiency_joblog.txt"
else
    echo "No efficiency configs found, skipping."
fi

echo "=== Efficiency Evaluation Complete ==="
