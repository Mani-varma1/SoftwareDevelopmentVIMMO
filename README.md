# For Documentation manual please visit [this page](https://softwaredevelopmentvimmo.readthedocs.io/en/latest/)

# SoftwareDevelopmentVIMMO

# VIMMO

A Flask-based API application for panel data analysis.

## Installation

### Prerequisites

- Conda (Miniconda or Anaconda)
- Git

### Setup Instructions

1. Clone the repository:
```bash
git clone https://github.com/yourusername/VIMMO.git
cd VIMMO
```

2. Create and activate the conda environment:
```bash
# Create the conda environment from environment.yaml
conda env create -f environment.yaml

# Activate the environment
conda activate VIMMO
```

3. Install the package:
```bash
# Install in development mode
pip install -e .
```

The package installation will automatically handle all dependencies listed in `pyproject.toml`.

### Building the Package for Production

If you want to build the distribution files:
```bash
# This will create both wheel and source distribution
python -m build
```

This will create:
- A wheel file (*.whl) in the `dist/` directory
- A source distribution (*.tar.gz) in the `dist/` directory

Install using:
```bash
# This will create both wheel and source distribution
pip install dist/*.whl
```

## Usage

After installation, you can run the API server:
```bash
# Using the console script
vimmo

# Or using the module directly
python -m vimmo.main
```

The API will be available at:
- Main API: http://127.0.0.1:5000/
- Swagger UI Documentation: http://127.0.0.1:5000/



how to exit

This is to test weebhooks

tryagain 1
