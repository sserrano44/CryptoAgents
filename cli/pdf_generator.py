"""
PDF Report Generator for CryptoAgents Trading Reports
"""

import os
import re
import datetime
from typing import Optional
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.colors import HexColor
import markdown


class CryptoReportPDFGenerator:
    """Generates PDF reports from CryptoAgents trading analysis."""
    
    def __init__(self, crypto_symbol: str, analysis_date: str):
        self.crypto_symbol = crypto_symbol.upper()
        self.analysis_date = analysis_date
        self.styles = self._create_styles()
        
    def _create_styles(self):
        """Create custom paragraph styles for the PDF report."""
        styles = getSampleStyleSheet()
        
        # Custom title style
        styles.add(ParagraphStyle(
            name='CryptoTitle',
            parent=styles['Title'],
            fontSize=24,
            textColor=HexColor('#1f4e79'),
            spaceAfter=30,
            alignment=1  # Center alignment
        ))
        
        # Custom heading styles
        styles.add(ParagraphStyle(
            name='CryptoHeading1',
            parent=styles['Heading1'],
            fontSize=18,
            textColor=HexColor('#2e5c8a'),
            spaceBefore=20,
            spaceAfter=12
        ))
        
        styles.add(ParagraphStyle(
            name='CryptoHeading2',
            parent=styles['Heading2'],
            fontSize=16,
            textColor=HexColor('#4472a8'),
            spaceBefore=16,
            spaceAfter=10
        ))
        
        styles.add(ParagraphStyle(
            name='CryptoHeading3',
            parent=styles['Heading3'],
            fontSize=14,
            textColor=HexColor('#5a87c6'),
            spaceBefore=12,
            spaceAfter=8
        ))
        
        # Custom body style
        styles.add(ParagraphStyle(
            name='CryptoBody',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=8,
            textColor=HexColor('#333333'),
            leading=14
        ))
        
        # Metadata style
        styles.add(ParagraphStyle(
            name='CryptoMeta',
            parent=styles['Normal'],
            fontSize=10,
            textColor=HexColor('#666666'),
            alignment=1,  # Center alignment
            spaceAfter=20
        ))
        
        return styles
    
    def _clean_markdown_text(self, text: str) -> str:
        """Clean and prepare markdown text for PDF conversion."""
        if not text:
            return ""
            
        # Remove markdown headers and replace with simpler formatting
        text = re.sub(r'^#{4,}\s*', '• ', text, flags=re.MULTILINE)
        text = re.sub(r'^#{3}\s*', '### ', text, flags=re.MULTILINE)
        text = re.sub(r'^#{2}\s*', '## ', text, flags=re.MULTILINE)
        text = re.sub(r'^#{1}\s*', '# ', text, flags=re.MULTILINE)
        
        # Clean up excessive whitespace
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        
        return text
    
    def _convert_markdown_to_paragraphs(self, markdown_text: str) -> list:
        """Convert markdown text to reportlab paragraph objects."""
        if not markdown_text:
            return []
            
        cleaned_text = self._clean_markdown_text(markdown_text)
        paragraphs = []
        
        # Split text into sections
        sections = cleaned_text.split('\n\n')
        
        for section in sections:
            if not section.strip():
                continue
                
            lines = section.strip().split('\n')
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Determine paragraph style based on content
                if line.startswith('# '):
                    content = line[2:].strip()
                    paragraphs.append(Paragraph(content, self.styles['CryptoHeading1']))
                elif line.startswith('## '):
                    content = line[3:].strip()
                    paragraphs.append(Paragraph(content, self.styles['CryptoHeading2']))
                elif line.startswith('### '):
                    content = line[4:].strip()
                    paragraphs.append(Paragraph(content, self.styles['CryptoHeading3']))
                else:
                    # Regular paragraph - escape HTML special characters
                    content = line.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
                    # Handle bold markdown
                    content = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', content)
                    # Handle italic markdown
                    content = re.sub(r'\*(.*?)\*', r'<i>\1</i>', content)
                    paragraphs.append(Paragraph(content, self.styles['CryptoBody']))
            
            # Add spacing between sections
            if paragraphs:
                paragraphs.append(Spacer(1, 12))
        
        return paragraphs
    
    def generate_pdf_report(self, final_report: str, output_dir: str = "reports", 
                          timestamp: str = None) -> str:
        """
        Generate a PDF report from the final markdown report.
        
        Args:
            final_report: The complete markdown report content
            output_dir: Directory to save the PDF file
            timestamp: Optional timestamp string for filename consistency
            
        Returns:
            str: Path to the generated PDF file
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Use provided timestamp or generate new one
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate filename
        filename = f"{self.crypto_symbol}_{self.analysis_date}_trading_report_{timestamp}.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create PDF document
        doc = SimpleDocTemplate(
            filepath,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=18
        )
        
        # Build document content
        story = []
        
        # Title page
        title = f"{self.crypto_symbol} Trading Analysis Report"
        story.append(Paragraph(title, self.styles['CryptoTitle']))
        
        # Metadata
        meta_info = f"Analysis Date: {self.analysis_date}<br/>Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}<br/>CryptoAgents Multi-Agent Framework"
        story.append(Paragraph(meta_info, self.styles['CryptoMeta']))
        
        story.append(Spacer(1, 30))
        
        # Convert markdown content to paragraphs
        if final_report:
            content_paragraphs = self._convert_markdown_to_paragraphs(final_report)
            story.extend(content_paragraphs)
        else:
            story.append(Paragraph("No report content available.", self.styles['CryptoBody']))
        
        # Build PDF
        doc.build(story)
        
        return filepath
    
    def save_markdown_report(self, final_report: str, output_dir: str = "reports", 
                           timestamp: str = None) -> str:
        """
        Save the markdown report to a file.
        
        Args:
            final_report: The complete markdown report content
            output_dir: Directory to save the markdown file
            timestamp: Optional timestamp string for filename consistency
            
        Returns:
            str: Path to the saved markdown file
        """
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Use provided timestamp or generate new one
        if timestamp is None:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Generate filename
        filename = f"{self.crypto_symbol}_{self.analysis_date}_trading_report_{timestamp}.md"
        filepath = os.path.join(output_dir, filename)
        
        # Create enhanced markdown content with metadata
        enhanced_content = f"""# {self.crypto_symbol} Trading Analysis Report

**Analysis Date:** {self.analysis_date}  
**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Framework:** CryptoAgents Multi-Agent Framework  

---

{final_report if final_report else 'No report content available.'}

---

*Report generated by CryptoAgents Multi-Agent Cryptocurrency Trading Framework*
"""
        
        # Write markdown file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(enhanced_content)
        
        return filepath


def generate_trading_report_pdf(crypto_symbol: str, analysis_date: str, 
                              final_report: str, output_dir: str = "reports") -> tuple[str, str]:
    """
    Convenience function to generate both PDF and markdown trading reports.
    
    Args:
        crypto_symbol: The cryptocurrency symbol (e.g., 'BTC')
        analysis_date: The analysis date in YYYY-MM-DD format
        final_report: The complete markdown report content
        output_dir: Directory to save the files (default: 'reports')
        
    Returns:
        tuple[str, str]: Paths to the generated (PDF file, markdown file)
    """
    generator = CryptoReportPDFGenerator(crypto_symbol, analysis_date)
    
    # Generate consistent timestamp for both files
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Generate both files with same timestamp
    pdf_path = generator.generate_pdf_report(final_report, output_dir, timestamp)
    markdown_path = generator.save_markdown_report(final_report, output_dir, timestamp)
    
    return pdf_path, markdown_path