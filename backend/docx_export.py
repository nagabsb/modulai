"""
Export HTML content to proper DOCX with native Word math equations (OMML).
Uses python-docx + latex2mathml + lxml XSLT for LaTeX → MathML → OMML pipeline.
"""
import re
import io
from html.parser import HTMLParser
from docx import Document
from docx.shared import Pt, Inches, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from lxml import etree
import latex2mathml.converter

# Load XSLT once at module level
_xslt = etree.parse("/app/backend/MML2OMML.XSL")
_transform = etree.XSLT(_xslt)


def latex_to_omml(latex_str):
    """Convert LaTeX string to OMML etree element"""
    try:
        mathml = latex2mathml.converter.convert(latex_str)
        mathml_tree = etree.fromstring(mathml.encode('utf-8'))
        omml_tree = _transform(mathml_tree)
        return omml_tree.getroot()
    except Exception:
        return None


class HTMLToDocxParser(HTMLParser):
    """Parse HTML and build a python-docx Document with proper math rendering"""

    def __init__(self, doc):
        super().__init__()
        self.doc = doc
        self.current_paragraph = None
        self.current_run_props = {}  # bold, italic
        self.in_table = False
        self.table_data = []
        self.current_row = []
        self.current_cell_text = ""
        self.in_th = False
        self.in_td = False
        self.tag_stack = []
        self.skip_content = False
        self.pending_text = ""
        self.in_strong = False
        self.in_em = False
        self.list_counter = 0

    def _flush_text(self):
        """Flush pending text to current paragraph, handling LaTeX math"""
        if not self.pending_text or not self.current_paragraph:
            return

        text = self.pending_text
        self.pending_text = ""

        # Split text by $...$ LaTeX patterns
        parts = re.split(r'(\$\$[\s\S]+?\$\$|\$[^\$\n]+?\$)', text)
        for part in parts:
            if not part:
                continue

            # Display math $$...$$
            if part.startswith('$$') and part.endswith('$$'):
                latex = part[2:-2].strip()
                omml = latex_to_omml(latex)
                if omml is not None:
                    self.current_paragraph._element.append(omml)
                else:
                    run = self.current_paragraph.add_run(latex)
                    run.italic = True

            # Inline math $...$
            elif part.startswith('$') and part.endswith('$') and len(part) > 2:
                latex = part[1:-1].strip()
                omml = latex_to_omml(latex)
                if omml is not None:
                    self.current_paragraph._element.append(omml)
                else:
                    run = self.current_paragraph.add_run(latex)
                    run.italic = True

            # Regular text
            else:
                if part.strip():
                    run = self.current_paragraph.add_run(part)
                    run.bold = self.in_strong
                    run.italic = self.in_em
                    run.font.size = Pt(11)
                    run.font.name = 'Cambria'

    def _ensure_paragraph(self):
        if self.current_paragraph is None:
            self.current_paragraph = self.doc.add_paragraph()

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        self.tag_stack.append(tag)

        if tag == 'svg' or tag == 'script' or tag == 'style':
            self.skip_content = True
            return

        if self.in_table and tag in ('td', 'th'):
            self.in_th = tag == 'th'
            self.in_td = tag == 'td'
            self.current_cell_text = ""
            return

        if self.in_table and tag == 'tr':
            self.current_row = []
            return

        if tag == 'table':
            self._flush_text()
            self.in_table = True
            self.table_data = []
            return

        if self.in_table:
            return

        if tag == 'h1':
            self._flush_text()
            self.current_paragraph = self.doc.add_heading(level=1)

        elif tag == 'h2':
            self._flush_text()
            self.current_paragraph = self.doc.add_heading(level=2)

        elif tag == 'h3':
            self._flush_text()
            self.current_paragraph = self.doc.add_heading(level=3)

        elif tag == 'p':
            self._flush_text()
            self.current_paragraph = self.doc.add_paragraph()
            style = attrs_dict.get('style', '')
            if 'text-align:center' in style or 'text-align: center' in style:
                self.current_paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER

        elif tag == 'div':
            style = attrs_dict.get('style', '')
            if 'margin-left' in style:
                self._flush_text()
                self.current_paragraph = self.doc.add_paragraph()
                pf = self.current_paragraph.paragraph_format
                pf.left_indent = Cm(1.5)

        elif tag == 'br':
            if self.current_paragraph:
                self._flush_text()
                self.current_paragraph.add_run('\n')

        elif tag == 'hr':
            self._flush_text()
            p = self.doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            run = p.add_run('─' * 60)
            run.font.color.rgb = RGBColor(0x1E, 0x3A, 0x5F)

        elif tag == 'strong' or tag == 'b':
            self._flush_text()
            self.in_strong = True

        elif tag == 'em' or tag == 'i':
            self._flush_text()
            self.in_em = True

    def handle_endtag(self, tag):
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()

        if tag in ('svg', 'script', 'style'):
            self.skip_content = False
            return

        if tag in ('strong', 'b'):
            self._flush_text()
            self.in_strong = False
            return

        if tag in ('em', 'i'):
            self._flush_text()
            self.in_em = False
            return

        if self.in_table:
            if tag in ('td', 'th'):
                self.current_row.append({
                    'text': self.current_cell_text.strip(),
                    'is_header': self.in_th,
                })
                self.in_th = False
                self.in_td = False

            elif tag == 'tr':
                if self.current_row:
                    self.table_data.append(self.current_row)
                self.current_row = []

            elif tag == 'table':
                self.in_table = False
                self._build_table()

            return

        if tag in ('p', 'div', 'h1', 'h2', 'h3'):
            self._flush_text()
            self.current_paragraph = None

    def handle_data(self, data):
        if self.skip_content:
            return

        if self.in_table and (self.in_th or self.in_td):
            self.current_cell_text += data
            return

        text = data
        if text:
            self._ensure_paragraph()
            self.pending_text += text

    def _build_table(self):
        """Build a Word table from parsed table data"""
        if not self.table_data:
            return

        max_cols = max(len(row) for row in self.table_data)
        if max_cols == 0:
            return

        table = self.doc.add_table(rows=len(self.table_data), cols=max_cols)
        table.style = 'Table Grid'
        table.alignment = WD_TABLE_ALIGNMENT.CENTER

        for i, row_data in enumerate(self.table_data):
            for j, cell_data in enumerate(row_data):
                if j >= max_cols:
                    break
                cell = table.cell(i, j)
                cell.text = cell_data['text']
                para = cell.paragraphs[0]
                run = para.runs[0] if para.runs else para.add_run(cell_data['text'])
                run.font.size = Pt(10)
                run.font.name = 'Cambria'

                if cell_data['is_header'] or i == 0:
                    run.bold = True
                    shading = cell._tc.get_or_add_tcPr()
                    bg = etree.SubElement(shading, qn('w:shd'))
                    bg.set(qn('w:val'), 'clear')
                    bg.set(qn('w:color'), 'auto')
                    bg.set(qn('w:fill'), '1E3A5F')
                    run.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

        self.table_data = []


def html_to_docx(html_content, title="Dokumen"):
    """Convert HTML content with LaTeX math to a proper DOCX file"""
    doc = Document()

    # Set default font
    style = doc.styles['Normal']
    font = style.font
    font.name = 'Cambria'
    font.size = Pt(11)

    # Set math font
    style2 = doc.styles['Heading 2']
    style2.font.name = 'Cambria'
    style2.font.size = Pt(14)
    style2.font.color.rgb = RGBColor(0x1E, 0x3A, 0x5F)
    style2.font.bold = True

    style3 = doc.styles['Heading 3']
    style3.font.name = 'Cambria'
    style3.font.size = Pt(12)
    style3.font.color.rgb = RGBColor(0x1E, 0x3A, 0x5F)

    # Clean HTML: remove diagram placeholders
    html_content = re.sub(r'\[DIAGRAM:[^\]]+\]', '[Lihat Diagram di Aplikasi]', html_content)

    # Parse and build document
    parser = HTMLToDocxParser(doc)
    parser.feed(html_content)
    parser._flush_text()

    # Save to buffer
    buffer = io.BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer
