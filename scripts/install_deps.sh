#!/bin/bash
#
# Dependency installation script for Server Monitoring System (pyenv version)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Server Monitoring System - Dependency Setup (pyenv)"
echo "=========================================="
echo ""

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Check if pyenv is installed
echo -e "${YELLOW}Checking pyenv...${NC}"
if ! command -v pyenv &> /dev/null; then
    echo -e "${RED}Error: pyenv is not installed${NC}"
    echo "Install pyenv first: https://github.com/pyenv/pyenv#installation"
    exit 1
fi
echo -e "${GREEN}pyenv is installed${NC}"
echo ""

# Check if pyenv-virtualenv is installed
echo -e "${YELLOW}Checking pyenv-virtualenv...${NC}"
if ! pyenv commands | grep -q virtualenv; then
    echo -e "${RED}Error: pyenv-virtualenv is not installed${NC}"
    echo "Install pyenv-virtualenv: https://github.com/pyenv/pyenv-virtualenv"
    exit 1
fi
echo -e "${GREEN}pyenv-virtualenv is installed${NC}"
echo ""

# Check .python-version file
VENV_NAME="report-server"
PYTHON_VERSION="3.11.0"

if [ -f ".python-version" ]; then
    VENV_NAME=$(cat .python-version)
    echo -e "${GREEN}Found .python-version: $VENV_NAME${NC}"
fi

# Check if virtualenv exists, create if not
echo -e "${YELLOW}Setting up pyenv virtualenv...${NC}"
if ! pyenv versions | grep -q "$VENV_NAME"; then
    echo "Creating virtualenv: $VENV_NAME"
    pyenv virtualenv $PYTHON_VERSION $VENV_NAME
    echo -e "${GREEN}Virtualenv created${NC}"
else
    echo -e "${GREEN}Virtualenv already exists: $VENV_NAME${NC}"
fi

# Set local python version
pyenv local $VENV_NAME
echo ""

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

# Check if user is in adm group (needed for log access on Linux)
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    if ! groups | grep -q "\badm\b"; then
        echo -e "${YELLOW}Warning: Current user is not in 'adm' group${NC}"
        echo "Log file access may be limited."
        echo "To add user to adm group, run:"
        echo "  sudo usermod -aG adm \$USER"
        echo "Then log out and log back in."
        echo ""
    fi
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
echo "pyenv virtualenv: $VENV_NAME"
echo "Python version: $(python --version)"
echo ""
echo "Next steps:"
echo "1. Test metrics collection: python src/main.py --collect-only"
echo "2. Setup cron jobs: bash scripts/setup_cron.sh"
echo ""
echo "For log access on Linux, ensure your user is in the 'adm' group:"
echo "  sudo usermod -aG adm \$USER"
echo "  (then log out and log back in)"
echo ""
