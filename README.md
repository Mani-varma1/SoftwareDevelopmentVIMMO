# For Documentation manual please visit [this page](https://softwaredevelopmentvimmo.readthedocs.io/en/latest/)

# SoftwareDevelopmentVIMMO

# VIMMO

A Flask-based API application for panel data analysis.

## Installation

### Prerequisites

- Conda (Miniconda or Anaconda)
- Git.

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
pip install -e .[test]
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


## Version Update
Use after git commit -m "message"
```bash
# Patch version (0.1.0 → 0.1.1) 
bumpversion patch

# Minor version (0.1.0 → 0.2.0):
bumpversion minor

# Major version (0.1.0 → 1.0.0):
bumpversion major
```

## Docker
```bash
# to run docker make sure you are in route directory of the project
cd <your_file_path>/SoftwareDevelopmentVIMMO

# make sure your docker daemon is running if you are on mac/windows use docker desktop
  
# if you are on linux use
sudo systemctl start docker

# to build the image
docker-compose build

# to run the container 
docker-compose up
````

## Testing

In root directory (<path>/SoftwareDevelopmentVIMMO) :
Testing requires an instance of the application to be running as it checks for various responses
Please run the App in a seperate terminal or have an instance of Docker running in the background
```bash
pytest #Tests everything

# for extra debugging purposes use 
pytest -s # this prints out some of the info we recieve and should only be used for debugging purposes e.g, change in panelapp or variant validator.

# To test just integration
pytest -m integration

# To test just unittest modules
 pytest -m "not integration"
 #Note: this does not require an instance of the app to run as it mocks responses with dummy data
```

how to exit

