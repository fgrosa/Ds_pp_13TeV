###################################
# Makefile for projections and fitting
###################################

# Configuration variables
NAME ?= OO
ISDATA ?= true
BASE_CONFIG_DIR = ./configs

# Set base directory based on data type
ifeq ($(ISDATA),true)
    BASE_DIR = ./data
else
    BASE_DIR = ./MC
endif

TRIAL_DIR = $(BASE_DIR)/$(NAME)

# Output directories
OUTPUT_PROJ = $(TRIAL_DIR)/Projections
OUTPUT_FIT = $(TRIAL_DIR)/RawYields

# Configuration files (adjust names based on data type)
ifeq ($(ISDATA),true)
    CONFIG_PROJ = config_projection_data.yaml
    CONFIG_FIT = config_fit_data.yml
else
    CONFIG_PROJ = config_projection_mc.yaml
    CONFIG_FIT = config_fit_mc.yml
endif
CONFIG_CUTSET = cutset.yml

# Source configuration files
SRC_CONFIG_PROJ = $(BASE_CONFIG_DIR)/$(CONFIG_PROJ)
SRC_CONFIG_FIT = $(BASE_CONFIG_DIR)/$(CONFIG_FIT)
SRC_CONFIG_CUTSET = $(BASE_CONFIG_DIR)/$(CONFIG_CUTSET)

# Copied configuration files
DEST_CONFIG_PROJ = $(OUTPUT_PROJ)/$(CONFIG_PROJ)
DEST_CONFIG_FIT = $(OUTPUT_FIT)/$(CONFIG_FIT)
DEST_CONFIG_CUTSET = $(OUTPUT_PROJ)/$(CONFIG_CUTSET)

# Scripts (adjust paths as needed)
PROJ_SCRIPT = project_data_from_sparse.py
FIT_SCRIPT = get_raw_yields_ds_dplus_flarefly.py

# Output files (adjust based on what your scripts actually produce)
PROJ_OUTPUT = $(OUTPUT_PROJ)/projections.done
FIT_OUTPUT = $(OUTPUT_FIT)/rawYields.done

# Define the targets
.PHONY: all clean help setup

# Default target
all: setup project fit

# Help target
help:
	@echo "Available targets:"
	@echo "  all        - Run complete pipeline (setup -> project -> fit)"
	@echo "  setup      - Create directories and copy config files"
	@echo "  project    - Run projections"
	@echo "  fit        - Run fitting"
	@echo "  clean      - Remove output directories"
	@echo "  help       - Show this help message"
	@echo ""
	@echo "Variables:"
	@echo "  NAME=$(NAME) - Trial name (override with NAME=your_trial)"
	@echo "  ISDATA=$(ISDATA) - Data type flag (true for data, false for MC)"
	@echo ""
	@echo "Examples:"
	@echo "  make NAME=PP ISDATA=true    - Run data analysis for PP trial"
	@echo "  make NAME=OO ISDATA=false   - Run MC analysis for OO trial"
	@echo ""
	@echo "Note: Config files are automatically modified to use correct output directories"

# Setup directories and copy configs
setup: $(OUTPUT_PROJ) $(OUTPUT_FIT) $(DEST_CONFIG_PROJ) $(DEST_CONFIG_FIT) $(DEST_CONFIG_CUTSET)

# Create directories
$(OUTPUT_PROJ):
	mkdir -p $@

$(OUTPUT_FIT):
	mkdir -p $@

# Copy and modify configuration files
$(DEST_CONFIG_PROJ): $(SRC_CONFIG_PROJ) | $(OUTPUT_PROJ)
	cp $< $@
	sed -i 's|directory: .*|directory: "$(abspath $(OUTPUT_PROJ))"|g' $@

$(DEST_CONFIG_FIT): $(SRC_CONFIG_FIT) | $(OUTPUT_FIT)
	cp $< $@
	sed -i 's|directory: .*|directory: "$(abspath $(OUTPUT_FIT))"|g' $@

$(DEST_CONFIG_CUTSET): $(SRC_CONFIG_CUTSET) | $(OUTPUT_PROJ)
	cp $< $@

# Run projections
$(PROJ_OUTPUT): $(DEST_CONFIG_PROJ) $(DEST_CONFIG_CUTSET) $(PROJ_SCRIPT)
	cd $(OUTPUT_PROJ) && python3 $(abspath $(PROJ_SCRIPT)) $(CONFIG_PROJ)
	@touch $@

# Run fitting (depends on projections being complete)
$(FIT_OUTPUT): $(PROJ_OUTPUT) $(DEST_CONFIG_FIT) $(FIT_SCRIPT)
	cd $(OUTPUT_FIT) && python3 $(abspath $(PROJ_SCRIPT)) $(CONFIG_FIT)
	@touch $@

# Convenient aliases
project: $(PROJ_OUTPUT)
fit: $(FIT_OUTPUT)

# Clean up
clean:
	rm -rf $(TRIAL_DIR)

# Alternative clean that preserves configs
clean-output:
	find $(OUTPUT_PROJ) -name "*.done" -delete
	find $(OUTPUT_FIT) -name "*.done" -delete
	# Add specific output files to clean as needed

# Debug target to show variables
debug:
	@echo "NAME: $(NAME)"
	@echo "ISDATA: $(ISDATA)"
	@echo "BASE_DIR: $(BASE_DIR)"
	@echo "TRIAL_DIR: $(TRIAL_DIR)"
	@echo "OUTPUT_PROJ: $(OUTPUT_PROJ)"
	@echo "OUTPUT_FIT: $(OUTPUT_FIT)"
	@echo "CONFIG_PROJ: $(CONFIG_PROJ)"
	@echo "CONFIG_FIT: $(CONFIG_FIT)"
	@echo "SRC_CONFIG_PROJ: $(SRC_CONFIG_PROJ)"
	@echo "DEST_CONFIG_PROJ: $(DEST_CONFIG_PROJ)"