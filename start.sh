#!/bin/bash

# Get the directory of the script
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
#
# # Change to the script's directory
cd "$SCRIPT_DIR"
#
# # Print current directory to verify
echo "Current directory: $(pwd)"

source venv/bin/activate
cd src && python3 push_core_price.py
