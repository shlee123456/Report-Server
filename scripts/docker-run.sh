#!/bin/bash
# Helper script to run Report Server in Docker
# Usage: ./scripts/docker-run.sh [OPTIONS]

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=====================================${NC}"
echo -e "${BLUE}Report Server - Docker Runner${NC}"
echo -e "${BLUE}=====================================${NC}"
echo ""

# Parse command line arguments
ACTION=${1:-"help"}

case "$ACTION" in
    build)
        echo -e "${GREEN}Building Docker image...${NC}"
        docker-compose build
        echo -e "${GREEN}Build completed!${NC}"
        ;;

    collect)
        echo -e "${GREEN}Running metrics collection...${NC}"
        docker-compose run --rm report-server python src/main.py --collect-only
        ;;

    report)
        echo -e "${GREEN}Generating monthly report...${NC}"
        docker-compose run --rm report-server python src/main.py --generate-report
        ;;

    report-month)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo -e "${YELLOW}Usage: $0 report-month YEAR MONTH${NC}"
            exit 1
        fi
        YEAR=$2
        MONTH=$3
        echo -e "${GREEN}Generating report for ${YEAR}-${MONTH}...${NC}"
        docker-compose run --rm report-server python src/main.py --generate-report --year "$YEAR" --month "$MONTH"
        ;;

    start-cron)
        echo -e "${GREEN}Starting cron scheduler...${NC}"
        docker-compose up -d report-server-cron
        echo -e "${GREEN}Cron scheduler started. Check logs with: $0 logs-cron${NC}"
        ;;

    stop-cron)
        echo -e "${GREEN}Stopping cron scheduler...${NC}"
        docker-compose stop report-server-cron
        docker-compose rm -f report-server-cron
        ;;

    logs)
        echo -e "${GREEN}Showing application logs...${NC}"
        tail -f logs/app.log
        ;;

    logs-cron)
        echo -e "${GREEN}Showing cron logs...${NC}"
        docker-compose logs -f report-server-cron
        ;;

    shell)
        echo -e "${GREEN}Starting interactive shell...${NC}"
        docker-compose run --rm report-server /bin/bash
        ;;

    clean)
        echo -e "${YELLOW}Cleaning up Docker containers and images...${NC}"
        docker-compose down
        docker rmi report-server_report-server 2>/dev/null || true
        echo -e "${GREEN}Cleanup completed!${NC}"
        ;;

    help|*)
        echo "Usage: $0 {command} [options]"
        echo ""
        echo "Commands:"
        echo "  build           - Build Docker image"
        echo "  collect         - Collect metrics once"
        echo "  report          - Generate report for previous month"
        echo "  report-month    - Generate report for specific month (requires YEAR MONTH)"
        echo "  start-cron      - Start scheduled cron service"
        echo "  stop-cron       - Stop scheduled cron service"
        echo "  logs            - Show application logs"
        echo "  logs-cron       - Show cron scheduler logs"
        echo "  shell           - Start interactive shell in container"
        echo "  clean           - Remove containers and images"
        echo "  help            - Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0 build"
        echo "  $0 collect"
        echo "  $0 report"
        echo "  $0 report-month 2026 1"
        echo "  $0 start-cron"
        ;;
esac

echo ""
