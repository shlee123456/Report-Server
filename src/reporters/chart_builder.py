"""
Chart builder module for generating modern dashboard-style visualizations.
게이지 차트, 도넛 차트, 트렌드 라인 등 대시보드 스타일 차트 생성
"""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Circle, Wedge, Rectangle, FancyBboxPatch
import matplotlib.dates as mdates
import matplotlib.font_manager as fm
import numpy as np
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import logging
import io
import platform
import os


class ChartBuilder:
    """Build modern dashboard-style charts for PDF reports."""

    # 모던 컬러 팔레트
    COLORS = {
        'primary': '#0066CC',
        'success': '#00A86B',
        'warning': '#FFB020',
        'danger': '#E53935',
        'info': '#0891B2',
        'purple': '#7C3AED',
        'background': '#F5F7FA',
        'card': '#FFFFFF',
        'text': '#1A1A2E',
        'muted': '#6B7280',
        'light': '#E5E7EB',
        'border': '#D1D5DB',
    }

    def __init__(self):
        """Initialize chart builder with Korean font."""
        self.logger = logging.getLogger('monitoring_system')
        self._setup_korean_font()
        self._setup_style()

    def _setup_korean_font(self):
        """Setup Korean font for matplotlib."""
        font_paths = []
        
        if platform.system() == 'Darwin':  # macOS
            font_paths = [
                '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
                '/Library/Fonts/AppleGothic.ttf',
            ]
        elif platform.system() == 'Linux':
            font_paths = [
                '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
            ]
        else:  # Windows
            font_paths = [
                'C:/Windows/Fonts/malgun.ttf',
            ]

        font_path_found = None
        for font_path in font_paths:
            if os.path.exists(font_path):
                font_path_found = font_path
                break

        if font_path_found:
            try:
                fm.fontManager.addfont(font_path_found)
                font_prop = fm.FontProperties(fname=font_path_found)
                self.font_name = font_prop.get_name()
                plt.rcParams['font.family'] = self.font_name
                self.logger.info(f"Korean font loaded: {font_path_found}")
            except Exception as e:
                self.logger.warning(f"Failed to load font: {e}")
                self.font_name = 'DejaVu Sans'
        else:
            self.font_name = 'DejaVu Sans'

        plt.rcParams['axes.unicode_minus'] = False

    def _setup_style(self):
        """Setup modern chart style."""
        plt.rcParams.update({
            'font.family': self.font_name,
            'figure.facecolor': self.COLORS['background'],
            'axes.facecolor': self.COLORS['card'],
            'axes.edgecolor': self.COLORS['border'],
            'axes.labelcolor': self.COLORS['text'],
            'axes.titlecolor': self.COLORS['text'],
            'xtick.color': self.COLORS['muted'],
            'ytick.color': self.COLORS['muted'],
            'grid.color': self.COLORS['light'],
            'grid.linewidth': 0.5,
            'axes.titlesize': 14,
            'axes.labelsize': 10,
            'xtick.labelsize': 9,
            'ytick.labelsize': 9,
            'legend.fontsize': 9,
            'axes.unicode_minus': False,
            'axes.spines.top': False,
            'axes.spines.right': False,
        })

    def create_gauge_chart(
        self,
        value: float,
        title: str,
        thresholds: Dict[str, float] = None
    ) -> bytes:
        """
        Create a semicircular gauge chart.

        Args:
            value: Current value (0-100)
            title: Chart title
            thresholds: Warning/critical thresholds

        Returns:
            Chart image as bytes
        """
        try:
            fig, ax = plt.subplots(figsize=(4, 3), subplot_kw={'aspect': 'equal'})
            fig.patch.set_facecolor(self.COLORS['card'])
            ax.set_facecolor(self.COLORS['card'])

            # 게이지 설정
            warning_threshold = thresholds.get('warning', 70) if thresholds else 70
            critical_threshold = thresholds.get('critical', 85) if thresholds else 85

            # 배경 아크
            theta1, theta2 = 180, 0
            
            # 구간별 색상 아크 그리기
            segments = [
                (180, 180 - (warning_threshold / 100) * 180, self.COLORS['success']),
                (180 - (warning_threshold / 100) * 180, 180 - (critical_threshold / 100) * 180, self.COLORS['warning']),
                (180 - (critical_threshold / 100) * 180, 0, self.COLORS['danger']),
            ]

            for start, end, color in segments:
                wedge = Wedge(
                    center=(0, 0), r=1, theta1=end, theta2=start,
                    width=0.3, facecolor=color, alpha=0.3, edgecolor='none'
                )
                ax.add_patch(wedge)

            # 현재 값 아크
            value_angle = 180 - (min(value, 100) / 100) * 180
            if value >= critical_threshold:
                value_color = self.COLORS['danger']
            elif value >= warning_threshold:
                value_color = self.COLORS['warning']
            else:
                value_color = self.COLORS['success']

            value_wedge = Wedge(
                center=(0, 0), r=1, theta1=value_angle, theta2=180,
                width=0.3, facecolor=value_color, edgecolor='none'
            )
            ax.add_patch(value_wedge)

            # 중앙 값 표시
            ax.text(0, -0.1, f'{value:.1f}%', ha='center', va='center',
                   fontsize=24, fontweight='bold', color=value_color,
                   fontname=self.font_name)
            ax.text(0, -0.45, title, ha='center', va='center',
                   fontsize=11, color=self.COLORS['muted'],
                   fontname=self.font_name)

            # 눈금 표시
            for pct, label in [(0, '0'), (50, '50'), (100, '100')]:
                angle = np.radians(180 - (pct / 100) * 180)
                x = 1.15 * np.cos(angle)
                y = 1.15 * np.sin(angle)
                ax.text(x, y, label, ha='center', va='center',
                       fontsize=8, color=self.COLORS['muted'])

            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-0.7, 1.3)
            ax.axis('off')

            plt.tight_layout()
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)
            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating gauge chart: {e}")
            return self._create_error_chart(title)

    def create_donut_chart(
        self,
        data: Dict[str, float],
        title: str,
        colors: List[str] = None
    ) -> bytes:
        """
        Create a donut chart.

        Args:
            data: Dictionary of labels and values
            title: Chart title
            colors: Custom colors (optional)

        Returns:
            Chart image as bytes
        """
        try:
            fig, ax = plt.subplots(figsize=(5, 4))
            fig.patch.set_facecolor(self.COLORS['card'])
            ax.set_facecolor(self.COLORS['card'])

            labels = list(data.keys())
            sizes = list(data.values())
            
            if not colors:
                colors = [
                    self.COLORS['primary'],
                    self.COLORS['success'],
                    self.COLORS['warning'],
                    self.COLORS['danger'],
                    self.COLORS['info'],
                    self.COLORS['purple'],
                ]

            # 도넛 차트
            wedges, texts, autotexts = ax.pie(
                sizes, labels=None, autopct='%1.1f%%',
                colors=colors[:len(sizes)], startangle=90,
                wedgeprops=dict(width=0.5, edgecolor='white', linewidth=2),
                pctdistance=0.75
            )

            # 텍스트 스타일
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontsize(10)
                autotext.set_fontweight('bold')

            # 범례
            ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5),
                     fontsize=9, frameon=False)

            # 중앙 텍스트
            total = sum(sizes)
            ax.text(0, 0, f'{total:.1f}%', ha='center', va='center',
                   fontsize=18, fontweight='bold', color=self.COLORS['text'])

            ax.set_title(title, fontsize=12, fontweight='bold', 
                        color=self.COLORS['text'], pad=10)

            plt.tight_layout()
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)
            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating donut chart: {e}")
            return self._create_error_chart(title)

    def create_kpi_card_image(
        self,
        metrics: Dict[str, Any],
        analysis: Dict[str, Any]
    ) -> bytes:
        """
        Create KPI cards summary image.

        Args:
            metrics: Current metrics
            analysis: Analysis data

        Returns:
            Chart image as bytes
        """
        try:
            fig, axes = plt.subplots(1, 4, figsize=(14, 3))
            fig.patch.set_facecolor(self.COLORS['background'])

            # CPU
            cpu_usage = metrics.get('cpu', {}).get('usage_percent', 0)
            cpu_trend = analysis.get('cpu', {}).get('trend', 'stable')
            self._draw_kpi_card(axes[0], 'CPU 사용률', cpu_usage, '%', cpu_trend,
                               self.COLORS['primary'])

            # Memory
            mem_usage = metrics.get('memory', {}).get('ram', {}).get('percent', 0)
            mem_trend = analysis.get('memory', {}).get('ram', {}).get('trend', 'stable')
            self._draw_kpi_card(axes[1], '메모리 사용률', mem_usage, '%', mem_trend,
                               self.COLORS['info'])

            # Disk
            disk_data = analysis.get('disk', {})
            root_disk = disk_data.get('/', disk_data.get(list(disk_data.keys())[0] if disk_data else '/', {}))
            disk_usage = root_disk.get('usage_percent', {}).get('mean', 0) if root_disk else 0
            disk_trend = root_disk.get('trend', 'stable') if root_disk else 'stable'
            self._draw_kpi_card(axes[2], '디스크 사용률', disk_usage, '%', disk_trend,
                               self.COLORS['purple'])

            # Status
            self._draw_status_card(axes[3], '시스템 상태', 'normal')

            plt.tight_layout()
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)
            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating KPI cards: {e}")
            return self._create_error_chart("KPI Cards")

    def _draw_kpi_card(self, ax, title: str, value: float, unit: str, 
                       trend: str, color: str):
        """Draw a single KPI card."""
        ax.set_facecolor(self.COLORS['card'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # 카드 배경
        card = FancyBboxPatch(
            (0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=self.COLORS['card'], edgecolor=self.COLORS['border'],
            linewidth=1.5
        )
        ax.add_patch(card)

        # 제목
        ax.text(0.5, 0.85, title, ha='center', va='center',
               fontsize=11, color=self.COLORS['muted'], fontweight='medium')

        # 값
        ax.text(0.5, 0.5, f'{value:.1f}{unit}', ha='center', va='center',
               fontsize=28, color=color, fontweight='bold')

        # 트렌드
        trend_symbols = {'increasing': '▲', 'decreasing': '▼', 'stable': '─'}
        trend_colors = {
            'increasing': self.COLORS['danger'],
            'decreasing': self.COLORS['success'],
            'stable': self.COLORS['muted']
        }
        trend_labels = {'increasing': '증가', 'decreasing': '감소', 'stable': '안정'}
        
        symbol = trend_symbols.get(trend, '─')
        t_color = trend_colors.get(trend, self.COLORS['muted'])
        t_label = trend_labels.get(trend, '안정')
        
        ax.text(0.5, 0.18, f'{symbol} {t_label}', ha='center', va='center',
               fontsize=10, color=t_color, fontweight='medium')

        ax.axis('off')

    def _draw_status_card(self, ax, title: str, status: str):
        """Draw system status card."""
        ax.set_facecolor(self.COLORS['card'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)

        # 카드 배경
        card = FancyBboxPatch(
            (0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02,rounding_size=0.05",
            facecolor=self.COLORS['card'], edgecolor=self.COLORS['border'],
            linewidth=1.5
        )
        ax.add_patch(card)

        # 제목
        ax.text(0.5, 0.85, title, ha='center', va='center',
               fontsize=11, color=self.COLORS['muted'], fontweight='medium')

        # 상태
        status_config = {
            'normal': ('정상', self.COLORS['success'], '✓'),
            'warning': ('주의', self.COLORS['warning'], '!'),
            'critical': ('위험', self.COLORS['danger'], '✕'),
        }
        label, color, icon = status_config.get(status, ('정상', self.COLORS['success'], '✓'))
        
        ax.text(0.5, 0.5, label, ha='center', va='center',
               fontsize=24, color=color, fontweight='bold')
        ax.text(0.5, 0.18, icon, ha='center', va='center',
               fontsize=20, color=color)

        ax.axis('off')

    def create_cpu_usage_chart(
        self,
        metrics_list: List[Dict[str, Any]],
        thresholds: Dict[str, Any] = None
    ) -> bytes:
        """
        Create CPU usage time series chart with modern style.
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
                return self._create_no_data_chart("CPU 사용량")

            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor(self.COLORS['card'])
            ax.set_facecolor(self.COLORS['card'])

            # 그라데이션 영역
            ax.fill_between(dates, cpu_usage, alpha=0.15, color=self.COLORS['primary'])
            
            # 라인
            ax.plot(dates, cpu_usage, linewidth=2.5, color=self.COLORS['primary'],
                   marker='o', markersize=6, markerfacecolor='white',
                   markeredgecolor=self.COLORS['primary'], markeredgewidth=2)

            # 임계값 라인
            if thresholds:
                warning = thresholds.get('warning', {}).get('avg_usage')
                critical = thresholds.get('critical', {}).get('avg_usage')
                if warning:
                    ax.axhline(y=warning, color=self.COLORS['warning'],
                              linestyle='--', linewidth=1.5, alpha=0.8,
                              label=f'경고 ({warning}%)')
                if critical:
                    ax.axhline(y=critical, color=self.COLORS['danger'],
                              linestyle='--', linewidth=1.5, alpha=0.8,
                              label=f'위험 ({critical}%)')

            ax.set_xlabel('날짜', fontsize=10, color=self.COLORS['text'])
            ax.set_ylabel('사용률 (%)', fontsize=10, color=self.COLORS['text'])
            ax.set_title('CPU 사용률 추이', fontsize=14, fontweight='bold',
                        color=self.COLORS['text'], pad=15)
            ax.set_ylim(0, 100)
            ax.legend(loc='upper right', frameon=True, fancybox=True,
                     framealpha=0.9, edgecolor=self.COLORS['border'])
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)
            ax.grid(True, alpha=0.3, linestyle='-', color=self.COLORS['light'])

            plt.tight_layout()
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)
            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating CPU chart: {e}")
            return self._create_error_chart("CPU 사용량 차트")

    def create_memory_usage_chart(
        self,
        metrics_list: List[Dict[str, Any]],
        thresholds: Dict[str, Any] = None
    ) -> bytes:
        """
        Create memory usage time series chart with modern style.
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
                return self._create_no_data_chart("메모리 사용량")

            fig, ax = plt.subplots(figsize=(10, 4))
            fig.patch.set_facecolor(self.COLORS['card'])
            ax.set_facecolor(self.COLORS['card'])

            # RAM
            ax.fill_between(dates, ram_usage, alpha=0.15, color=self.COLORS['info'])
            ax.plot(dates, ram_usage, linewidth=2.5, color=self.COLORS['info'],
                   marker='o', markersize=6, markerfacecolor='white',
                   markeredgecolor=self.COLORS['info'], markeredgewidth=2,
                   label='RAM 사용률')

            # SWAP
            if swap_usage and len(swap_usage) == len(dates):
                ax.plot(dates, swap_usage, linewidth=2, color=self.COLORS['purple'],
                       linestyle='--', marker='s', markersize=4,
                       label='SWAP 사용률')

            # 임계값
            if thresholds:
                warning = thresholds.get('warning', {}).get('ram_usage')
                critical = thresholds.get('critical', {}).get('ram_usage')
                if warning:
                    ax.axhline(y=warning, color=self.COLORS['warning'],
                              linestyle='--', linewidth=1.5, alpha=0.8,
                              label=f'경고 ({warning}%)')
                if critical:
                    ax.axhline(y=critical, color=self.COLORS['danger'],
                              linestyle='--', linewidth=1.5, alpha=0.8,
                              label=f'위험 ({critical}%)')

            ax.set_xlabel('날짜', fontsize=10, color=self.COLORS['text'])
            ax.set_ylabel('사용률 (%)', fontsize=10, color=self.COLORS['text'])
            ax.set_title('메모리 사용률 추이', fontsize=14, fontweight='bold',
                        color=self.COLORS['text'], pad=15)
            ax.set_ylim(0, 100)
            ax.legend(loc='upper right', frameon=True, fancybox=True,
                     framealpha=0.9, edgecolor=self.COLORS['border'])
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%d'))
            plt.xticks(rotation=45)
            ax.grid(True, alpha=0.3, linestyle='-', color=self.COLORS['light'])

            plt.tight_layout()
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)
            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating memory chart: {e}")
            return self._create_error_chart("메모리 사용량 차트")

    def create_disk_usage_chart(
        self,
        disk_analysis: Dict[str, Any],
        thresholds: Dict[str, Any] = None
    ) -> bytes:
        """
        Create disk usage horizontal bar chart with modern style.
        """
        try:
            mountpoints = []
            usage_values = []

            for mountpoint, stats in disk_analysis.items():
                usage_percent = stats.get('usage_percent', {})
                avg_usage = usage_percent.get('mean')
                if avg_usage is not None:
                    display_name = mountpoint if len(mountpoint) <= 15 else '...' + mountpoint[-12:]
                    mountpoints.append(display_name)
                    usage_values.append(avg_usage)

            if not mountpoints:
                return self._create_no_data_chart("디스크 사용량")

            fig, ax = plt.subplots(figsize=(10, max(3, len(mountpoints) * 0.8)))
            fig.patch.set_facecolor(self.COLORS['card'])
            ax.set_facecolor(self.COLORS['card'])

            warning_threshold = thresholds.get('warning', {}).get('usage', 80) if thresholds else 80
            critical_threshold = thresholds.get('critical', {}).get('usage', 90) if thresholds else 90

            # 색상 결정
            bar_colors = []
            for usage in usage_values:
                if usage >= critical_threshold:
                    bar_colors.append(self.COLORS['danger'])
                elif usage >= warning_threshold:
                    bar_colors.append(self.COLORS['warning'])
                else:
                    bar_colors.append(self.COLORS['success'])

            # 배경 바
            y_pos = range(len(mountpoints))
            ax.barh(y_pos, [100] * len(mountpoints), color=self.COLORS['light'],
                   height=0.6, alpha=0.5)
            
            # 사용량 바
            bars = ax.barh(y_pos, usage_values, color=bar_colors, height=0.6,
                          edgecolor='white', linewidth=1)

            # 값 레이블
            for i, (bar, usage) in enumerate(zip(bars, usage_values)):
                ax.text(usage + 2, i, f'{usage:.1f}%', va='center',
                       fontsize=10, fontweight='bold', color=bar_colors[i])

            ax.set_yticks(y_pos)
            ax.set_yticklabels(mountpoints)
            ax.set_xlabel('사용률 (%)', fontsize=10, color=self.COLORS['text'])
            ax.set_title('디스크 사용률 (파티션별)', fontsize=14, fontweight='bold',
                        color=self.COLORS['text'], pad=15)
            ax.set_xlim(0, 110)

            # 임계값 라인
            ax.axvline(x=warning_threshold, color=self.COLORS['warning'],
                      linestyle='--', linewidth=1.5, alpha=0.8)
            ax.axvline(x=critical_threshold, color=self.COLORS['danger'],
                      linestyle='--', linewidth=1.5, alpha=0.8)

            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_color(self.COLORS['border'])
            ax.spines['left'].set_color(self.COLORS['border'])

            plt.tight_layout()
            img_bytes = self._fig_to_bytes(fig)
            plt.close(fig)
            return img_bytes

        except Exception as e:
            self.logger.error(f"Error creating disk chart: {e}")
            return self._create_error_chart("디스크 사용량 차트")

    def _fig_to_bytes(self, fig) -> bytes:
        """Convert matplotlib figure to bytes."""
        buf = io.BytesIO()
        fig.savefig(buf, format='png', dpi=150, bbox_inches='tight',
                   facecolor=fig.get_facecolor(), edgecolor='none')
        buf.seek(0)
        return buf.read()

    def _create_no_data_chart(self, title: str) -> bytes:
        """Create a placeholder chart when no data is available."""
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(self.COLORS['card'])
        ax.set_facecolor(self.COLORS['card'])
        
        ax.text(0.5, 0.55, '데이터 없음', ha='center', va='center',
               fontsize=18, color=self.COLORS['muted'], fontweight='bold')
        ax.text(0.5, 0.4, '해당 기간에 수집된 데이터가 없습니다.',
               ha='center', va='center', fontsize=11, color=self.COLORS['muted'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold',
                    color=self.COLORS['text'], pad=15)

        plt.tight_layout()
        img_bytes = self._fig_to_bytes(fig)
        plt.close(fig)
        return img_bytes

    def _create_error_chart(self, title: str) -> bytes:
        """Create an error placeholder chart."""
        fig, ax = plt.subplots(figsize=(8, 4))
        fig.patch.set_facecolor(self.COLORS['card'])
        ax.set_facecolor(self.COLORS['card'])
        
        ax.text(0.5, 0.55, '차트 생성 오류', ha='center', va='center',
               fontsize=18, color=self.COLORS['danger'], fontweight='bold')
        ax.text(0.5, 0.4, '차트를 생성하는 중 오류가 발생했습니다.',
               ha='center', va='center', fontsize=11, color=self.COLORS['muted'])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        ax.set_title(title, fontsize=14, fontweight='bold',
                    color=self.COLORS['text'], pad=15)

        plt.tight_layout()
        img_bytes = self._fig_to_bytes(fig)
        plt.close(fig)
        return img_bytes
