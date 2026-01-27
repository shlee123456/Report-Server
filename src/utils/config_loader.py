"""
Configuration file loader module.
"""
import os
import socket
import yaml
from typing import Dict, Any
from pathlib import Path


class ConfigLoader:
    """Load and manage YAML configuration files."""

    def __init__(self, config_dir: str = 'config'):
        """
        Initialize config loader.

        Args:
            config_dir: Directory containing configuration files
        """
        self.config_dir = Path(config_dir)
        self._config = None
        self._thresholds = None
        self._log_patterns = None

    def load_config(self, config_file: str = 'config.yaml') -> Dict[str, Any]:
        """
        Load main configuration file.

        Args:
            config_file: Configuration file name

        Returns:
            Configuration dictionary
        """
        config_path = self.config_dir / config_file
        with open(config_path, 'r') as f:
            self._config = yaml.safe_load(f)

        # Auto-detect hostname if set to 'auto'
        # Priority: 1. Environment variable REPORT_HOSTNAME
        #          2. Config file setting (if not 'auto')
        #          3. Auto-detection via socket.gethostname()
        env_hostname = os.environ.get('REPORT_HOSTNAME', '').strip()
        if env_hostname:
            self._config['system']['hostname'] = env_hostname
        elif self._config.get('system', {}).get('hostname') == 'auto':
            self._config['system']['hostname'] = socket.gethostname()

        # Convert relative paths to absolute
        self._resolve_paths()

        return self._config

    def load_thresholds(self, thresholds_file: str = 'thresholds.yaml') -> Dict[str, Any]:
        """
        Load threshold configuration.

        Args:
            thresholds_file: Thresholds file name

        Returns:
            Thresholds dictionary
        """
        thresholds_path = self.config_dir / thresholds_file
        with open(thresholds_path, 'r') as f:
            self._thresholds = yaml.safe_load(f)
        return self._thresholds

    def load_log_patterns(self, patterns_file: str = 'log_patterns.yaml') -> Dict[str, Any]:
        """
        Load log pattern configuration.

        Args:
            patterns_file: Log patterns file name

        Returns:
            Log patterns dictionary
        """
        patterns_path = self.config_dir / patterns_file
        with open(patterns_path, 'r') as f:
            self._log_patterns = yaml.safe_load(f)
        return self._log_patterns

    def _resolve_paths(self):
        """Convert relative paths in config to absolute paths."""
        # Get project root directory (parent of config dir)
        project_root = self.config_dir.parent

        # Resolve report output directory
        if 'report' in self._config:
            output_dir = self._config['report'].get('output_dir', 'reports')
            if not os.path.isabs(output_dir):
                self._config['report']['output_dir'] = str(project_root / output_dir)

        # Resolve storage data directory
        if 'storage' in self._config:
            data_dir = self._config['storage'].get('data_dir', 'data/metrics')
            if not os.path.isabs(data_dir):
                self._config['storage']['data_dir'] = str(project_root / data_dir)

        # Resolve logging file
        if 'logging' in self._config:
            log_file = self._config['logging'].get('file', 'logs/app.log')
            if not os.path.isabs(log_file):
                self._config['logging']['file'] = str(project_root / log_file)

    @property
    def config(self) -> Dict[str, Any]:
        """Get main configuration."""
        if self._config is None:
            self.load_config()
        return self._config

    @property
    def thresholds(self) -> Dict[str, Any]:
        """Get thresholds configuration."""
        if self._thresholds is None:
            self.load_thresholds()
        return self._thresholds

    @property
    def log_patterns(self) -> Dict[str, Any]:
        """Get log patterns configuration."""
        if self._log_patterns is None:
            self.load_log_patterns()
        return self._log_patterns
