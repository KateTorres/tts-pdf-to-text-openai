#!/bin/bash
# Bash script to run the PDF extraction script

# Navigate to the script directory (assumes the script is in the same folder as this Bash file)
cd "$(dirname "$0")"

# Check if Python is installed
if ! command -v python3 &> /dev/null
then
    echo "Python3 is not installed or not in PATH. Please install Python3 and try again."
    exit 1
fi

# Run the main Python script
echo "Running PDF Extraction..."
python3 main.py

# Keep terminal open (optional, remove 'read -p' if not needed)
read -p "Press Enter to exit..."
