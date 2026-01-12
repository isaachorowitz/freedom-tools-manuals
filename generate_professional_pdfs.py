#!/usr/bin/env python3
"""
Freedom Tools Professional Manual PDF Generator
Creates beautifully formatted, consistent PDF manuals with headers, footers, and page numbers.
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY, TA_RIGHT
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, 
    Table, TableStyle, KeepTogether, Frame, PageTemplate
)
from reportlab.pdfgen import canvas
import re
from datetime import datetime


class NumberedCanvas(canvas.Canvas):
    """Custom canvas that adds page numbers and headers/footers."""
    
    def __init__(self, *args, **kwargs):
        canvas.Canvas.__init__(self, *args, **kwargs)
        self._saved_page_states = []
        self.model_number = kwargs.get('model_number', '')
        self.tool_name = kwargs.get('tool_name', '')
        
    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()
        
    def save(self):
        """Add page info to each page (page x of y)"""
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)
        
    def draw_page_decorations(self, page_count):
        """Draw headers, footers, and page numbers."""
        page_num = self._pageNumber
        
        # Skip decorations on cover page (page 1)
        if page_num == 1:
            return
            
        # Header
        self.saveState()
        self.setFont('Helvetica', 9)
        self.setFillColor(colors.HexColor('#666666'))
        
        # Left side - Brand and model
        self.drawString(0.75*inch, letter[1] - 0.5*inch, 
                       f"FREEDOM TOOLS  |  {self.model_number}")
        
        # Right side - Tool name
        text_width = self.stringWidth(self.tool_name, 'Helvetica', 9)
        self.drawString(letter[0] - 0.75*inch - text_width, 
                       letter[1] - 0.5*inch, 
                       self.tool_name)
        
        # Header line
        self.setStrokeColor(colors.HexColor('#0066cc'))
        self.setLineWidth(0.5)
        self.line(0.75*inch, letter[1] - 0.55*inch, 
                 letter[0] - 0.75*inch, letter[1] - 0.55*inch)
        
        # Footer line
        self.line(0.75*inch, 0.65*inch, 
                 letter[0] - 0.75*inch, 0.65*inch)
        
        # Page number - centered
        page_text = f"Page {page_num} of {page_count}"
        text_width = self.stringWidth(page_text, 'Helvetica', 9)
        self.drawString((letter[0] - text_width) / 2, 0.5*inch, page_text)
        
        # Copyright - left side
        self.setFont('Helvetica', 8)
        self.drawString(0.75*inch, 0.5*inch, 
                       f"© {datetime.now().year} Freedom Tools")
        
        # Empty space on right side (no contact info)
        
        self.restoreState()


class FreedomManualPDF:
    """Generate professional PDF manuals for Freedom Tools."""
    
    def __init__(self, output_filename, model_number, tool_name):
        self.output_filename = output_filename
        self.model_number = model_number
        self.tool_name = tool_name
        self.story = []
        self.styles = getSampleStyleSheet()
        # Layout mode: 'full' prioritizes whitespace and clarity; 'condensed' targets ~10 pages.
        self.layout_mode = 'condensed'
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Create custom paragraph styles for consistent formatting."""
        
        def add_style_if_not_exists(name, style):
            if name not in self.styles:
                self.styles.add(style)
        
        # Cover page styles
        add_style_if_not_exists('CoverBrand', ParagraphStyle(
            name='CoverBrand',
            parent=self.styles['Heading1'],
            fontSize=32,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold',
            letterSpacing=2
        ))
        
        add_style_if_not_exists('CoverTitle', ParagraphStyle(
            name='CoverTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=12,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        add_style_if_not_exists('ModelNumber', ParagraphStyle(
            name='ModelNumber',
            parent=self.styles['Normal'],
            fontSize=18,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=30,
            alignment=TA_CENTER,
            fontName='Helvetica-Bold'
        ))
        
        add_style_if_not_exists('CoverSubtitle', ParagraphStyle(
            name='CoverSubtitle',
            parent=self.styles['Normal'],
            fontSize=16,
            textColor=colors.HexColor('#666666'),
            spaceAfter=6,
            alignment=TA_CENTER,
            fontName='Helvetica'
        ))
        
        # Major section header style (top-level sections surrounded by ===== lines in source)
        add_style_if_not_exists('MajorSectionHeader', ParagraphStyle(
            name='MajorSectionHeader',
            parent=self.styles['Heading1'],
            fontSize=14,
            textColor=colors.HexColor('#ffffff'),
            spaceAfter=12,
            spaceBefore=14,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#004a99'),
            leftIndent=12,
            rightIndent=12,
            borderPadding=8,
            keepWithNext=1
        ))

        # Section header style
        add_style_if_not_exists('SectionHeader', ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading1'],
            fontSize=13,
            textColor=colors.HexColor('#ffffff'),
            spaceAfter=14,
            spaceBefore=24,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#0066cc'),
            leftIndent=12,
            rightIndent=12,
            borderPadding=8
        ))
        
        # Subsection header style
        add_style_if_not_exists('SubsectionHeader', ParagraphStyle(
            name='SubsectionHeader',
            parent=self.styles['Heading2'],
            fontSize=11,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=8,
            spaceBefore=14,
            fontName='Helvetica-Bold',
            borderWidth=0,
            borderPadding=0,
            leftIndent=0,
            keepWithNext=1
        ))
        
        # Problem header style for troubleshooting
        add_style_if_not_exists('ProblemHeader', ParagraphStyle(
            name='ProblemHeader',
            parent=self.styles['Normal'],
            fontSize=10,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=4,
            spaceBefore=12,
            fontName='Helvetica-Bold',
            leftIndent=0
        ))
        
        # Body text style
        add_style_if_not_exists('BodyText', ParagraphStyle(
            name='BodyText',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=6,
            alignment=TA_LEFT,
            fontName='Helvetica',
            leading=12
        ))
        
        # Bullet point style
        add_style_if_not_exists('BulletPoint', ParagraphStyle(
            name='BulletPoint',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#1a1a1a'),
            spaceAfter=4,
            leftIndent=24,
            bulletIndent=12,
            fontName='Helvetica',
            leading=12
        ))
        
        # Warning style
        add_style_if_not_exists('Warning', ParagraphStyle(
            name='Warning',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#cc0000'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#fff5f5'),
            borderWidth=2,
            borderColor=colors.HexColor('#cc0000'),
            borderPadding=10,
            leading=12,
            leftIndent=12,
            rightIndent=12
        ))
        
        # Note style
        add_style_if_not_exists('Note', ParagraphStyle(
            name='Note',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#0066cc'),
            spaceAfter=10,
            spaceBefore=10,
            fontName='Helvetica-Bold',
            backColor=colors.HexColor('#f0f8ff'),
            borderWidth=2,
            borderColor=colors.HexColor('#0066cc'),
            borderPadding=10,
            leading=12,
            leftIndent=12,
            rightIndent=12
        ))
        
        # Footer style
        add_style_if_not_exists('Footer', ParagraphStyle(
            name='Footer',
            parent=self.styles['Normal'],
            fontSize=9,
            textColor=colors.HexColor('#666666'),
            alignment=TA_CENTER,
            fontName='Helvetica',
            leading=14
        ))
    
    def add_cover_page(self, title, model, subtitle="INSTRUCTION MANUAL"):
        """Add a professional cover page."""
        # Add space from top
        self.story.append(Spacer(1, 1.8*inch))
        
        # Brand name
        brand = Paragraph("FREEDOM", self.styles['CoverBrand'])
        self.story.append(brand)
        self.story.append(Spacer(1, 0.1*inch))
        
        # Product title
        title_para = Paragraph(title, self.styles['CoverTitle'])
        self.story.append(title_para)
        self.story.append(Spacer(1, 0.3*inch))
        
        # Model number
        model_para = Paragraph(f"MODEL {model}", self.styles['ModelNumber'])
        self.story.append(model_para)
        self.story.append(Spacer(1, 0.6*inch))
        
        # Subtitle
        subtitle_para = Paragraph(subtitle, self.styles['CoverSubtitle'])
        self.story.append(subtitle_para)
        self.story.append(Spacer(1, 1.2*inch))
        
        # Important notice
        notice = Paragraph(
            "<b>⚠ IMPORTANT:</b> Please read this manual carefully before using your tool. "
            "Keep it in a safe place for future reference. Failure to follow instructions "
            "may result in serious injury.",
            self.styles['Warning']
        )
        self.story.append(notice)
        
        # Add page break
        self.story.append(PageBreak())
    
    def parse_and_add_content(self, text_content):
        """Parse text file and add formatted content to PDF."""
        lines = text_content.split('\n')
        i = 0

        def is_separator(s: str) -> bool:
            s = s.strip()
            return len(s) >= 10 and set(s) == {'='}

        def is_dashes_only(s: str) -> bool:
            s = s.strip()
            return len(s) >= 5 and set(s) == {'-'}

        def should_skip_header_line(s: str) -> bool:
            # Skip the text-based cover header lines that appear in the source TXT
            if not s:
                return True
            if ('FREEDOM' in s and 'TOOLS' in s) or s.startswith('MODEL:') or s == 'INSTRUCTION MANUAL':
                return True
            return False

        def start_major_section():
            # We intentionally avoid forced page breaks here (page count explodes).
            # keepWithNext on the header style prevents orphaned headings at page bottom.
            return
        
        while i < len(lines):
            line = lines[i].strip()
            
            # Major section blocks in the source are formatted as:
            # ========\nSECTION TITLE\n========
            if is_separator(line):
                j = i + 1
                while j < len(lines) and not lines[j].strip():
                    j += 1
                if j >= len(lines):
                    break
                title = lines[j].strip()

                k = j + 1
                while k < len(lines) and not lines[k].strip():
                    k += 1

                if k < len(lines) and is_separator(lines[k].strip()):
                    # It's a section block. Only treat it as a "major section" if it isn't part of
                    # the decorative header at the top of the TXT.
                    if not should_skip_header_line(title) and not title.startswith('FREEDOM '):
                        start_major_section()
                        self.story.append(Paragraph(title, self.styles['MajorSectionHeader']))
                    i = k + 1
                    continue

                # Separator line not followed by a proper section block; skip it.
                i += 1
                continue

            # Skip the text-based header lines (non-section content at top / end)
            if should_skip_header_line(line):
                i += 1
                continue
            
            # Skip empty lines
            if not line:
                i += 1
                continue

            # Skip underline lines made of dashes (titles above them are handled via lookahead)
            if is_dashes_only(line):
                i += 1
                continue

            # Title lines followed by dashed underlines are subsection headers
            if (i + 1) < len(lines) and is_dashes_only(lines[i + 1].strip()):
                # Prevent warnings/notes/problems from being styled as headings
                if (not line.startswith('⚠') and not line.startswith('WARNING') and
                    not line.startswith('NOTE:') and not line.startswith('IMPORTANT:') and
                    not line.startswith('CAUTION:') and not line.startswith('PROBLEM:')):
                    self.story.append(Paragraph(line, self.styles['SubsectionHeader']))
                    i += 2
                    continue
            
            # Uppercase headings in-body are treated as subsection headers (not major section bars)
            if (line.isupper() and len(line) > 3 and
                not line.startswith('⚠') and not line.startswith('WARNING') and
                not line.startswith('NOTE:') and not line.startswith('IMPORTANT:') and
                not line.startswith('CAUTION:') and not line.startswith('PROBLEM:')):
                self.story.append(Paragraph(line, self.styles['SubsectionHeader']))
                i += 1
                continue
            
            # Problem headers in troubleshooting section
            if line.startswith('PROBLEM:'):
                problem = Paragraph(line, self.styles['ProblemHeader'])
                self.story.append(problem)
                i += 1
                continue
            
            # Subsection headers (lines ending with colon)
            if (line.endswith(':') and len(line) < 80 and 
                not line.startswith('⚠') and not line.startswith('WARNING') and
                not line.startswith('NOTE:') and not line.startswith('IMPORTANT:') and
                not line.startswith('CAUTION:') and not line.startswith('•') and
                not line.startswith('□') and not line.startswith('PROBLEM:')):
                subsection = Paragraph(line.rstrip(':').rstrip('-').strip(), 
                                     self.styles['SubsectionHeader'])
                self.story.append(subsection)
                i += 1
                continue
            
            # Warning lines - collect multi-line warnings
            if line.startswith('⚠') or line.startswith('WARNING'):
                warning_lines = [line]
                i += 1
                
                # Collect continuation lines
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (not next_line or next_line.startswith('⚠') or 
                        next_line.startswith('WARNING') or next_line.isupper() or 
                        next_line.startswith('□') or next_line.startswith('•') or 
                        next_line.startswith('-') or re.match(r'^\d+\.', next_line) or
                        next_line.startswith('PROBLEM:') or
                        (next_line.endswith(':') and len(next_line) < 80)):
                        break
                    warning_lines.append(next_line)
                    i += 1
                
                warning_text = ' '.join(warning_lines)
                warning_text = warning_text.replace('⚠', '⚠ ')
                warning = Paragraph(warning_text, self.styles['Warning'])
                self.story.append(KeepTogether(warning))
                continue
            
            # Note lines - collect multi-line notes
            if line.startswith('NOTE:') or line.startswith('IMPORTANT:') or line.startswith('CAUTION:'):
                note_lines = [line]
                i += 1
                
                # Collect continuation lines
                while i < len(lines):
                    next_line = lines[i].strip()
                    if (not next_line or next_line.startswith('NOTE:') or 
                        next_line.startswith('IMPORTANT:') or next_line.startswith('CAUTION:') or 
                        next_line.startswith('⚠') or next_line.startswith('WARNING') or 
                        next_line.isupper() or next_line.startswith('□') or 
                        next_line.startswith('•') or next_line.startswith('-') or 
                        re.match(r'^\d+\.', next_line) or next_line.startswith('PROBLEM:') or
                        (next_line.endswith(':') and len(next_line) < 80)):
                        break
                    note_lines.append(next_line)
                    i += 1
                
                note_text = ' '.join(note_lines)
                note = Paragraph(note_text, self.styles['Note'])
                self.story.append(KeepTogether(note))
                continue
            
            # Checkbox items
            if line.startswith('□'):
                bullet = Paragraph(f"• {line[1:].strip()}", self.styles['BulletPoint'])
                self.story.append(bullet)
                i += 1
                continue
            
            # Bullet points
            if line.startswith('•') or (line.startswith('-') and len(line) > 2 and line[1] == ' '):
                bullet = Paragraph(line, self.styles['BulletPoint'])
                self.story.append(bullet)
                i += 1
                continue
            
            # Numbered items
            if re.match(r'^\d+\.', line):
                bullet = Paragraph(line, self.styles['BulletPoint'])
                self.story.append(bullet)
                i += 1
                continue
            
            # Regular paragraph
            if len(line) > 0:
                para = Paragraph(line, self.styles['BodyText'])
                self.story.append(para)
                i += 1
                continue
            
            i += 1
    
    def add_footer_page(self):
        """Add a final footer page with company information."""
        self.story.append(PageBreak())
        self.story.append(Spacer(1, 3*inch))
        
        footer_text = f"""
        <para align=center>
        <b><font size=16 color="#0066cc">FREEDOM TOOLS</font></b><br/>
        <font size=12>Built for Performance, Designed for You</font><br/>
        <br/>
        <br/>
        <br/>
        <font size=9 color="#666666">© {datetime.now().year} Freedom Tools. All rights reserved.<br/>
        Specifications subject to change without notice.</font>
        </para>
        """
        
        footer = Paragraph(footer_text, self.styles['Footer'])
        self.story.append(footer)
    
    def build(self):
        """Build the PDF document with custom canvas."""
        doc = SimpleDocTemplate(
            self.output_filename,
            pagesize=letter,
            rightMargin=0.6*inch,
            leftMargin=0.6*inch,
            topMargin=0.6*inch,
            bottomMargin=0.6*inch
        )
        
        # Build with custom canvas that adds page numbers
        doc.build(
            self.story,
            canvasmaker=lambda *args, **kwargs: NumberedCanvas(
                *args, 
                model_number=self.model_number,
                tool_name=self.tool_name,
                **kwargs
            )
        )
        print(f"✓ PDF created successfully: {self.output_filename}")


