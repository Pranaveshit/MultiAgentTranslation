from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.cidfonts import UnicodeCIDFont
import os

class PDFWriterInput(BaseModel):
    """Input schema for PDFWriter."""
    translated_text: dict = Field(..., description="Dictionary containing the translated text")
    output_path: str = Field(..., description="Path where to save the translated PDF")

class PDFWriter(BaseTool):
    name: str = "PDF Writer"
    description: str = "A tool for creating readable PDFs from translated text."
    args_schema: Type[BaseModel] = PDFWriterInput

    def _run(self, translated_text: dict, output_path: str) -> str:
        try:
            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Create the PDF document
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=inch,
                leftMargin=inch,
                topMargin=inch,
                bottomMargin=inch
            )

            # Try to register CJK fonts for better character support
            try:
                for font in ['HeiseiMin-W3', 'HeiseiKakuGo-W5', 'HYSMyeongJo-Medium']:
                    try:
                        pdfmetrics.registerFont(UnicodeCIDFont(font))
                        break
                    except:
                        continue
            except:
                pass  # Use default font if CJK fonts aren't available

            # Create styles
            styles = getSampleStyleSheet()
            
            # Custom style for title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1  # Center alignment
            )
            
            # Custom style for headers
            header_style = ParagraphStyle(
                'CustomHeader',
                parent=styles['Heading2'],
                fontSize=14,
                spaceBefore=20,
                spaceAfter=10
            )
            
            # Custom style for normal text
            text_style = ParagraphStyle(
                'CustomText',
                parent=styles['Normal'],
                fontSize=11,
                leading=14,  # Line spacing
                spaceAfter=8
            )

            # Build the document content
            story = []

            # Add title if it exists
            if 'title' in translated_text:
                story.append(Paragraph(translated_text['title'], title_style))
                story.append(Spacer(1, 20))

            # Process the translated text
            for key, text in translated_text.items():
                if key == 'title':  # Skip title as it's already added
                    continue
                    
                if isinstance(text, str):
                    # Determine if this is likely a header (shorter text, ends with newline)
                    if len(text.strip()) < 100 and text.strip().endswith('\n'):
                        story.append(Paragraph(text.strip(), header_style))
                    else:
                        # Split text into paragraphs
                        paragraphs = text.split('\n\n')
                        for para in paragraphs:
                            if para.strip():
                                story.append(Paragraph(para.strip(), text_style))
                                story.append(Spacer(1, 8))

            # Build the PDF
            doc.build(story)
            return f"Successfully created translated PDF at {output_path}"

        except Exception as e:
            return f"Error creating PDF: {str(e)}" 