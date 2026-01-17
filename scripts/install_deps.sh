#!/bin/bash
#
# Dependency installation script for Server Monitoring System
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Server Monitoring System - Dependency Setup"
echo "=========================================="
echo ""

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check Python version
echo -e "${YELLOW}Checking Python version...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo -e "${GREEN}Found Python $PYTHON_VERSION${NC}"
echo ""

# Check if pip is installed
echo -e "${YELLOW}Checking pip...${NC}"
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed${NC}"
    echo "Install pip using: sudo apt-get install python3-pip"
    exit 1
fi
echo -e "${GREEN}pip3 is installed${NC}"
echo ""

# Create virtual environment
echo -e "${YELLOW}Creating virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}Virtual environment created${NC}"
else
    echo -e "${GREEN}Virtual environment already exists${NC}"
fi
echo ""

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate

# Upgrade pip
echo -e "${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
echo ""

# Install dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install -r requirements.txt
echo -e "${GREEN}Dependencies installed successfully${NC}"
echo ""

# Check for system dependencies
echo -e "${YELLOW}Checking system dependencies...${NC}"

# Check if user is in adm group (needed for log access)
if ! groups | grep -q "\badm\b"; then
    echo -e "${YELLOW}Warning: Current user is not in 'adm' group${NC}"
    echo "Log file access may be limited."
    echo "To add user to adm group, run:"
    echo "  sudo usermod -aG adm \$USER"
    echo "Then log out and log back in."
    echo ""
fi

# Create required directories
echo -e "${YELLOW}Creating required directories...${NC}"
mkdir -p data/metrics
mkdir -p reports
mkdir -p logs
echo -e "${GREEN}Directories created${NC}"
echo ""

# Make scripts executable
echo -e "${YELLOW}Making scripts executable...${NC}"
chmod +x scripts/*.sh
chmod +x src/main.py
echo -e "${GREEN}Scripts are now executable${NC}"
echo ""

# Summary
echo "=========================================="
echo -e "${GREEN}Installation Complete!${NC}"
echo "=========================================="
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate"
echo "2. Test metrics collection: python src/main.py --collect-only"
echo "3. Setup cron jobs: bash scripts/setup_cron.sh"
echo ""
echo "For log access, ensure your user is in the 'adm' group:"
echo "  sudo usermod -aG adm \$USER"
echo "  (then log out and log back in)"
echo ""
