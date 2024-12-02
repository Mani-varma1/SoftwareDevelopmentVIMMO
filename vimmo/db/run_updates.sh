#!/bin/bash
# Find the directory where this script is located
script_dir=$(dirname "$(realpath "$0")")

# Find the root of the Git repository by tracing up from the script's directory
repo_root=$(git -C "$script_dir" rev-parse --show-toplevel 2>/dev/null)

# If not in a git repo, exit with an error message
if [ $? -ne 0 ]; then
    echo "Error: This script must be run from within a Git repository."
    exit 1
fi

# Run the Python script using the dynamic repo root path
python "$repo_root/vimmo/db/weekly_update.py"