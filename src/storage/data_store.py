"""
Data storage module for system metrics.
"""
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging


class DataStore:
    """JSON-based storage for system metrics."""

    def __init__(self, data_dir: str, retention_months: int = 12):
        """
        Initialize data store.

        Args:
            data_dir: Base directory for storing metrics
            retention_months: Number of months to retain data
        """
        self.data_dir = Path(data_dir)
        self.retention_months = retention_months
        self.logger = logging.getLogger('monitoring_system')

        # Ensure data directory exists
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def save_metrics(self, metrics: Dict[str, Any], timestamp: Optional[datetime] = None) -> str:
        """
        Save metrics to JSON file.

        Args:
            metrics: Metrics dictionary to save
            timestamp: Timestamp for the metrics (default: current time)

        Returns:
            Path to saved file
        """
        if timestamp is None:
            timestamp = datetime.now()

        # Create year/month directory structure
        year_month_dir = self.data_dir / str(timestamp.year) / f"{timestamp.month:02d}"
        year_month_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename
        filename = f"metrics_{timestamp.strftime('%Y-%m-%d')}.json"
        file_path = year_month_dir / filename

        # Add timestamp to metrics if not present
        if 'timestamp' not in metrics:
            metrics['timestamp'] = timestamp.isoformat()

        # Save to JSON
        with open(file_path, 'w') as f:
            json.dump(metrics, f, indent=2)

        self.logger.info(f"Metrics saved to {file_path}")
        return str(file_path)

    def load_metrics(self, date: datetime) -> Optional[Dict[str, Any]]:
        """
        Load metrics for a specific date.

        Args:
            date: Date to load metrics for

        Returns:
            Metrics dictionary or None if not found
        """
        year_month_dir = self.data_dir / str(date.year) / f"{date.month:02d}"
        filename = f"metrics_{date.strftime('%Y-%m-%d')}.json"
        file_path = year_month_dir / filename

        if not file_path.exists():
            self.logger.warning(f"Metrics file not found: {file_path}")
            return None

        with open(file_path, 'r') as f:
            return json.load(f)

    def load_month_metrics(self, year: int, month: int) -> List[Dict[str, Any]]:
        """
        Load all metrics for a specific month.

        Args:
            year: Year
            month: Month (1-12)

        Returns:
            List of metrics dictionaries
        """
        year_month_dir = self.data_dir / str(year) / f"{month:02d}"

        if not year_month_dir.exists():
            self.logger.warning(f"No metrics found for {year}-{month:02d}")
            return []

        metrics_list = []
        for file_path in sorted(year_month_dir.glob('metrics_*.json')):
            try:
                with open(file_path, 'r') as f:
                    metrics = json.load(f)
                    metrics_list.append(metrics)
            except Exception as e:
                self.logger.error(f"Error loading {file_path}: {e}")

        self.logger.info(f"Loaded {len(metrics_list)} metrics files for {year}-{month:02d}")
        return metrics_list

    def load_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """
        Load metrics for a date range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of metrics dictionaries
        """
        metrics_list = []
        current_date = start_date

        while current_date <= end_date:
            metrics = self.load_metrics(current_date)
            if metrics:
                metrics_list.append(metrics)
            current_date += timedelta(days=1)

        self.logger.info(f"Loaded {len(metrics_list)} metrics files for date range")
        return metrics_list

    def cleanup_old_data(self):
        """Remove data older than retention period."""
        cutoff_date = datetime.now() - timedelta(days=self.retention_months * 30)
        deleted_count = 0

        for year_dir in self.data_dir.iterdir():
            if not year_dir.is_dir():
                continue

            for month_dir in year_dir.iterdir():
                if not month_dir.is_dir():
                    continue

                try:
                    # Parse year and month from directory names
                    year = int(year_dir.name)
                    month = int(month_dir.name)
                    dir_date = datetime(year, month, 1)

                    # Delete if older than cutoff
                    if dir_date < cutoff_date:
                        import shutil
                        shutil.rmtree(month_dir)
                        deleted_count += 1
                        self.logger.info(f"Deleted old metrics: {month_dir}")
                except Exception as e:
                    self.logger.error(f"Error cleaning up {month_dir}: {e}")

        if deleted_count > 0:
            self.logger.info(f"Cleaned up {deleted_count} old metric directories")

    def get_available_months(self) -> List[tuple]:
        """
        Get list of available months with data.

        Returns:
            List of (year, month) tuples
        """
        available = []

        for year_dir in sorted(self.data_dir.iterdir()):
            if not year_dir.is_dir():
                continue

            for month_dir in sorted(year_dir.iterdir()):
                if not month_dir.is_dir():
                    continue

                try:
                    year = int(year_dir.name)
                    month = int(month_dir.name)
                    available.append((year, month))
                except ValueError:
                    continue

        return available
