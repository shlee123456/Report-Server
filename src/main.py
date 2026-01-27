#!/usr/bin/env python3
"""
Main entry point for the Ubuntu Server Monitoring & Reporting System.
"""
import argparse
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.utils.logger import setup_logger
from src.utils.config_loader import ConfigLoader
from src.storage.data_store import DataStore
from src.collectors.system_monitor import SystemMonitor
from src.collectors.log_analyzer import LogAnalyzer
from src.analyzers.metrics_analyzer import MetricsAnalyzer
from src.analyzers.threshold_checker import ThresholdChecker
from src.analyzers.recommendation_engine import RecommendationEngine
from src.reporters.chart_builder import ChartBuilder
from src.reporters.table_builder import TableBuilder
from src.reporters.pdf_generator import PDFGenerator


def collect_metrics(config, logger):
    """
    Collect system metrics and save to storage.

    Args:
        config: Configuration dictionary
        logger: Logger instance

    Returns:
        True if successful, False otherwise
    """
    try:
        logger.info("Starting metrics collection")

        # Initialize components
        monitor = SystemMonitor()
        data_store = DataStore(
            config['storage']['data_dir'],
            config['collection']['retention_months']
        )

        # Collect metrics
        metrics = monitor.collect_all_metrics()

        # Save metrics
        saved_path = data_store.save_metrics(metrics)
        logger.info(f"Metrics saved successfully: {saved_path}")

        # Cleanup old data
        data_store.cleanup_old_data()

        return True

    except Exception as e:
        logger.error(f"Error during metrics collection: {e}", exc_info=True)
        return False


def generate_report(config, thresholds, log_patterns, logger, year=None, month=None):
    """
    Generate monthly PDF report.

    Args:
        config: Configuration dictionary
        thresholds: Thresholds configuration
        log_patterns: Log patterns configuration
        logger: Logger instance
        year: Report year (default: previous month)
        month: Report month (default: previous month)

    Returns:
        True if successful, False otherwise
    """
    try:
        # Determine report period (default to previous month)
        if year is None or month is None:
            today = datetime.now()
            first_of_month = today.replace(day=1)
            last_month = first_of_month - timedelta(days=1)
            year = last_month.year
            month = last_month.month

        logger.info(f"Generating report for {year}-{month:02d}")

        # Initialize components
        data_store = DataStore(
            config['storage']['data_dir'],
            config['collection']['retention_months']
        )

        # Load metrics for the month
        metrics_list = data_store.load_month_metrics(year, month)
        if not metrics_list:
            logger.warning(f"No metrics found for {year}-{month:02d}")
            return False

        logger.info(f"Loaded {len(metrics_list)} days of metrics")

        # Analyze metrics
        analyzer = MetricsAnalyzer()
        analysis = analyzer.analyze_monthly_metrics(metrics_list)
        summary = analyzer.get_summary_statistics(analysis)

        # Analyze logs
        log_analyzer = LogAnalyzer(config['logs'], log_patterns)
        log_analysis = log_analyzer.analyze_all_logs()

        # Check thresholds
        threshold_checker = ThresholdChecker(thresholds)
        violations = threshold_checker.check_all_thresholds(analysis, log_analysis)

        # Generate recommendations
        rec_engine = RecommendationEngine()
        recommendations = rec_engine.generate_recommendations(
            analysis, violations, log_analysis
        )

        # Build charts
        logger.info("Building charts")
        chart_builder = ChartBuilder()
        charts = {
            'cpu_chart': chart_builder.create_cpu_usage_chart(
                metrics_list, thresholds.get('cpu')
            ),
            'memory_chart': chart_builder.create_memory_usage_chart(
                metrics_list, thresholds.get('memory')
            ),
            'disk_chart': chart_builder.create_disk_usage_chart(
                analysis.get('disk', {}), thresholds.get('disk')
            )
        }

        # Build tables
        logger.info("Building tables")
        table_builder = TableBuilder()
        tables = {
            'summary_table': table_builder.build_summary_table(summary),
            'daily_usage_table': table_builder.build_daily_usage_table(metrics_list),
            'cpu_stats_table': table_builder.build_cpu_stats_table(analysis.get('cpu', {})),
            'memory_stats_table': table_builder.build_memory_stats_table(analysis.get('memory', {})),
            'disk_stats_table': table_builder.build_disk_stats_table(analysis.get('disk', {})),
            'violations_table': table_builder.build_violations_table(violations),
            'log_summary_table': table_builder.build_log_summary_table(log_analysis),
            'recommendations_table': table_builder.build_recommendations_table(recommendations)
        }

        # Generate PDF
        logger.info("Generating PDF report")
        hostname = config['system']['hostname']
        filename = config['report']['filename_format'].format(
            hostname=hostname,
            year=year,
            month=f"{month:02d}"
        )
        output_dir = config['report']['output_dir']
        # Create year/month directory structure like metrics
        output_path = os.path.join(output_dir, str(year), f"{month:02d}", filename)

        pdf_gen = PDFGenerator(output_path)
        pdf_gen.create_complete_report(
            hostname=hostname,
            year=year,
            month=month,
            metrics_list=metrics_list,
            analysis=analysis,
            log_analysis=log_analysis,
            violations=violations,
            recommendations=recommendations,
            charts=charts,
            tables=tables
        )

        logger.info(f"Report generated successfully: {output_path}")
        print(f"Report generated: {output_path}")

        return True

    except Exception as e:
        logger.error(f"Error generating report: {e}", exc_info=True)
        return False


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Ubuntu Server Monitoring & Reporting System'
    )

    parser.add_argument(
        '--collect-only',
        action='store_true',
        help='Collect metrics only (no report generation)'
    )

    parser.add_argument(
        '--generate-report',
        action='store_true',
        help='Generate monthly report only (no metrics collection)'
    )

    parser.add_argument(
        '--year',
        type=int,
        help='Report year (default: previous month)'
    )

    parser.add_argument(
        '--month',
        type=int,
        help='Report month (1-12, default: previous month)'
    )

    parser.add_argument(
        '--config-dir',
        default='config',
        help='Configuration directory (default: config)'
    )

    args = parser.parse_args()

    # Load configuration
    try:
        config_loader = ConfigLoader(args.config_dir)
        config = config_loader.load_config()
        thresholds = config_loader.load_thresholds()
        log_patterns = config_loader.load_log_patterns()
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return 1

    # Setup logger
    logger = setup_logger(
        log_file=config['logging']['file'],
        level=config['logging']['level'],
        max_bytes=config['logging'].get('max_bytes', 10485760),
        backup_count=config['logging'].get('backup_count', 5)
    )

    logger.info("=" * 60)
    logger.info("Server Monitoring System Starting")
    logger.info("=" * 60)

    # Execute based on arguments
    success = True

    if args.collect_only:
        success = collect_metrics(config, logger)

    elif args.generate_report:
        success = generate_report(
            config, thresholds, log_patterns, logger,
            args.year, args.month
        )

    else:
        # Default: both collect and generate report
        logger.info("Running full workflow: collect + report")
        success = collect_metrics(config, logger)
        if success:
            success = generate_report(
                config, thresholds, log_patterns, logger,
                args.year, args.month
            )

    logger.info("=" * 60)
    if success:
        logger.info("Completed successfully")
        return 0
    else:
        logger.error("Completed with errors")
        return 1


if __name__ == '__main__':
    sys.exit(main())