def generate_manual_pdf(text_file, output_pdf, title, model):
    """Generate a PDF manual from a text file."""
    print(f"\nGenerating PDF: {output_pdf}")
    print(f"  Title: {title}")
    print(f"  Model: {model}")
    
    # Read the text file
    with open(text_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Create PDF
    pdf = FreedomManualPDF(output_pdf, model, title)
    pdf.add_cover_page(title, model)
    pdf.parse_and_add_content(content)
    # Avoid adding a whole extra page at the end; it hurts the 10-page goal.
    pdf.build()


def main():
    """Generate all three Freedom Tools manuals."""
    print("=" * 70)
    print("Freedom Tools Professional Manual PDF Generator")
    print("=" * 70)
    
    manuals = [
        {
            'text_file': 'FT1001_Drill_Manual_CONDENSED.txt',
            'output_pdf': 'Freedom_FT1001_Drill_Manual_Condensed.pdf',
            'title': '18V Cordless Drill',
            'model': 'FT1001'
        },
        {
            'text_file': 'FT1003_MiniSaw_Manual_CONDENSED.txt',
            'output_pdf': 'Freedom_FT1003_MiniSaw_Manual_Condensed.pdf',
            'title': '18V Cordless Mini Saw',
            'model': 'FT1003'
        },
        {
            'text_file': 'FT1002_OscillatingTool_Manual_CONDENSED.txt',
            'output_pdf': 'Freedom_FT1002_OscillatingTool_Manual_Condensed.pdf',
            'title': '18V Cordless Oscillating Multi-Tool',
            'model': 'FT1002'
        },
        {
            'text_file': 'FT1004_RotaryTool_Manual_CONDENSED.txt',
            'output_pdf': 'Freedom_FT1004_RotaryTool_Manual_Condensed.pdf',
            'title': '18V Cordless Rotary Tool',
            'model': 'FT1004'
        }
    ]
    
    for manual in manuals:
        try:
            generate_manual_pdf(
                manual['text_file'],
                manual['output_pdf'],
                manual['title'],
                manual['model']
            )
        except Exception as e:
            print(f"✗ Error generating {manual['output_pdf']}: {str(e)}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 70)
    print("PDF Generation Complete!")
    print("=" * 70)


if __name__ == "__main__":
    main()
