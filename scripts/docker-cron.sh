#!/bin/bash
# Docker Cron Scheduler for Report Server
# This script runs inside the Docker container to schedule periodic tasks

set -e

echo "Starting Report Server Cron Scheduler..."
echo "Container timezone: $(date)"

# Function to run metrics collection
collect_metrics() {
    echo "[$(date)] Running metrics collection..."
    cd /app
    python src/main.py --collect-only >> logs/cron.log 2>&1
    echo "[$(date)] Metrics collection completed"
}

# Function to generate monthly report
generate_report() {
    echo "[$(date)] Generating monthly report..."
    cd /app
    python src/main.py --generate-report >> logs/cron.log 2>&1
    echo "[$(date)] Report generation completed"
}

# Initialize cron log
touch logs/cron.log

# Main loop - check every minute for scheduled times
while true; do
    current_hour=$(date +%H)
    current_minute=$(date +%M)
    current_day=$(date +%d)

    # Daily metrics collection at 23:59
    if [ "$current_hour" = "23" ] && [ "$current_minute" = "59" ]; then
        collect_metrics
        # Sleep for 2 minutes to avoid running twice
        sleep 120
    fi

    # Monthly report generation on 1st day at 02:00
    if [ "$current_day" = "01" ] && [ "$current_hour" = "02" ] && [ "$current_minute" = "00" ]; then
        generate_report
        # Sleep for 2 minutes to avoid running twice
        sleep 120
    fi

    # Sleep for 50 seconds before next check
    sleep 50
done
