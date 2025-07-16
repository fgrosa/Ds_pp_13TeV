#!/bin/bash

# RunProjections.sh
# Usage: bash RunProjections.sh [TRIAL_DIR]

# Get trial directory (default to current directory if not provided)
TRIAL_DIR=${1:-.}

# Base paths
PROJ_PATH="../../Projections_RawYields"

# Maximum number of retries
MAX_RETRIES=3

# Configuration paths
ConfigFilePromptEnhanced="${TRIAL_DIR}/config_projection_prompt_enhanced.yml"
ConfigFileDir="${TRIAL_DIR}/configs/Projections"
ProjectionsDir="${TRIAL_DIR}/Projections"

# Create output directory if it doesn't exist
mkdir -p "${ProjectionsDir}"

echo "=== Running Projections ==="
echo "Trial directory: ${TRIAL_DIR}"
echo "Projections output: ${ProjectionsDir}"

# Build array of projection config files
declare -a ProjectionsConfigs=()
for filename in "${ConfigFileDir}"/*.yml; do
    if [[ -f "$filename" ]]; then
        tmp_name="$(basename -- "${filename}" .yml)"
        tmp_name=${tmp_name:23}  # Adjust this number based on your naming convention
        ProjectionsConfigs+=("${tmp_name}")
    fi
done

echo "Found ${#ProjectionsConfigs[@]} projection configs"

# Run prompt enhanced projection with retry
if [[ -f "${ConfigFilePromptEnhanced}" ]]; then
    echo "Running prompt enhanced projection..."

    for ((attempt=1; attempt<=MAX_RETRIES; attempt++)); do
        echo "Attempt $attempt of $MAX_RETRIES..."
        nice -n 15 python3 "${PROJ_PATH}/project_data_from_sparse.py" "${ConfigFilePromptEnhanced}"
        status=$?

        if [[ $status -eq 0 ]]; then
            echo "Prompt enhanced projection succeeded on attempt $attempt."
            break
        else
            echo "Prompt enhanced projection failed on attempt $attempt."
            if [[ $attempt -lt MAX_RETRIES ]]; then
                echo "Retrying..."
            else
                echo "All $MAX_RETRIES attempts failed. Check above logs."
                exit 1
            fi
        fi
    done

    # Merge prompt enhanced results
    if [[ -d "${ProjectionsDir}/prompt_enhanced" ]]; then
        echo "Merging prompt enhanced results..."
        hadd -f "${ProjectionsDir}/projection_prompt_enhanced.root" "${ProjectionsDir}/prompt_enhanced/"*.root
    else
        echo "Warning: prompt_enhanced directory not found"
    fi
else
    echo "Warning: ${ConfigFilePromptEnhanced} not found, skipping prompt enhanced projection"
fi

# Run parallel projections for all cutsets
if [[ ${#ProjectionsConfigs[@]} -gt 0 ]]; then
    echo "Running parallel projections for ${#ProjectionsConfigs[@]} configs..."
    nice -n 15 parallel --retries ${MAX_RETRIES} -j3 \
        --joblog "${ProjectionsDir}/parallel_joblog.txt" \
        --results "${ProjectionsDir}/results" \
        python3 "${PROJ_PATH}/project_data_from_sparse.py" "${ConfigFileDir}/config_projection_data_{1}.yml" \
        ::: "${ProjectionsConfigs[@]}"
    
    # Merge projection files for each cutset
    echo "Merging projection files..."
    for dir in "${ProjectionsDir}"/*; do
        if [[ -d "$dir" && $(basename "$dir") =~ [0-9]{2}$ ]]; then
            cutset_name=$(basename "$dir")
            echo "Merging projections for cutset ${cutset_name}..."
            hadd -f "${ProjectionsDir}/projection_data_${cutset_name}.root" "${ProjectionsDir}/${cutset_name}/"*.root
        fi
    done
else
    echo "No projection configs found, skipping parallel projections"
fi

echo "=== Projections Complete ==="
