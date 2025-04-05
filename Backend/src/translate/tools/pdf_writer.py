from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
import os

class PDFWriterInput(BaseModel):
    """Input schema for PDFWriter."""
    original_layout: str = Field(..., description="The layout information from PDFReader (as string)")
    translated_text: dict = Field(..., description="Dictionary mapping original text to translated text")
    output_path: str = Field(..., description="Path where to save the translated PDF")
    font_path: str = Field(default=None, description="Path to a TTF font file for CJK support")

class PDFWriter(BaseTool):
    name: str = "PDF Writer"
    description: str = "A tool for recreating PDFs with translated text while maintaining the original layout."
    args_schema: Type[BaseModel] = PDFWriterInput

    def _run(self, original_layout: str, translated_text: dict, output_path: str, font_path: str = None) -> str:
        try:
            # Parse the layout information
            layout_info = eval(original_layout)  # Convert string representation back to dict
            
            # Create the output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Initialize the PDF canvas
            c = canvas.Canvas(output_path)
            
            # Register CJK font if provided
            if font_path and os.path.exists(font_path):
                font_name = os.path.splitext(os.path.basename(font_path))[0]
                pdfmetrics.registerFont(TTFont(font_name, font_path))
            else:
                # Default to built-in fonts
                font_name = 'Helvetica'
            
            for page in layout_info['pages']:
                # Set page size based on original dimensions
                c.setPageSize((page['width'], page['height']))
                
                # Process each word while maintaining position
                for word in page['words']:
                    original_text = word['text']
                    translated = translated_text.get(original_text, original_text)
                    
                    # Get position information
                    pos = word['position']
                    x = pos['x0']
                    y = page['height'] - pos['y1']  # Convert from PDF coordinates
                    
                    # Calculate font size based on the original text box
                    width = pos['x1'] - pos['x0']
                    height = pos['y1'] - pos['y0']
                    font_size = height * 0.9  # Slightly smaller to ensure fit
                    
                    # Set font and size
                    c.setFont(font_name, font_size)
                    
                    # Draw the translated text
                    c.drawString(x, y, translated)
                
                # Process tables if any
                for table in page['tables']:
                    # Table processing would go here
                    # This is a placeholder for table reconstruction
                    pass
                
                c.showPage()
            
            c.save()
            return f"Successfully created translated PDF at {output_path}"

        except Exception as e:
            return f"Error creating PDF: {str(e)}" 