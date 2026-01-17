#!/bin/bash
#
# Cron job setup script for Server Monitoring System (pyenv version)
#

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Server Monitoring System - Cron Setup (pyenv)"
echo "=========================================="
echo ""

# Get script directory and project root
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Get pyenv paths
PYENV_ROOT="${PYENV_ROOT:-$HOME/.pyenv}"
VENV_NAME=$(cat .python-version 2>/dev/null || echo "report-server")
PYTHON_BIN="$PYENV_ROOT/versions/$VENV_NAME/bin/python"
MAIN_SCRIPT="$PROJECT_ROOT/src/main.py"
CRON_LOG="$PROJECT_ROOT/logs/cron.log"

# Check if virtualenv python exists
if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}Error: pyenv virtualenv Python not found${NC}"
    echo "Expected: $PYTHON_BIN"
    echo "Run 'bash scripts/install_deps.sh' first"
    exit 1
fi

# Check if main script exists
if [ ! -f "$MAIN_SCRIPT" ]; then
    echo -e "${RED}Error: Main script not found: $MAIN_SCRIPT${NC}"
    exit 1
fi

# Ensure logs directory exists
mkdir -p logs

# Define cron jobs
CRON_COLLECT="59 23 * * * $PYTHON_BIN $MAIN_SCRIPT --collect-only >> $CRON_LOG 2>&1"
CRON_REPORT="0 2 1 * * $PYTHON_BIN $MAIN_SCRIPT --generate-report >> $CRON_LOG 2>&1"

echo "The following cron jobs will be added:"
echo ""
echo -e "${YELLOW}Daily metrics collection (23:59):${NC}"
echo "$CRON_COLLECT"
echo ""
echo -e "${YELLOW}Monthly report generation (1st of month at 02:00):${NC}"
echo "$CRON_REPORT"
echo ""

# Ask for confirmation
read -p "Do you want to add these cron jobs? (y/n): " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Cron setup cancelled${NC}"
    exit 0
fi

# Backup existing crontab
echo -e "${YELLOW}Backing up existing crontab...${NC}"
crontab -l > /tmp/crontab_backup_$(date +%Y%m%d_%H%M%S).txt 2>/dev/null || true
echo -e "${GREEN}Backup created${NC}"
echo ""

# Check if jobs already exist
echo -e "${YELLOW}Checking for existing jobs...${NC}"
EXISTING_CRON=$(crontab -l 2>/dev/null || true)

if echo "$EXISTING_CRON" | grep -q "$MAIN_SCRIPT"; then
    echo -e "${YELLOW}Warning: Similar cron jobs already exist${NC}"
    echo "Existing jobs:"
    echo "$EXISTING_CRON" | grep "$MAIN_SCRIPT"
    echo ""
    read -p "Do you want to remove existing jobs and add new ones? (y/n): " -n 1 -r
    echo ""

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        # Remove existing jobs
        CLEANED_CRON=$(echo "$EXISTING_CRON" | grep -v "$MAIN_SCRIPT" || true)
        echo "$CLEANED_CRON" | crontab -
        echo -e "${GREEN}Removed existing jobs${NC}"
    else
        echo -e "${YELLOW}Keeping existing jobs, adding new ones${NC}"
    fi
fi

# Add new cron jobs
echo -e "${YELLOW}Adding cron jobs...${NC}"
(crontab -l 2>/dev/null || true; echo "# Server Monitoring System - Daily Collection"; echo "$CRON_COLLECT"; echo "# Server Monitoring System - Monthly Report"; echo "$CRON_REPORT") | crontab -

echo -e "${GREEN}Cron jobs added successfully${NC}"
echo ""

# Display current crontab
echo "=========================================="
echo "Current crontab:"
echo "=========================================="
crontab -l
echo ""

# Test instructions
echo "=========================================="
echo -e "${GREEN}Cron Setup Complete!${NC}"
echo "=========================================="
echo ""
echo "Cron jobs have been installed:"
echo "1. Daily metrics collection at 23:59"
echo "2. Monthly report generation on 1st at 02:00"
echo ""
echo "Python executable: $PYTHON_BIN"
echo "Logs will be written to: $CRON_LOG"
echo ""
echo "To test manually:"
echo "  python src/main.py --collect-only"
echo "  python src/main.py --generate-report"
echo ""
echo "To view cron logs:"
echo "  tail -f $CRON_LOG"
echo ""
echo "To remove cron jobs:"
echo "  crontab -e"
echo "  (then delete the Server Monitoring System lines)"
echo ""
