#!/bin/bash

# Get the absolute path to the current directory (where the script is being run)
current_dir=$(pwd)

# Find the absolute path to the root of the cloned repo (assuming .git exists at the root)
repo_dir=$(git -C "$current_dir" rev-parse --show-toplevel 2>/dev/null)

# If the repo directory cannot be determined, exit
if [ -z "$repo_dir" ]; then
  echo "Error: Unable to determine the root directory of the repository."
  exit 1
fi

# Ask the user for the frequency
echo "How often do you want the script to run?"
echo "1. Every minute"
echo "2. Every day"
echo "3. Every week"
echo "4. Every month"

read -p "Choose an option [1-4]: " choice

# Define the cron job schedule based on user input
case $choice in
  1)
    cron_schedule="* * * * *"  # Every minute
    schedule_text="Every minute"
    ;;
  2)
    cron_schedule="0 0 * * *"  # Every day at midnight
    schedule_text="Every day at midnight"
    ;;
  3)
    cron_schedule="0 0 * * 0"  # Every week on Sunday at midnight
    schedule_text="Every week at midnight (Sunday)"
    ;;
  4)
    cron_schedule="0 0 1 * *"  # Every month on the 1st at midnight
    schedule_text="Every month at midnight (1st)"
    ;;
  *)
    echo "Invalid option, exiting."
    exit 1
    ;;
esac

# Define the script and log file paths relative to the repo root directory
script_path="$repo_dir/vimmo/db/run_updates.sh"   # Adjust to the actual path within the repo
log_file="$repo_dir/vimmo/db/logs/cron_panel_updates.log"  # Adjust the log file path

# Ensure the logs directory exists
mkdir -p "$(dirname "$log_file")"

# Remove the old cron job (if exists) - we assume it's already using the same script path
crontab -l | grep -v "$script_path" | crontab -

# Find the user's Conda installation path dynamically
if command -v conda &> /dev/null
then
    conda_path=$(dirname "$(which conda)")   # Get the directory of the Conda executable
else
    echo "Error: Conda is not installed or not in the PATH."
    exit 1
fi

# Set up the new cron job, including the steps to source Conda, activate the environment, and execute the script
(crontab -l 2>/dev/null; echo "$cron_schedule cd $repo_dir && /bin/bash -c 'source $conda_path/../etc/profile.d/conda.sh && conda activate VIMMO && /bin/bash $script_path >> $log_file 2>&1'") | crontab -

# Output confirmation with human-readable schedule
echo "Cron job updated to run: $schedule_text"
echo "Log file will be saved to: $log_file"