#!/bin/bash
# ============================================================================
# OBS Digital Signage Automation System - Ubuntu/Linux Start Script
# ============================================================================

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo ""
echo "===================================================================="
echo " OBS Digital Signage Automation System"
echo "===================================================================="
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${RED}[ERROR]${NC} Virtual environment not found"
    echo ""
    echo "Please run the installation script first:"
    echo "  ./install.sh"
    echo ""
    exit 1
fi

# Activate virtual environment
echo -e "${GREEN}[1/2]${NC} Activating virtual environment..."
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}[ERROR]${NC} Failed to activate virtual environment"
    exit 1
fi

# Set environment to use production config
export DIGITAL_SIGNAGE_ENV=ubuntu_prod

# Run the application
echo -e "${GREEN}[2/2]${NC} Starting Digital Signage System..."
echo ""
python src/main.py

# Deactivate virtual environment on exit
deactivate
