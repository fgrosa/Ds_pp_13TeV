#!/bin/bash
TRAIN_RUN=304566
INPUT="/home/fchinu/Run3/Ds_pp_13TeV/utils/AODsForDownload.txt"
IS_SLIM=true
MAX_FILES_TO_DOWNLOAD=400
N_FILES_FOR_MERGE=30
N_JOBS=10
SUFFIX="LHC24h1"
SELECTIONS="" #"fNSigTpcTofKa0 < 1.e5 and fNSigTpcTofKa1 < 1.e5 and fNSigTpcTofKa2 < 1.e5 and fNSigTpcTofPi0 < 1.e5 and fNSigTpcTofPi1 < 1.e5 and fNSigTpcTofPi2 < 1.e5 and fDecayLength < 25" # Can be null if no selection is needed
TRAIN_FRACTION=1
ISMC=true
MC_SELECTIONS=(
    "PromptDs:abs(fFlagMcMatchRec) == 5 and fOriginMcRec == 1 and fFlagMcDecayChanRec == 6"
    "PromptDplus:abs(fFlagMcMatchRec) == 4 and fOriginMcRec == 1 and fFlagMcDecayChanRec == 1"
    "Prompt:(abs(fFlagMcMatchRec) == 4 or abs(fFlagMcMatchRec) == 5) and fOriginMcRec == 1 and (fFlagMcDecayChanRec == 1 or fFlagMcDecayChanRec == 6)"
    "NonPromptDs:abs(fFlagMcMatchRec) == 5 and fOriginMcRec == 2 and fFlagMcDecayChanRec == 6"
    "NonPromptDplus:abs(fFlagMcMatchRec) == 4 and fOriginMcRec == 2 and fFlagMcDecayChanRec == 1"
    "NonPrompt:(abs(fFlagMcMatchRec) == 4 or abs(fFlagMcMatchRec) == 5) and fOriginMcRec == 2 and (fFlagMcDecayChanRec == 1 or fFlagMcDecayChanRec == 6)"
    "DplusBkg:abs(fFlagMcMatchRec) == 0"
    ) # Array of selections in the form "Name:selection", or "" if no selection is needed

TREE_NAME=("O2hfcanddslite") # Can be an array of strings for multiple trees, or a single string for a single tree. "*" for all trees.
OUTPUT_DIRECTORY="/home/fchinu/Run3/Ds_pp_13TeV/Datasets/Ds_pp_run3_ml" # Files will be downloaded in this/directory/MC(data)/TrainXXXXXX/
OPTIONAL_ARGS="" # --aod, --analysis, or --parquet


#_______________________________________________________________________________________________________________________

# Check if TREE_NAME is an array or a single string
if [ "$(declare -p TREE_NAME 2>/dev/null | grep 'declare -a')" ]; then
    # Convert array to JSON format
    tree_name_json=$(printf '%s\n' "${TREE_NAME[@]}" | jq -R . | jq -s .)
else
    # Single string, convert it to array and then to JSON format
    tree_name_json=$(jq -n --arg tn "$TREE_NAME" '$tn')
fi

# Convert MC_SELECTIONS to JSON format using jq
if [ -z "$MC_SELECTIONS" ]; then
    selections_json="null"
else
    selections_json=$(printf '%s\n' "${MC_SELECTIONS[@]}" | awk -F: '{print ""$1": "$2""}' | jq -R -s 'split("\n") | map(select(length > 0)) | map(split(": ") | { (.[0]): .[1] }) | add')
fi

# Pass information to a json file using jq
# For strings, use --arg, for numbers, use --argjson
jq -n --argjson train_run "$TRAIN_RUN" \
      --arg input "$INPUT" \
      --argjson is_slim "$IS_SLIM" \
      --argjson max_files_to_download "$MAX_FILES_TO_DOWNLOAD" \
      --argjson n_files_for_merge "$N_FILES_FOR_MERGE" \
      --argjson n_jobs "$N_JOBS" \
      --arg suffix "$SUFFIX" \
      --arg selections "$SELECTIONS" \
      --argjson train_fraction "$TRAIN_FRACTION" \
      --argjson isMC "$ISMC" \
      --argjson mc_selections "$selections_json" \
      --argjson tree_name "$tree_name_json" \
      --arg output_directory "$OUTPUT_DIRECTORY" \
      '{
          train_run: $train_run,
          input: $input,
          is_slim: $is_slim,
          max_files_to_download: $max_files_to_download,
          n_files_for_merge: $n_files_for_merge,
          n_jobs: $n_jobs,
          suffix: $suffix,
          selections: $selections,
          train_fraction: $train_fraction,
          isMC: $isMC,
          mc_selections: $mc_selections,
          tree_name: $tree_name,
          output_directory: $output_directory
      }' > config_download.json

python3 /home/fchinu/Run3/ThesisUtils/train_output_downloader.py config_download.json $OPTIONAL_ARGS

rm -f config_download.json