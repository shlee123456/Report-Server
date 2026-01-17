"""
Chart builder module for generating visualizations.
"""
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server environments
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
from typing import Dict, List, Any, Optional
import logging
import io


class ChartBuilder:
    """Build charts for PDF reports using matplotlib."""

    def __init__(self):
        """Initialize chart builder."""
        self.logger = logging.getLogger('monitoring_system')

        # Set default style
        plt.style.use('seaborn-v0_8-darkgrid')

    def create_cpu_usage_chart(
        self,
        metrics_list: List[Dict[str, Any]],
        thresholds: Dict[str, Any] = None
    ) -> bytes:
        """
        Create CPU usage time series chart.

        Args:
            metrics_list: List of metrics dictionaries
            thresholds: CPU thresholds for reference lines

        Returns:
            Chart image as bytes
        """
        try:
            dates = []
            cpu_usage = []

            for metrics in metrics_list:
                timestamp = metrics.get('timestamp')
                if timestamp:
                    dates.append(datetime.fromisoformat(timestamp))

                cpu_data = metrics.get('cpu', {})
                usage = cpu_data.get('usage_percent')
                if usage is not None:
                    cpu_usage.append(usage)

            if not dates or not cpu_usage:
                self.logger.warning("No CPU data to plot")
                return self._create_no_data_chart("CPU Usage")

            fig, ax = plt.subplots(figsize=(10, 5))

            # Plot CPU usage
            ax.plot(dates, cpu_usage, linewidth=2, color='#2E86AB', label='CPU Usage')

            # Add threshold lines if provided
            if thresholds:
                warning_threshold = thresholds.get('warning', {}).get('avg_usage')
                critical_threshold = thresholds.get('critical', {}).get('avg_usage')

                if warning_threshold:
                    ax.axhline(y=warning_threshold, color='#F77F00', linestyle='--',
                              linewidth=1.5, label=f'Warning ({warning_threshold}%)')
                if critical_threshold:
                    ax.axhline(y=critical_threshold, color='#D62828', linestyle='--',
                              linewidth=1.5, label=f'Critical ({critical_threshold}%)')

            # Formatting
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('CPU Usage (%)', fontsize=12)
            ax.set_title('CPU Usage Over Time', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left')

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)

            plt.tight_layout()

            # Save to bytes
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)

            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating CPU chart: {e}")
            return self._create_error_chart("CPU Usage Chart")

    def create_memory_usage_chart(
        self,
        metrics_list: List[Dict[str, Any]],
        thresholds: Dict[str, Any] = None
    ) -> bytes:
        """
        Create memory usage time series chart.

        Args:
            metrics_list: List of metrics dictionaries
            thresholds: Memory thresholds for reference lines

        Returns:
            Chart image as bytes
        """
        try:
            dates = []
            ram_usage = []
            swap_usage = []

            for metrics in metrics_list:
                timestamp = metrics.get('timestamp')
                if timestamp:
                    dates.append(datetime.fromisoformat(timestamp))

                mem_data = metrics.get('memory', {})
                ram = mem_data.get('ram', {}).get('percent')
                swap = mem_data.get('swap', {}).get('percent')

                if ram is not None:
                    ram_usage.append(ram)
                if swap is not None:
                    swap_usage.append(swap)

            if not dates or not ram_usage:
                self.logger.warning("No memory data to plot")
                return self._create_no_data_chart("Memory Usage")

            fig, ax = plt.subplots(figsize=(10, 5))

            # Plot RAM usage
            ax.plot(dates, ram_usage, linewidth=2, color='#2E86AB', label='RAM Usage')

            # Plot SWAP usage if available
            if swap_usage and len(swap_usage) == len(dates):
                ax.plot(dates, swap_usage, linewidth=2, color='#A23B72',
                       label='SWAP Usage', linestyle=':')

            # Add threshold lines if provided
            if thresholds:
                warning_threshold = thresholds.get('warning', {}).get('ram_usage')
                critical_threshold = thresholds.get('critical', {}).get('ram_usage')

                if warning_threshold:
                    ax.axhline(y=warning_threshold, color='#F77F00', linestyle='--',
                              linewidth=1.5, label=f'Warning ({warning_threshold}%)')
                if critical_threshold:
                    ax.axhline(y=critical_threshold, color='#D62828', linestyle='--',
                              linewidth=1.5, label=f'Critical ({critical_threshold}%)')

            # Formatting
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Memory Usage (%)', fontsize=12)
            ax.set_title('Memory Usage Over Time', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3)
            ax.legend(loc='upper left')

            # Format x-axis dates
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)

            plt.tight_layout()

            # Save to bytes
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)

            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating memory chart: {e}")
            return self._create_error_chart("Memory Usage Chart")

    def create_disk_usage_chart(
        self,
        disk_analysis: Dict[str, Any],
        thresholds: Dict[str, Any] = None
    ) -> bytes:
        """
        Create disk usage bar chart.

        Args:
            disk_analysis: Disk analysis dictionary
            thresholds: Disk thresholds for reference lines

        Returns:
            Chart image as bytes
        """
        try:
            mountpoints = []
            usage_values = []

            for mountpoint, stats in disk_analysis.items():
                usage_percent = stats.get('usage_percent', {})
                avg_usage = usage_percent.get('mean')

                if avg_usage is not None:
                    mountpoints.append(mountpoint)
                    usage_values.append(avg_usage)

            if not mountpoints:
                self.logger.warning("No disk data to plot")
                return self._create_no_data_chart("Disk Usage")

            fig, ax = plt.subplots(figsize=(10, 5))

            # Color bars based on usage
            colors = []
            warning_threshold = thresholds.get('warning', {}).get('usage', 80) if thresholds else 80
            critical_threshold = thresholds.get('critical', {}).get('usage', 90) if thresholds else 90

            for usage in usage_values:
                if usage >= critical_threshold:
                    colors.append('#D62828')  # Red
                elif usage >= warning_threshold:
                    colors.append('#F77F00')  # Orange
                else:
                    colors.append('#2E86AB')  # Blue

            # Create bar chart
            bars = ax.bar(mountpoints, usage_values, color=colors, alpha=0.8)

            # Add value labels on bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=10)

            # Add threshold lines
            if thresholds:
                if warning_threshold:
                    ax.axhline(y=warning_threshold, color='#F77F00', linestyle='--',
                              linewidth=1.5, label=f'Warning ({warning_threshold}%)')
                if critical_threshold:
                    ax.axhline(y=critical_threshold, color='#D62828', linestyle='--',
                              linewidth=1.5, label=f'Critical ({critical_threshold}%)')

            # Formatting
            ax.set_xlabel('Mountpoint', fontsize=12)
            ax.set_ylabel('Disk Usage (%)', fontsize=12)
            ax.set_title('Average Disk Usage by Partition', fontsize=14, fontweight='bold')
            ax.set_ylim(0, 100)
            ax.grid(True, alpha=0.3, axis='y')
            ax.legend(loc='upper right')
            plt.xticks(rotation=45, ha='right')

            plt.tight_layout()

            # Save to bytes
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)

            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating disk chart: {e}")
            return self._create_error_chart("Disk Usage Chart")

    def _fig_to_bytes(self, fig) -> bytes:
        """
        Convert matplotlib figure to bytes.

        Args:
            fig: Matplotlib figure

        Returns:
            Image as bytes
        """
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=100, bbox_inches='tight')
        buf.seek(0)
        return buf.read()

    def _create_no_data_chart(self, title: str) -> bytes:
        """
        Create a placeholder chart when no data is available.

        Args:
            title: Chart title

        Returns:
            Chart image as bytes
        """
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, 'No Data Available',
               ha='center', va='center', fontsize=16, color='gray')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        img_bytes = self._fig_to_bytes(fig)
        plt.close(fig)

        return img_bytes

    def _create_error_chart(self, title: str) -> bytes:
        """
        Create an error placeholder chart.

        Args:
            title: Chart title

        Returns:
            Chart image as bytes
        """
        fig, ax = plt.subplots(figsize=(10, 5))
        ax.text(0.5, 0.5, 'Error Creating Chart',
               ha='center', va='center', fontsize=16, color='red')
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold')

        plt.tight_layout()
        img_bytes = self._fig_to_bytes(fig)
        plt.close(fig)

        return img_bytes
