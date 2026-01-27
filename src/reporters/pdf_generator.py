"""
PDF report generator module using ReportLab.
대시보드 스타일의 현대적인 PDF 보고서 생성
"""
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm, cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Image, KeepTogether, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.graphics.shapes import Drawing, Rect, String, Line
from reportlab.graphics.charts.piecharts import Pie
from datetime import datetime
from typing import Dict, List, Any
import logging
import os
import io
import platform


class PDFGenerator:
    """Generate modern dashboard-style PDF reports."""

    # 컬러 팔레트
    COLORS = {
        'primary': colors.HexColor('#0066CC'),
        'primary_light': colors.HexColor('#E3F2FD'),
        'success': colors.HexColor('#00A86B'),
        'success_light': colors.HexColor('#E8F5E9'),
        'warning': colors.HexColor('#FFB020'),
        'warning_light': colors.HexColor('#FFF8E1'),
        'danger': colors.HexColor('#E53935'),
        'danger_light': colors.HexColor('#FFEBEE'),
        'background': colors.HexColor('#F5F7FA'),
        'card': colors.HexColor('#FFFFFF'),
        'text': colors.HexColor('#1A1A2E'),
        'text_secondary': colors.HexColor('#4A5568'),
        'muted': colors.HexColor('#6B7280'),
        'border': colors.HexColor('#E5E7EB'),
        'light': colors.HexColor('#F3F4F6'),
    }

    def __init__(self, output_path: str):
        """Initialize PDF generator."""
        self.output_path = output_path
        self.logger = logging.getLogger('monitoring_system')

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        self._register_korean_font()

        self.doc = SimpleDocTemplate(
            output_path,
            pagesize=A4,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )

        self.page_width = A4[0] - 80
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        self.story = []

    def _register_korean_font(self):
        """Register Korean font for PDF rendering."""
        font_configs = []

        if platform.system() == 'Darwin':
            font_configs = [
                {
                    'regular': '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
                    'bold': '/System/Library/Fonts/Supplemental/AppleGothic.ttf',
                },
                {
                    'regular': '/Library/Fonts/AppleGothic.ttf',
                    'bold': '/Library/Fonts/AppleGothic.ttf',
                },
            ]
        elif platform.system() == 'Linux':
            font_configs = [
                {
                    'regular': '/usr/share/fonts/truetype/nanum/NanumGothic.ttf',
                    'bold': '/usr/share/fonts/truetype/nanum/NanumGothicBold.ttf',
                },
            ]
        else:
            font_configs = [
                {
                    'regular': 'C:/Windows/Fonts/malgun.ttf',
                    'bold': 'C:/Windows/Fonts/malgunbd.ttf',
                },
            ]

        font_registered = False
        for config in font_configs:
            regular_path = config['regular']
            bold_path = config['bold']

            if os.path.exists(regular_path):
                try:
                    pdfmetrics.registerFont(TTFont('Korean', regular_path))
                    font_registered = True
                    self.korean_font = 'Korean'
                    self.logger.info(f"Korean font registered: {regular_path}")

                    # Register bold font if available
                    if os.path.exists(bold_path):
                        pdfmetrics.registerFont(TTFont('KoreanBold', bold_path))
                        self.korean_font_bold = 'KoreanBold'
                        self.logger.info(f"Korean bold font registered: {bold_path}")
                    else:
                        self.korean_font_bold = 'Korean'
                        self.logger.warning(f"Bold font not found, using regular: {bold_path}")

                    # Register font family for automatic bold/italic substitution
                    pdfmetrics.registerFontFamily(
                        'Korean',
                        normal='Korean',
                        bold=self.korean_font_bold,
                        italic='Korean',
                        boldItalic=self.korean_font_bold
                    )
                    self.logger.info("Korean font family registered for <b> tag support")

                    break
                except Exception as e:
                    self.logger.warning(f"Failed to register font: {e}")

        if not font_registered:
            self.korean_font = 'Helvetica'
            self.korean_font_bold = 'Helvetica-Bold'

    def _setup_custom_styles(self):
        """Set up custom paragraph styles."""
        # 메인 타이틀
        self.styles.add(ParagraphStyle(
            name='MainTitle',
            fontName=self.korean_font,
            fontSize=32,
            textColor=self.COLORS['text'],
            alignment=TA_CENTER,
            spaceAfter=10,
            leading=40
        ))

        # 서브타이틀
        self.styles.add(ParagraphStyle(
            name='Subtitle',
            fontName=self.korean_font,
            fontSize=14,
            textColor=self.COLORS['muted'],
            alignment=TA_CENTER,
            spaceAfter=30
        ))

        # 섹션 헤더
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            fontName=self.korean_font,
            fontSize=16,
            textColor=self.COLORS['text'],
            spaceBefore=20,
            spaceAfter=15,
            leading=22
        ))

        # 서브섹션 헤더
        self.styles.add(ParagraphStyle(
            name='SubsectionHeader',
            fontName=self.korean_font,
            fontSize=12,
            textColor=self.COLORS['text_secondary'],
            spaceBefore=12,
            spaceAfter=8
        ))

        # 본문
        self.styles.add(ParagraphStyle(
            name='Body',
            fontName=self.korean_font,
            fontSize=10,
            textColor=self.COLORS['text'],
            spaceAfter=8,
            leading=16
        ))

        # 카드 제목
        self.styles.add(ParagraphStyle(
            name='CardTitle',
            fontName=self.korean_font,
            fontSize=11,
            textColor=self.COLORS['muted'],
            alignment=TA_CENTER
        ))

        # 카드 값
        self.styles.add(ParagraphStyle(
            name='CardValue',
            fontName=self.korean_font,
            fontSize=24,
            textColor=self.COLORS['primary'],
            alignment=TA_CENTER,
            leading=30
        ))

        # 목차 항목
        self.styles.add(ParagraphStyle(
            name='TOCItem',
            fontName=self.korean_font,
            fontSize=12,
            textColor=self.COLORS['text'],
            spaceAfter=12,
            leftIndent=20
        ))

    def add_cover_page(self, hostname: str, year: int, month: int):
        """Add modern cover page."""
        self.story.append(Spacer(1, 2*inch))

        # 메인 타이틀
        self.story.append(Paragraph(
            "서버 모니터링 보고서",
            self.styles['MainTitle']
        ))

        # 기간
        self.story.append(Paragraph(
            f"{year}년 {month}월",
            self.styles['Subtitle']
        ))

        self.story.append(Spacer(1, 0.5*inch))

        # 구분선
        line_data = [[''] * 1]
        line_table = Table(line_data, colWidths=[200])
        line_table.setStyle(TableStyle([
            ('LINEABOVE', (0, 0), (-1, 0), 3, self.COLORS['primary']),
        ]))
        self.story.append(line_table)

        self.story.append(Spacer(1, 0.8*inch))

        # 서버 정보 카드
        info_data = [
            ['서버 이름', hostname],
            ['보고 기간', f'{year}년 {month}월 1일 ~ {year}년 {month}월 말'],
            ['생성 일시', datetime.now().strftime('%Y년 %m월 %d일 %H:%M')],
        ]

        info_table = Table(info_data, colWidths=[100, 280])
        info_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('TEXTCOLOR', (0, 0), (0, -1), self.COLORS['muted']),
            ('TEXTCOLOR', (1, 0), (1, -1), self.COLORS['text']),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['light']),
            ('BOX', (0, 0), (-1, -1), 1, self.COLORS['border']),
        ]))
        self.story.append(info_table)

        self.story.append(PageBreak())

    def add_table_of_contents(self):
        """Add visually appealing table of contents page."""
        # 목차 제목
        self.story.append(Spacer(1, 0.3*inch))

        toc_title = Paragraph(
            "<font size='20'>📑 목차</font>",
            ParagraphStyle('TOCTitle', fontName=self.korean_font, 
                          alignment=TA_CENTER, spaceAfter=8)
        )
        self.story.append(toc_title)
        
        toc_subtitle = Paragraph(
            "<font size='10' color='#6B7280'>보고서에 포함된 내용을 확인하세요</font>",
            ParagraphStyle('TOCSubtitle', fontName=self.korean_font,
                          alignment=TA_CENTER, spaceAfter=25)
        )
        self.story.append(toc_subtitle)

        # 목차 항목 정의 (아이콘, 번호, 제목, 설명, 컬러)
        toc_items = [
            ('📊', '1', '요약 대시보드', '핵심 지표 및 시스템 상태 한눈에 보기', self.COLORS['primary']),
            ('🖥️', '2', 'CPU 분석', 'CPU 사용률 추이 및 상세 통계', colors.HexColor('#0891B2')),
            ('💾', '3', '메모리 분석', 'RAM 및 SWAP 메모리 사용 현황', colors.HexColor('#7C3AED')),
            ('💿', '4', '디스크 분석', '파티션별 디스크 사용량 모니터링', colors.HexColor('#059669')),
            ('📝', '5', '로그 분석', '시스템 로그 및 보안 이벤트 요약', colors.HexColor('#D97706')),
            ('⚡', '6', '이슈 및 권장사항', '임계값 위반 항목 및 개선 권고', self.COLORS['danger']),
        ]

        # 2열 레이아웃으로 목차 카드 배치
        card_width = (self.page_width - 15) / 2
        
        for i in range(0, len(toc_items), 2):
            row_cards = []
            
            for j in range(2):
                if i + j < len(toc_items):
                    item = toc_items[i + j]
                    card = self._create_toc_card(
                        item[0], item[1], item[2], item[3], item[4], card_width
                    )
                    row_cards.append(card)
                else:
                    row_cards.append('')  # 빈 셀

            row_table = Table([row_cards], colWidths=[card_width, card_width])
            row_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                ('LEFTPADDING', (0, 0), (-1, -1), 4),
                ('RIGHTPADDING', (0, 0), (-1, -1), 4),
            ]))
            self.story.append(row_table)
            self.story.append(Spacer(1, 0.12*inch))

        self.story.append(PageBreak())

    def _create_toc_card(self, icon: str, number: str, title: str, 
                         desc: str, color: colors.Color, width: float) -> Table:
        """Create a styled TOC card."""
        inner_width = width - 24

        # 아이콘 + 번호
        header_para = Paragraph(
            f"<font size='16'>{icon}</font>  "
            f"<font size='11' color='#{color.hexval()[2:]}'><b>{number}</b></font>",
            ParagraphStyle('TOCCardHeader', fontName=self.korean_font, leading=20)
        )

        # 제목
        title_para = Paragraph(
            f"<font size='12' color='#1A1A2E'><b>{title}</b></font>",
            ParagraphStyle('TOCCardTitle', fontName=self.korean_font, 
                          spaceBefore=4, spaceAfter=4)
        )

        # 설명
        desc_para = Paragraph(
            f"<font size='9' color='#6B7280'>{desc}</font>",
            ParagraphStyle('TOCCardDesc', fontName=self.korean_font, leading=13)
        )

        # 내부 테이블
        inner_data = [
            [header_para],
            [title_para],
            [desc_para],
        ]
        
        inner_table = Table(inner_data, colWidths=[inner_width])
        inner_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ]))

        # 외부 카드
        card_data = [[inner_table]]
        card_table = Table(card_data, colWidths=[width - 8])
        card_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), self.COLORS['light']),
            ('BOX', (0, 0), (-1, -1), 0, self.COLORS['border']),
            ('LINEABOVE', (0, 0), (-1, 0), 3, color),  # 상단 컬러 바
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 12),
            ('RIGHTPADDING', (0, 0), (-1, -1), 12),
        ]))

        return card_table

    def add_section_header(self, number: str, title: str, icon: str = ""):
        """Add styled section header."""
        header_text = f"{icon} {number}. {title}" if icon else f"{number}. {title}"
        
        # 헤더 배경
        header_data = [[header_text]]
        header_table = Table(header_data, colWidths=[self.page_width])
        header_table.setStyle(TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, -1), 16),
            ('TEXTCOLOR', (0, 0), (-1, -1), self.COLORS['primary']),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('LINEBELOW', (0, 0), (-1, -1), 2, self.COLORS['primary']),
        ]))
        self.story.append(header_table)
        self.story.append(Spacer(1, 0.2*inch))

    def add_kpi_cards(self, metrics: Dict[str, Any], analysis: Dict[str, Any],
                      violations: List[Dict[str, Any]]):
        """Add KPI summary cards with uniform layout."""
        # 데이터 준비
        cpu_usage = 0
        mem_usage = 0
        disk_usage = 0
        
        if metrics:
            cpu_usage = metrics.get('cpu', {}).get('usage_percent', 0)
            mem_usage = metrics.get('memory', {}).get('ram', {}).get('percent', 0)
            
            disk_data = analysis.get('disk', {})
            if disk_data:
                first_disk = list(disk_data.values())[0] if disk_data else {}
                disk_usage = first_disk.get('usage_percent', {}).get('mean', 0)

        # 상태 결정
        critical_count = sum(1 for v in violations if v.get('severity') == 'critical')
        warning_count = sum(1 for v in violations if v.get('severity') == 'warning')
        
        if critical_count > 0:
            status = '주의'
            status_color = self.COLORS['danger']
            status_bg = self.COLORS['danger_light']
        elif warning_count > 0:
            status = '경고'
            status_color = self.COLORS['warning']
            status_bg = self.COLORS['warning_light']
        else:
            status = '정상'
            status_color = self.COLORS['success']
            status_bg = self.COLORS['success_light']

        # 추세 데이터
        cpu_trend = analysis.get('cpu', {}).get('trend', 'stable')
        mem_trend = analysis.get('memory', {}).get('ram', {}).get('trend', 'stable')

        # 고정 카드 너비
        card_width = (self.page_width - 24) / 4  # 24 = 간격

        # KPI 데이터 정의
        kpi_items = [
            {
                'title': 'CPU',
                'value': f'{cpu_usage:.1f}%',
                'trend': cpu_trend,
                'color': self.COLORS['primary'],
                'bg': self.COLORS['primary_light'],
            },
            {
                'title': '메모리',
                'value': f'{mem_usage:.1f}%',
                'trend': mem_trend,
                'color': colors.HexColor('#0891B2'),
                'bg': colors.HexColor('#E0F7FA'),
            },
            {
                'title': '디스크',
                'value': f'{disk_usage:.1f}%',
                'trend': 'stable',
                'color': colors.HexColor('#7C3AED'),
                'bg': colors.HexColor('#EDE9FE'),
            },
            {
                'title': '상태',
                'value': status,
                'trend': None,
                'color': status_color,
                'bg': status_bg,
            },
        ]

        # 카드 테이블 생성
        card_cells = []
        for item in kpi_items:
            card_cells.append(self._create_uniform_kpi_card(
                item['title'], item['value'], item['trend'],
                item['color'], item['bg'], card_width
            ))

        kpi_table = Table([card_cells], colWidths=[card_width] * 4)
        kpi_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        self.story.append(kpi_table)
        self.story.append(Spacer(1, 0.25*inch))

    def _create_uniform_kpi_card(self, title: str, value: str, trend: str,
                                  color: colors.Color, bg_color: colors.Color,
                                  width: float) -> Table:
        """Create a uniformly styled KPI card."""
        trend_symbols = {'increasing': '▲ 증가', 'decreasing': '▼ 감소', 'stable': '─ 안정'}
        trend_colors = {
            'increasing': self.COLORS['danger'],
            'decreasing': self.COLORS['success'],
            'stable': self.COLORS['muted']
        }

        # 카드 내용 구성
        inner_width = width - 16  # 패딩 제외

        # 제목 행
        title_para = Paragraph(
            f"<font size='10' color='#{self.COLORS['muted'].hexval()[2:]}'>{title}</font>",
            ParagraphStyle('CardTitleStyle', alignment=TA_CENTER, fontName=self.korean_font)
        )

        # 값 행
        value_para = Paragraph(
            f"<font size='22' color='#{color.hexval()[2:]}'><b>{value}</b></font>",
            ParagraphStyle('CardValueStyle', alignment=TA_CENTER, fontName=self.korean_font,
                          leading=28)
        )

        # 추세 행
        if trend:
            t_text = trend_symbols.get(trend, '─ 안정')
            t_color = trend_colors.get(trend, self.COLORS['muted'])
            trend_para = Paragraph(
                f"<font size='9' color='#{t_color.hexval()[2:]}'>{t_text}</font>",
                ParagraphStyle('CardTrendStyle', alignment=TA_CENTER, fontName=self.korean_font)
            )
        else:
            trend_para = Paragraph("", ParagraphStyle('Empty', fontSize=9))

        # 내부 테이블
        inner_data = [
            [title_para],
            [Spacer(1, 5)],
            [value_para],
            [Spacer(1, 5)],
            [trend_para],
        ]

        inner_table = Table(inner_data, colWidths=[inner_width], 
                           rowHeights=[18, 5, 35, 5, 16])
        inner_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))

        # 외부 카드 테이블 (배경, 테두리)
        card_data = [[inner_table]]
        card_table = Table(card_data, colWidths=[width - 6])
        card_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('BACKGROUND', (0, 0), (-1, -1), bg_color),
            ('BOX', (0, 0), (-1, -1), 1.5, color),
            ('TOPPADDING', (0, 0), (-1, -1), 12),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))

        return card_table

    def add_chart(self, chart_bytes: bytes, width: float = None, height: float = None):
        """Add chart image."""
        if width is None:
            width = self.page_width
        if height is None:
            height = 2.8*inch
            
        try:
            img = Image(io.BytesIO(chart_bytes), width=width, height=height)
            self.story.append(img)
            self.story.append(Spacer(1, 0.15*inch))
        except Exception as e:
            self.logger.error(f"Error adding chart: {e}")

    def add_table(self, table_data: List[List[str]], col_widths: List[float] = None):
        """Add modern styled table."""
        if not table_data:
            return

        table = Table(table_data, colWidths=col_widths)

        style_commands = [
            # 헤더
            ('FONTNAME', (0, 0), (-1, 0), self.korean_font),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('TEXTCOLOR', (0, 0), (-1, 0), self.COLORS['card']),
            ('BACKGROUND', (0, 0), (-1, 0), self.COLORS['primary']),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('TOPPADDING', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),

            # 데이터
            ('FONTNAME', (0, 1), (-1, -1), self.korean_font),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('TEXTCOLOR', (0, 1), (-1, -1), self.COLORS['text']),
            ('ALIGN', (0, 1), (-1, -1), 'LEFT'),
            ('TOPPADDING', (0, 1), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 1), (-1, -1), 10),
            ('LEFTPADDING', (0, 0), (-1, -1), 10),
            ('RIGHTPADDING', (0, 0), (-1, -1), 10),

            # 테두리
            ('LINEBELOW', (0, 0), (-1, -2), 0.5, self.COLORS['border']),
            ('LINEBELOW', (0, -1), (-1, -1), 1, self.COLORS['border']),
        ]

        # 행 배경색 교차
        for i in range(1, len(table_data)):
            bg = self.COLORS['card'] if i % 2 == 1 else self.COLORS['light']
            style_commands.append(('BACKGROUND', (0, i), (-1, i), bg))

        table.setStyle(TableStyle(style_commands))
        self.story.append(table)
        self.story.append(Spacer(1, 0.2*inch))

    def add_issue_card(self, title: str, items: List[Dict[str, Any]], 
                       card_type: str = 'warning'):
        """Add issue/recommendation card."""
        if not items:
            self.story.append(Paragraph(
                f"<font color='#{self.COLORS['success'].hexval()[2:]}'>✓ 특별한 이슈가 없습니다.</font>",
                self.styles['Body']
            ))
            return

        bg_colors = {
            'danger': self.COLORS['danger_light'],
            'warning': self.COLORS['warning_light'],
            'success': self.COLORS['success_light'],
            'info': self.COLORS['primary_light'],
        }
        
        text_colors = {
            'danger': self.COLORS['danger'],
            'warning': self.COLORS['warning'],
            'success': self.COLORS['success'],
            'info': self.COLORS['primary'],
        }

        bg_color = bg_colors.get(card_type, self.COLORS['light'])
        text_color = text_colors.get(card_type, self.COLORS['text'])

        for item in items:
            priority = item.get('priority', 'medium').upper()
            item_title = item.get('title', '')
            description = item.get('description', '')
            actions = item.get('actions', [])

            # 우선순위 아이콘
            priority_icons = {
                'CRITICAL': '🔴',
                'HIGH': '🟠',
                'MEDIUM': '🟡',
                'LOW': '🟢',
            }
            icon = priority_icons.get(priority, '⚪')

            # 카드 데이터
            card_content = f"<b>{icon} {item_title}</b>"
            if description:
                card_content += f"<br/><font size='9' color='#{self.COLORS['text_secondary'].hexval()[2:]}'>{description}</font>"

            card_data = [[Paragraph(card_content, self.styles['Body'])]]

            if actions:
                actions_text = "<br/>".join([f"• {a}" for a in actions[:3]])
                card_data.append([Paragraph(
                    f"<font size='9' color='#{self.COLORS['muted'].hexval()[2:]}'><b>권장 조치:</b><br/>{actions_text}</font>",
                    self.styles['Body']
                )])

            card_table = Table(card_data, colWidths=[self.page_width - 20])
            card_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, -1), bg_color),
                ('BOX', (0, 0), (-1, -1), 1, text_color),
                ('LEFTPADDING', (0, 0), (-1, -1), 15),
                ('RIGHTPADDING', (0, 0), (-1, -1), 15),
                ('TOPPADDING', (0, 0), (-1, -1), 12),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
            ]))
            
            self.story.append(card_table)
            self.story.append(Spacer(1, 0.1*inch))

    def add_spacer(self, height: float = 0.2):
        """Add vertical spacer."""
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
        """Create complete dashboard-style PDF report."""
        
        # 최신 메트릭
        latest_metrics = metrics_list[-1] if metrics_list else {}

        # 1. 표지
        self.add_cover_page(hostname, year, month)

        # 2. 목차
        self.add_table_of_contents()

        # 3. 요약 대시보드
        self.add_section_header('1', '요약 대시보드', '📊')
        self.add_kpi_cards(latest_metrics, analysis, violations)

        # 요약 통계 테이블
        if 'summary_table' in tables:
            self.story.append(Paragraph(
                "<b>월간 통계 요약</b>",
                self.styles['SubsectionHeader']
            ))
            self.add_table(tables['summary_table'])

        # 일자별 월간 사용률 테이블
        if 'daily_usage_table' in tables:
            self.add_spacer(0.2)
            self.story.append(Paragraph(
                "<b>월간 사용률 (일자별)</b>",
                self.styles['SubsectionHeader']
            ))
            self.add_table(tables['daily_usage_table'])

        self.add_page_break()

        # 4. CPU 분석
        self.add_section_header('2', 'CPU 분석', '🖥️')
        
        # CPU 게이지 차트
        if latest_metrics.get('cpu'):
            cpu_usage = latest_metrics['cpu'].get('usage_percent', 0)
            from src.reporters.chart_builder import ChartBuilder
            chart_builder = ChartBuilder()
            gauge_chart = chart_builder.create_gauge_chart(
                cpu_usage, 'CPU 사용률',
                {'warning': 70, 'critical': 85}
            )
            self.add_chart(gauge_chart, width=2.5*inch, height=2*inch)

        # CPU 트렌드 차트
        if 'cpu_chart' in charts:
            self.add_chart(charts['cpu_chart'])
        
        if 'cpu_stats_table' in tables:
            self.add_table(tables['cpu_stats_table'])

        self.add_page_break()

        # 5. 메모리 분석
        self.add_section_header('3', '메모리 분석', '💾')
        
        if 'memory_chart' in charts:
            self.add_chart(charts['memory_chart'])
        
        if 'memory_stats_table' in tables:
            self.add_table(tables['memory_stats_table'])

        self.add_page_break()

        # 6. 디스크 분석
        self.add_section_header('4', '디스크 분석', '💿')
        
        if 'disk_chart' in charts:
            self.add_chart(charts['disk_chart'])
        
        if 'disk_stats_table' in tables:
            self.add_table(tables['disk_stats_table'])

        self.add_page_break()

        # 7. 로그 분석
        self.add_section_header('5', '로그 분석', '📝')
        
        if 'log_summary_table' in tables:
            self.add_table(tables['log_summary_table'])

        # 보안 이벤트
        auth_log = log_analysis.get('auth_log', {})
        security_events = auth_log.get('security_events', 0)
        
        if security_events > 0:
            self.story.append(Paragraph(
                f"<b>🔒 보안 이벤트: {security_events}건 감지</b>",
                self.styles['SubsectionHeader']
            ))
            
            recent_events = auth_log.get('recent_events', [])[:5]
            if recent_events:
                for event in recent_events:
                    msg = event.get('message', '')[:100]
                    ts = event.get('timestamp', '')
                    self.story.append(Paragraph(
                        f"<font color='#{self.COLORS['muted'].hexval()[2:]}'>[{ts}]</font> {msg}",
                        self.styles['Body']
                    ))

        self.add_page_break()

        # 8. 이슈 및 권장사항
        self.add_section_header('6', '이슈 및 권장사항', '⚡')
        
        # 임계값 위반
        self.story.append(Paragraph(
            "<b>임계값 위반 항목</b>",
            self.styles['SubsectionHeader']
        ))
        
        if violations and 'violations_table' in tables:
            self.add_table(tables['violations_table'])
        else:
            self.story.append(Paragraph(
                "<font color='#00A86B'>✓ 모든 지표가 정상 범위 내에 있습니다.</font>",
                self.styles['Body']
            ))

        self.add_spacer(0.2)

        # 권장사항
        self.story.append(Paragraph(
            "<b>권장 조치 사항</b>",
            self.styles['SubsectionHeader']
        ))
        
        if recommendations:
            self.add_issue_card('권장사항', recommendations, 'info')
        else:
            self.story.append(Paragraph(
                "<font color='#00A86B'>✓ 현재 특별한 권장 사항이 없습니다. 시스템이 안정적으로 운영되고 있습니다.</font>",
                self.styles['Body']
            ))

        # 푸터 정보
        self.add_spacer(0.5)
        self.story.append(Paragraph(
            f"<font color='#{self.COLORS['muted'].hexval()[2:]}' size='8'>본 보고서는 {datetime.now().strftime('%Y년 %m월 %d일 %H:%M')}에 자동 생성되었습니다.</font>",
            self.styles['Body']
        ))

        # PDF 생성
        self.generate()
