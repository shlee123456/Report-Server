"""
PDF report generator module using ReportLab.
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime
from typing import Dict, List, Any
import logging
import os
import io


class PDFGenerator:
    """Generate PDF reports using ReportLab."""

    def __init__(self, output_path: str):
        """
        Initialize PDF generator.

        Args:
            output_path: Path where PDF will be saved
        """
        self.output_path = output_path
        self.logger = logging.getLogger('monitoring_system')

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Initialize document
        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )

        # Get styles
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()

        # Story elements
        self.story = []

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=30,
            alignment=TA_CENTER
        ))

        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=16,
            textColor=colors.HexColor('#2E86AB'),
            spaceAfter=12,
            spaceBefore=12
        ))

        # Subsection header style
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading3'],
            fontSize=14,
            textColor=colors.HexColor('#444444'),
            spaceAfter=10,
            spaceBefore=10
        ))

    def add_cover_page(self, hostname: str, year: int, month: int):
        """
        Add cover page to report.

        Args:
            hostname: Server hostname
            year: Report year
            month: Report month
        """
        # Title
        title = Paragraph(
            f"Server Monitoring Report",
            self.styles['CustomTitle']
        )
        self.story.append(title)
        self.story.append(Spacer(1, 0.3*inch))

        # Server info
        server_info = Paragraph(
            f"<b>Server:</b> {hostname}<br/>"
            f"<b>Period:</b> {year}-{month:02d}<br/>"
            f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            self.styles['Normal']
        )
        self.story.append(server_info)
        self.story.append(PageBreak())

    def add_section(self, title: str):
        """
        Add section header.

        Args:
            title: Section title
        """
        self.story.append(Paragraph(title, self.styles['SectionHeader']))
        self.story.append(Spacer(1, 0.1*inch))

    def add_subsection(self, title: str):
        """
        Add subsection header.

        Args:
            title: Subsection title
        """
        self.story.append(Paragraph(title, self.styles['SubsectionHeader']))
        self.story.append(Spacer(1, 0.05*inch))

    def add_paragraph(self, text: str):
        """
        Add paragraph text.

        Args:
            text: Paragraph text
        """
        self.story.append(Paragraph(text, self.styles['Normal']))
        self.story.append(Spacer(1, 0.1*inch))

    def add_table(self, table_data: List[List[str]], col_widths: List[float] = None):
        """
        Add table to report.

        Args:
            table_data: Table data as list of rows
            col_widths: Column widths (optional)
        """
        if not table_data:
            return

        # Create table
        table = Table(table_data, colWidths=col_widths)

        # Style table
        table.setStyle(TableStyle([
            # Header row
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E86AB')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # Data rows
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.beige, colors.lightgrey]),
        ]))

        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))

    def add_chart(self, chart_bytes: bytes, width: float = 6*inch, height: float = 3*inch):
        """
        Add chart image to report.

        Args:
            chart_bytes: Chart image as bytes
            width: Image width
            height: Image height
        """
        try:
            # Create image from bytes
            img = Image(io.BytesIO(chart_bytes), width=width, height=height)
            self.story.append(img)
            self.story.append(Spacer(1, 0.2*inch))
        except Exception as e:
            self.logger.error(f"Error adding chart to PDF: {e}")

    def add_recommendations(self, recommendations: List[Dict[str, Any]]):
        """
        Add recommendations section with detailed formatting.

        Args:
            recommendations: List of recommendations
        """
        for i, rec in enumerate(recommendations, 1):
            priority = rec.get('priority', 'N/A').upper()
            category = rec.get('category', 'N/A')
            title = rec.get('title', 'N/A')
            description = rec.get('description', '')
            actions = rec.get('actions', [])

            # Priority color
            priority_color = colors.black
            if priority == 'CRITICAL':
                priority_color = colors.red
            elif priority == 'HIGH':
                priority_color = colors.orange
            elif priority == 'MEDIUM':
                priority_color = colors.blue

            # Recommendation header
            header_text = f"<font color='{priority_color.hexval()}'><b>{i}. [{priority}]</b></font> <b>{title}</b> ({category})"
            self.story.append(Paragraph(header_text, self.styles['Normal']))
            self.story.append(Spacer(1, 0.05*inch))

            # Description
            if description:
                self.story.append(Paragraph(description, self.styles['Normal']))
                self.story.append(Spacer(1, 0.05*inch))

            # Actions
            if actions:
                self.story.append(Paragraph("<b>Recommended Actions:</b>", self.styles['Normal']))
                for action in actions:
                    bullet_text = f"• {action}"
                    self.story.append(Paragraph(bullet_text, self.styles['Normal']))

            self.story.append(Spacer(1, 0.15*inch))

    def add_log_events(self, events: List[Dict[str, str]], max_events: int = 10):
        """
        Add log events list.

        Args:
            events: List of log event dictionaries
            max_events: Maximum number of events to display
        """
        for i, event in enumerate(events[:max_events], 1):
            message = event.get('message', 'N/A')
            timestamp = event.get('timestamp', 'Unknown')

            event_text = f"{i}. [{timestamp}] {message}"
            # Truncate long messages
            if len(event_text) > 200:
                event_text = event_text[:197] + "..."

            self.story.append(Paragraph(event_text, self.styles['Normal']))
            self.story.append(Spacer(1, 0.05*inch))

    def add_key_value_list(self, data: Dict[str, str]):
        """
        Add key-value list.

        Args:
            data: Dictionary of key-value pairs
        """
        for key, value in data.items():
            text = f"<b>{key}:</b> {value}"
            self.story.append(Paragraph(text, self.styles['Normal']))
            self.story.append(Spacer(1, 0.05*inch))

    def add_spacer(self, height: float = 0.2):
        """
        Add vertical spacer.

        Args:
            height: Spacer height in inches
        """
        self.story.append(Spacer(1, height*inch))

    def add_page_break(self):
        """Add page break."""
        self.story.append(PageBreak())

    def generate(self):
        """Build and save PDF document."""
        try:
            self.doc.build(self.story)
            self.logger.info(f"PDF report generated: {self.output_path}")
        except Exception as e:
            self.logger.error(f"Error generating PDF: {e}")
            raise

    def create_complete_report(
        self,
        hostname: str,
        year: int,
        month: int,
        metrics_list: List[Dict[str, Any]],
        analysis: Dict[str, Any],
        log_analysis: Dict[str, Any],
        violations: List[Dict[str, Any]],
        recommendations: List[Dict[str, Any]],
        charts: Dict[str, bytes],
        tables: Dict[str, List[List[str]]]
    ):
        """
        Create complete PDF report with all sections.

        Args:
            hostname: Server hostname
            year: Report year
            month: Report month
            metrics_list: List of metrics
            analysis: Metrics analysis
            log_analysis: Log analysis results
            violations: Threshold violations
            recommendations: Recommendations list
            charts: Dictionary of chart images
            tables: Dictionary of table data
        """
        # Cover page
        self.add_cover_page(hostname, year, month)

        # Executive Summary
        self.add_section("1. Executive Summary")
        summary = analysis.get('summary', {}) if isinstance(analysis, dict) else {}
        if 'summary_table' in tables:
            self.add_table(tables['summary_table'])

        # Key findings
        self.add_subsection("Key Findings")
        severity_summary = {
            'critical': sum(1 for v in violations if v.get('severity') == 'critical'),
            'warning': sum(1 for v in violations if v.get('severity') == 'warning')
        }
        self.add_paragraph(
            f"<b>Critical Issues:</b> {severity_summary['critical']}<br/>"
            f"<b>Warnings:</b> {severity_summary['warning']}<br/>"
            f"<b>Total Log Events:</b> {log_analysis.get('summary', {}).get('total_events', 0)}"
        )
        self.add_spacer()

        # CPU Analysis
        self.add_section("2. CPU Analysis")
        if 'cpu_chart' in charts:
            self.add_chart(charts['cpu_chart'])
        if 'cpu_stats_table' in tables:
            self.add_table(tables['cpu_stats_table'])
        self.add_page_break()

        # Memory Analysis
        self.add_section("3. Memory Analysis")
        if 'memory_chart' in charts:
            self.add_chart(charts['memory_chart'])
        if 'memory_stats_table' in tables:
            self.add_table(tables['memory_stats_table'])
        self.add_page_break()

        # Disk Analysis
        self.add_section("4. Disk Analysis")
        if 'disk_chart' in charts:
            self.add_chart(charts['disk_chart'])
        if 'disk_stats_table' in tables:
            self.add_table(tables['disk_stats_table'])
        self.add_page_break()

        # Log Analysis
        self.add_section("5. Log Analysis")
        if 'log_summary_table' in tables:
            self.add_table(tables['log_summary_table'])

        # Security events
        auth_log = log_analysis.get('auth_log', {})
        recent_events = auth_log.get('recent_events', [])
        if recent_events:
            self.add_subsection("Recent Security Events")
            self.add_log_events(recent_events)

        self.add_page_break()

        # Threshold Violations
        self.add_section("6. Threshold Violations")
        if 'violations_table' in tables:
            self.add_table(tables['violations_table'])
        self.add_spacer()

        # Recommendations
        self.add_section("7. Recommendations")
        if recommendations:
            self.add_recommendations(recommendations)
        else:
            self.add_paragraph("No recommendations at this time. System is operating within normal parameters.")

        # Generate PDF
        self.generate()
