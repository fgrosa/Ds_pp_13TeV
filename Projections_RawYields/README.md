# Projections and Fitting

## Configuration

### Required Configuration Files

In the `configs/` directory you will find the necessary configuration files for both data and MC analyses that will be considered for the projection/fit. Only these config files are used, the others are there for reference:

- `config_projection_data.yaml` - Configuration for data projections
- `config_projection_mc.yaml` - Configuration for MC projections  
- `config_fit_data.yml` - Configuration for data fitting
- `config_fit_mc.yml` - Configuration for MC fitting
- `cutset.yml` - Cut set configuration

## Usage

### Basic Commands

```bash
# Run complete pipeline with default settings (NAME=OO, ISDATA=true)
make

# Run data analysis for a specific trial
make NAME=PP ISDATA=true

# Run MC analysis for a specific trial
make NAME=OO ISDATA=false

# Just setup directories and copy config files
make setup NAME=PP ISDATA=true

# Run only projections
make project NAME=PP ISDATA=true

# Run only fitting (requires projections to be completed)
make fit NAME=PP ISDATA=true
```

### Variables

- `NAME` - Trial name. Will set the output name (default: `OO`)
- `ISDATA` - Data type flag (default: `true`)
  - `true` for data analysis (uses `./data/` directory)
  - `false` for MC analysis (uses `./MC/` directory)

### Available Targets

- `all` - Run complete pipeline (setup → project → fit)
- `setup` - Create directories and copy configuration files
- `project` - Run projections
- `fit` - Run fitting (depends on projections)
- `clean-output` - Remove output files but keep configs
- `help` - Show help message with available targets and examples
- `debug` - Display all variable values for debugging

## What the Makefile Does

### 1. Setup Phase
- Creates output directories: `[data|MC]/[NAME]/Projections/` and `[data|MC]/[NAME]/RawYields/`
- Copies configuration files to appropriate directories
- **Automatically updates** `directory:` paths in config files to point to correct output locations
- Updates `data:` field in fit config to point to `projections.root`

### 2. Projection Phase
- Runs `project_data_from_sparse.py` with the projection configuration
- Combines all output ROOT files using `hadd` into `projections.root`
- Creates a completion marker file (`projections.done`)

### 3. Fitting Phase
- Runs `get_raw_yields_ds_dplus_flarefly.py` with the fit configuration
- Uses the combined `projections.root` as input
- Creates a completion marker file (`rawYields.done`)

## Cleaning Up

```bash
# Remove output files but keep config files
make clean-output NAME=PP ISDATA=true

# This removes: *.root, *.pdf, *.png, *.parquet, *.done files
```

## Examples

### Running Multiple Trials

```bash
# Data analysis for different trials
make NAME=OO ISDATA=true
make NAME=PP ISDATA=true
make NAME=PbPb ISDATA=true

# MC analysis for different trials
make NAME=OO ISDATA=false
make NAME=PP ISDATA=false
```

### Debugging

```bash
# Check variable values
make debug NAME=PP ISDATA=false

# Get help
make help
```
