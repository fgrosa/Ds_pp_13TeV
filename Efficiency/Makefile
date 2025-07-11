###################################
# Makefile for efficiency evaluation
###################################

# Configuration variables
NAME ?= OO
BASE_CONFIG_DIR = ./configs
BASE_CUTSET_DIR = ../Projections_RawYields/configs
BASE_DIR = ./efficiency
TRIAL_DIR = $(BASE_DIR)/$(NAME)

# Output directories
OUTPUT_EFF = $(TRIAL_DIR)

# Configuration file (adjust names based on data type)
CONFIG_EFF = config_efficiency.yml
CONFIG_WEIGHT = config_weights.yml
CONFIG_CUTSET = cutset.yml

# Source configuration files
SRC_CONFIG_EFF = $(BASE_CONFIG_DIR)/$(CONFIG_EFF)
SRC_CONFIG_WEIGHT = $(BASE_CONFIG_DIR)/$(CONFIG_WEIGHT)
SRC_CONFIG_CUTSET = $(BASE_CUTSET_DIR)/$(CONFIG_CUTSET)

# Copied configuration files
DEST_CONFIG_EFF = $(OUTPUT_EFF)/$(CONFIG_EFF)
DEST_CONFIG_WEIGHT = $(OUTPUT_EFF)/$(CONFIG_WEIGHT)
DEST_CONFIG_CUTSET = $(OUTPUT_EFF)/$(CONFIG_CUTSET)

# Scripts (adjust paths as needed)
EFF_SCRIPT = evaluate_efficiency_sparse.py
WEIGHT_SCRIPT = produce_mult_weights.py

# Output files (adjust based on what your scripts actually produce)
WEIGHT_OUTPUT = $(OUTPUT_EFF)/weights.done
EFF_OUTPUT = $(OUTPUT_EFF)/efficiency.done

# Define the targets
.PHONY: all clean-output help setup weight efficiency

# Default target
all: setup weight efficiency

# Help target
help:
	@echo "Available targets:"
	@echo "  all        	- Run complete pipeline (setup -> weight -> efficiency)"
	@echo "  setup      	- Create directories and copy config files"
	@echo "  weight     	- Run weight calculations"
	@echo "  efficiency 	- Run efficiency evaluation"
	@echo "  clean-output	- Remove output files but keep configs"
	@echo "  help       	- Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  NAME=$(NAME) - Trial name (override with NAME=your_trial)"
	@echo ""
	@echo "Examples:"
	@echo "  make NAME=PP    - Run analysis for PP trial"
	@echo "  make NAME=OO    - Run analysis for OO trial"
	@echo ""
	@echo "Notes:"
	@echo "  - Config files are automatically modified to use correct output directories"
	@echo "  - Weights config is only populated if 'apply: True' is found in efficiency config"
	@echo "  - If weights are not needed, the weights script is skipped"

# Setup directories and copy configs
setup: $(OUTPUT_EFF) $(DEST_CONFIG_EFF) $(DEST_CONFIG_CUTSET) $(DEST_CONFIG_WEIGHT)

# Create directories
$(OUTPUT_EFF):
	@mkdir -p $@

# Copy and modify configuration files
$(DEST_CONFIG_EFF): $(SRC_CONFIG_EFF) $(DEST_CONFIG_CUTSET) | $(OUTPUT_EFF)
	@cp $< $@
	@sed -i 's|output_dir: .*|output_dir: "$(abspath $(OUTPUT_EFF))"|g' $@
	@sed -i 's|cutset: .*|cutset: "$(abspath $(DEST_CONFIG_CUTSET))"|g' $@

$(DEST_CONFIG_CUTSET): $(SRC_CONFIG_CUTSET) | $(OUTPUT_EFF)
	@cp $< $@

$(DEST_CONFIG_WEIGHT): $(SRC_CONFIG_WEIGHT) $(DEST_CONFIG_EFF) $(DEST_CONFIG_CUTSET) | $(OUTPUT_EFF)
	@if grep -q "apply: *True" $(DEST_CONFIG_EFF); then \
		cp $< $@; \
		sed -i 's|directory: .*|directory: "$(abspath $(OUTPUT_EFF))"|g' $@; \
		sed -i 's|cutset: .*|cutset: "$(abspath $(DEST_CONFIG_CUTSET))"|g' $@; \
		echo "Weights will be produced."; \
	else \
		echo "Weights will not be produced."; \
		> $@; \
	fi

