import PyPDF2
import io
import os
from datetime import datetime

class PDFService:
    @staticmethod
    def get_page_count(file_path):
        """Get number of pages in PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception:
            return 0
    
    @staticmethod
    def generate_preview(file_path, pages=2):
        """Generate PDF preview (first few pages)"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                if total_pages == 0:
                    return None
                
                # Create preview with specified number of pages
                preview_writer = PyPDF2.PdfWriter()
                
                for i in range(min(pages, total_pages)):
                    preview_writer.add_page(pdf_reader.pages[i])
                
                # Save preview to memory
                preview_buffer = io.BytesIO()
                preview_writer.write(preview_buffer)
                preview_buffer.seek(0)
                
                return {
                    'preview_buffer': preview_buffer,
                    'total_pages': total_pages,
                    'preview_pages': min(pages, total_pages)
                }
                
        except Exception:
            return None
    
    @staticmethod
    def extract_text(file_path, page_range=None):
        """Extract text from PDF"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                if page_range:
                    start_page, end_page = page_range
                    for i in range(start_page, min(end_page, len(pdf_reader.pages))):
                        text += pdf_reader.pages[i].extract_text() + "\n"
                else:
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                
                return {
                    'text': text,
                    'pages': len(pdf_reader.pages)
                }
                
        except Exception:
            return {'text': '', 'pages': 0}
    
    @staticmethod
    def get_metadata(file_path):
        """Extract PDF metadata"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = {
                    'pages': len(pdf_reader.pages),
                    'title': pdf_reader.metadata.get('/Title', ''),
                    'author': pdf_reader.metadata.get('/Author', ''),
                    'subject': pdf_reader.metadata.get('/Subject', ''),
                    'creator': pdf_reader.metadata.get('/Creator', ''),
                    'producer': pdf_reader.metadata.get('/Producer', ''),
                    'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                    'modification_date': pdf_reader.metadata.get('/ModDate', '')
                }
                
                return metadata
                
        except Exception:
            return {'pages': 0}
    
    @staticmethod
    def merge_pdfs(file_paths, output_path):
        """Merge multiple PDFs"""
        try:
            merger = PyPDF2.PdfMerger()
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    merger.append(file_path)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                merger.write(f)
            
            merger.close()
            return True, "PDFs merged successfully"
            
        except Exception as e:
            return False, f"Error merging PDFs: {str(e)}"
    
    @staticmethod
    def split_pdf(file_path, page_ranges, output_dir):
        """Split PDF into multiple files"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                output_files = []
                
                for i, page_range in enumerate(page_ranges):
                    if isinstance(page_range, int):
                        start = page_range
                        end = page_range
                    elif isinstance(page_range, (list, tuple)) and len(page_range) == 2:
                        start, end = page_range
                    else:
                        continue
                    
                    # Validate page range
                    if start < 1 or end > total_pages or start > end:
                        continue
                    
                    # Create new PDF
                    writer = PyPDF2.PdfWriter()
                    
                    for page_num in range(start - 1, end):
                        writer.add_page(pdf_reader.pages[page_num])
                    
                    # Save split file
                    output_path = os.path.join(output_dir, f"split_{i+1}_{start}-{end}.pdf")
                    os.makedirs(output_dir, exist_ok=True)
                    
                    with open(output_path, 'wb') as f:
                        writer.write(f)
                    
                    output_files.append(output_path)
                
                return True, f"PDF split into {len(output_files)} files"
                
        except Exception as e:
            return False, f"Error splitting PDF: {str(e)}"
    
    @staticmethod
    def validate_pdf(file_path):
        """Validate PDF file"""
        try:
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
                return True, "Valid PDF file"
        except Exception as e:
            return False, f"Invalid PDF file: {str(e)}"
    
    @staticmethod
    def is_encrypted(file_path):
        """Check if PDF is encrypted"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return pdf_reader.is_encrypted
        except Exception:
            return False
    
    @staticmethod
    def get_page_dimensions(file_path, page_num=0):
        """Get page dimensions"""
        try:
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if page_num >= len(pdf_reader.pages):
                    return None
                
                page = pdf_reader.pages[page_num]
                return {
                    'width': page.mediabox.width,
                    'height': page.mediabox.height,
                    'rotation': page.rotation
                }
        except Exception:
            return None

# Create instance
pdf_service = PDFService()
