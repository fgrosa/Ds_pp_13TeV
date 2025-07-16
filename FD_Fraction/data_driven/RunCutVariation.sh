#!/bin/bash

# RunCutVariation.sh
# Usage: bash RunCutVariation.sh [TRIAL_DIR]

# Get trial directory (default to current directory if not provided)
TRIAL_DIR=${1:-.}

# Base paths - adjust these to your actual paths
SCRIPT_PATH="compute_fraction_cutvar.py"

# Maximum number of retries
MAX_RETRIES=3

# Configuration paths (now relative to trial directory)
ConfigDsDir="${TRIAL_DIR}/configs/Fractions/Ds"
ConfigDplusDir="${TRIAL_DIR}/configs/Fractions/Dplus"
CutVariationDir="${TRIAL_DIR}/Fractions"

# Create output directory if it doesn't exist
mkdir -p ${CutVariationDir}

echo "=== Running Cut Variation Analysis ==="
echo "Trial directory: ${TRIAL_DIR}"
echo "Cut variation output: ${CutVariationDir}"

# Function to create parallel job arrays
create_job_arrays() {
    declare -g -a AllConfigs=()
    declare -g -a AllParticles=()
    
    # Add Ds configs
    if [[ ${#DsConfigs[@]} -gt 0 ]]; then
        for config_name in "${DsConfigs[@]}"; do
            AllConfigs+=("${ConfigDsDir}/${config_name}.json")
            AllParticles+=("ds")
        done
    fi
    
    # Add D+ configs
    if [[ ${#DplusConfigs[@]} -gt 0 ]]; then
        for config_name in "${DplusConfigs[@]}"; do
            AllConfigs+=("${ConfigDplusDir}/${config_name}.json")
            AllParticles+=("dplus")
        done
    fi
}

# Build array of Ds config files
declare -a DsConfigs=()
if [[ -d "${ConfigDsDir}" ]]; then
    for filename in ${ConfigDsDir}/*.json; do
        if [[ -f "$filename" ]]; then
            config_name="$(basename -- ${filename} .json)"
            DsConfigs+=("${config_name}")
        fi
    done
    echo "Found ${#DsConfigs[@]} Ds configs"
else
    echo "Warning: ${ConfigDsDir} not found"
fi

# Build array of D+ config files
declare -a DplusConfigs=()
if [[ -d "${ConfigDplusDir}" ]]; then
    for filename in ${ConfigDplusDir}/*.json; do
        if [[ -f "$filename" ]]; then
            config_name="$(basename -- ${filename} .json)"
            DplusConfigs+=("${config_name}")
        fi
    done
    echo "Found ${#DplusConfigs[@]} D+ configs"
else
    echo "Warning: ${ConfigDplusDir} not found"
fi

# Create job arrays for parallel processing
create_job_arrays

# Track failed jobs
declare -a failed_jobs=()

# Process all configs with parallel
total_configs=$((${#DsConfigs[@]} + ${#DplusConfigs[@]}))
if [[ ${total_configs} -gt 0 ]]; then
    echo "Processing ${total_configs} configurations with parallel..."
    
    # Create temporary files for parallel processing
    config_file_list=$(mktemp)
    for config in "${AllConfigs[@]}"; do
        echo "$config" >> "$config_file_list"
    done
    
    # Run parallel processing
    nice -n 15 parallel --retries ${MAX_RETRIES} -j3 \
        --joblog "${CutVariationDir}/parallel_joblog.txt" \
        --results "${CutVariationDir}/logs" \
        python3 ${SCRIPT_PATH} {1} \
        :::: "$config_file_list"
    
    # Clean up temporary file
    rm "$config_file_list"
    
    echo "Parallel processing complete. Check ${CutVariationDir}/parallel_joblog.txt for job status"
else
    echo "No configs found, nothing to process"
fi

# Summary
echo "=== Cut Variation Analysis Complete ==="
echo "Processed ${total_configs} total configs (${#DsConfigs[@]} Ds + ${#DplusConfigs[@]} D+)"
echo "Check ${CutVariationDir}/parallel_joblog.txt for detailed job status"
echo "Individual job logs are in ${CutVariationDir}/logs/"