from crewai.tools import BaseTool
from typing import Type
from pydantic import BaseModel, Field
import pdfplumber
import os

class PDFReaderInput(BaseModel):
    """Input schema for PDFReader."""
    file_path: str = Field(..., description="Path to the PDF file to read.")
    page_numbers: list[int] = Field(default=None, description="Specific page numbers to read. If None, reads all pages.")

class PDFReader(BaseTool):
    name: str = "PDF Reader"
    description: str = "A tool for reading PDF files with support for multiple languages including CJK (Chinese, Japanese, Korean)."
    args_schema: Type[BaseModel] = PDFReaderInput

    def _run(self, file_path: str, page_numbers: list[int] = None) -> str:
        try:
            if not os.path.exists(file_path):
                return f"Error: The file at {file_path} was not found."

            with pdfplumber.open(file_path) as pdf:
                result = {
                    'total_pages': len(pdf.pages),
                    'pages': []
                }

                # If no specific pages are requested, read all pages
                pages_to_read = page_numbers if page_numbers else range(len(pdf.pages))

                for page_num in pages_to_read:
                    if page_num < 0 or page_num >= len(pdf.pages):
                        continue

                    page = pdf.pages[page_num]
                    
                    # Extract text with layout information
                    text = page.extract_text(x_tolerance=3, y_tolerance=3)
                    
                    # Extract tables if any
                    tables = page.extract_tables()
                    
                    # Get page dimensions
                    width = page.width
                    height = page.height

                    # Extract text with position information
                    words = page.extract_words(
                        x_tolerance=3,
                        y_tolerance=3,
                        keep_blank_chars=True,
                        use_text_flow=True,
                        horizontal_ltr=True
                    )

                    page_info = {
                        'page_number': page_num + 1,
                        'width': width,
                        'height': height,
                        'text': text,
                        'tables': [
                            [
                                [cell if cell is not None else "" for cell in row]
                                for row in table
                            ]
                            for table in tables
                        ],
                        'words': [
                            {
                                'text': word['text'],
                                'position': {
                                    'x0': word['x0'],
                                    'y0': word['top'],
                                    'x1': word['x1'],
                                    'y1': word['bottom']
                                }
                            }
                            for word in words
                        ]
                    }
                    
                    result['pages'].append(page_info)

                return str(result)

        except Exception as e:
            return f"Error reading PDF file: {str(e)}"