# Run weights (depends on config files)
$(WEIGHT_OUTPUT): $(DEST_CONFIG_WEIGHT) $(DEST_CONFIG_CUTSET) $(WEIGHT_SCRIPT)
	@if [ -s $(DEST_CONFIG_WEIGHT) ]; then \
		echo "Running weights calculation..."; \
		cd $(OUTPUT_EFF) && python3 $(abspath $(WEIGHT_SCRIPT)) $(CONFIG_WEIGHT); \
	else \
		echo "Weights config is empty, skipping weights calculation."; \
	fi
	@touch $@

# Run efficiency evaluation (depends on weights being complete)
$(EFF_OUTPUT): $(WEIGHT_OUTPUT) $(DEST_CONFIG_EFF) $(EFF_SCRIPT)
	@cd $(OUTPUT_EFF) && python3 $(abspath $(EFF_SCRIPT)) $(CONFIG_EFF)
	@touch $@

# Convenient aliases
weight: $(WEIGHT_OUTPUT)
efficiency: $(EFF_OUTPUT)

# Alternative clean that preserves configs
clean-output:
	find $(OUTPUT_EFF) \( -name "*.done" -o -name "*.root" -o -name "*.pdf" -o -name "*.png" -o -name "*.parquet" \) -delete
	# Add specific output files to clean as needed

# Debug target to show variables
debug:
	@echo "=== Configuration Variables ==="
	@echo "NAME: $(NAME)"
	@echo "TRIAL_DIR: $(TRIAL_DIR)"
	@echo "OUTPUT_EFF: $(OUTPUT_EFF)"
	@echo ""
	@echo "=== Directory Structure ==="
	@echo "BASE_CONFIG_DIR: $(BASE_CONFIG_DIR)"
	@echo "BASE_CUTSET_DIR: $(BASE_CUTSET_DIR)"
	@echo ""
	@echo "=== Source Config Files ==="
	@echo "SRC_CONFIG_EFF: $(SRC_CONFIG_EFF)"
	@echo "SRC_CONFIG_WEIGHT: $(SRC_CONFIG_WEIGHT)"
	@echo "SRC_CONFIG_CUTSET: $(SRC_CONFIG_CUTSET)"
	@echo ""
	@echo "=== Destination Config Files ==="
	@echo "DEST_CONFIG_EFF: $(DEST_CONFIG_EFF)"
	@echo "DEST_CONFIG_WEIGHT: $(DEST_CONFIG_WEIGHT)"
	@echo "DEST_CONFIG_CUTSET: $(DEST_CONFIG_CUTSET)"
	@echo ""
	@echo "=== Scripts ==="
	@echo "EFF_SCRIPT: $(EFF_SCRIPT)"
	@echo "WEIGHT_SCRIPT: $(WEIGHT_SCRIPT)"
	@echo ""
	@echo "=== Output Files ==="
	@echo "WEIGHT_OUTPUT: $(WEIGHT_OUTPUT)"
	@echo "EFF_OUTPUT: $(EFF_OUTPUT)"
	@echo ""
	@echo "=== File Status ==="
	@if [ -f "$(DEST_CONFIG_EFF)" ]; then echo "Efficiency config: EXISTS"; else echo "Efficiency config: MISSING"; fi
	@if [ -f "$(DEST_CONFIG_WEIGHT)" ]; then \
		if [ -s "$(DEST_CONFIG_WEIGHT)" ]; then \
			echo "Weights config: EXISTS (populated)"; \
		else \
			echo "Weights config: EXISTS (empty)"; \
		fi; \
	else \
		echo "Weights config: MISSING"; \
	fi
	@if [ -f "$(DEST_CONFIG_CUTSET)" ]; then echo "Cutset config: EXISTS"; else echo "Cutset config: MISSING"; fi
	@if [ -f "$(WEIGHT_OUTPUT)" ]; then echo "Weights output: COMPLETED"; else echo "Weights output: PENDING"; fi
	@if [ -f "$(EFF_OUTPUT)" ]; then echo "Efficiency output: COMPLETED"; else echo "Efficiency output: PENDING"; fi