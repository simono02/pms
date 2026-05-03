import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app
import PyPDF2
import io
from datetime import datetime

class FileService:
    ALLOWED_EXTENSIONS = {'pdf'}
    MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB
    
    @staticmethod
    def allowed_file(filename):
        """Check if file has allowed extension"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in FileService.ALLOWED_EXTENSIONS
    
    @staticmethod
    def validate_file(file):
        """Validate uploaded file"""
        errors = []
        
        if not file:
            errors.append('No file provided')
            return {'valid': False, 'errors': errors}
        
        if file.filename == '':
            errors.append('No file selected')
            return {'valid': False, 'errors': errors}
        
        if not FileService.allowed_file(file.filename):
            errors.append('File type not allowed. Only PDF files are allowed.')
        
        if file.content_length > FileService.MAX_FILE_SIZE:
            errors.append('File too large. Maximum size is 16MB.')
        
        return {
            'valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def generate_unique_filename(filename):
        """Generate unique filename"""
        secure_name = secure_filename(filename)
        unique_id = uuid.uuid4().hex
        name, ext = os.path.splitext(secure_name)
        return f"{name}_{unique_id}{ext}"
    
    @staticmethod
    def save_file(file, file_type='projects'):
        """Save uploaded file"""
        try:
            # Validate file
            validation = FileService.validate_file(file)
            if not validation['valid']:
                return {'success': False, 'message': validation['errors'][0]}
            
            # Generate unique filename
            unique_filename = FileService.generate_unique_filename(file.filename)
            
            # Create upload directory if it doesn't exist
            upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], file_type)
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            
            # Get file size
            file_size = os.path.getsize(file_path)
            
            return {
                'success': True,
                'file_path': file_path,
                'original_filename': file.filename,
                'unique_filename': unique_filename,
                'file_size': file_size,
                'file_type': file_type
            }
            
        except Exception as e:
            return {'success': False, 'message': f'File upload failed: {str(e)}'}
    
    @staticmethod
    def delete_file(file_path):
        """Delete file from storage"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return {'success': True, 'message': 'File deleted successfully'}
            else:
                return {'success': False, 'message': 'File not found'}
                
        except Exception as e:
            return {'success': False, 'message': f'File deletion failed: {str(e)}'}
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            file_size = stat.st_size
            created_at = datetime.fromtimestamp(stat.st_ctime)
            modified_at = datetime.fromtimestamp(stat.st_mtime)
            
            file_name = os.path.basename(file_path)
            file_extension = file_name.rsplit('.', 1)[1].lower() if '.' in file_name else ''
            
            return {
                'file_path': file_path,
                'file_name': file_name,
                'file_size': file_size,
                'file_extension': file_extension,
                'mime_type': 'application/pdf' if file_extension == 'pdf' else 'application/octet-stream',
                'created_at': created_at,
                'modified_at': modified_at,
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK)
            }
            
        except Exception as e:
            return None
    
    @staticmethod
    def get_pdf_metadata(file_path):
        """Get PDF metadata"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return {'error': 'Not a PDF file'}
            
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
                
        except Exception as e:
            return {'error': f'Failed to read PDF metadata: {str(e)}'}
    
    @staticmethod
    def generate_pdf_preview(file_path, pages=2):
        """Generate PDF preview (first few pages)"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return None
            
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
                
                # Generate preview URL (in a real app, this would be saved to a temporary location)
                preview_filename = f"preview_{uuid.uuid4().hex}.pdf"
                preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'previews', preview_filename)
                
                os.makedirs(os.path.dirname(preview_path), exist_ok=True)
                
                with open(preview_path, 'wb') as f:
                    f.write(preview_buffer.getvalue())
                
                return {
                    'preview_path': preview_path,
                    'preview_filename': preview_filename,
                    'total_pages': total_pages,
                    'preview_pages': min(pages, total_pages)
                }
                
        except Exception as e:
            return None
    
    @staticmethod
    def get_page_count(file_path):
        """Get number of pages in PDF"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return 0
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
                
        except Exception as e:
            return 0
    
    @staticmethod
    def validate_pdf(file_path):
        """Validate PDF file integrity"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return {'valid': False, 'error': 'Not a PDF file'}
            
            with open(file_path, 'rb') as file:
                PyPDF2.PdfReader(file)
                return {'valid': True, 'pages': FileService.get_page_count(file_path)}
                
        except Exception as e:
            return {'valid': False, 'error': f'PDF validation failed: {str(e)}'}
    
    @staticmethod
    def compress_pdf(file_path, quality=0.8):
        """Compress PDF file"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return {'success': False, 'message': 'Not a PDF file'}
            
            # TODO: Implement PDF compression
            # This would require additional libraries like PyPDF2 with compression
            
            return {
                'success': False,
                'message': 'PDF compression not implemented'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'PDF compression failed: {str(e)}'}
    
    @staticmethod
    def merge_pdfs(file_paths, output_filename):
        """Merge multiple PDFs"""
        try:
            if not all(path.lower().endswith('.pdf') for path in file_paths):
                return {'success': False, 'message': 'All files must be PDFs'}
            
            merger = PyPDF2.PdfMerger()
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    merger.append(file_path)
            
            # Create output path
            output_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'merged', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            merger.write(output_path)
            merger.close()
            
            return {
                'success': True,
                'output_path': output_path,
                'message': 'PDFs merged successfully'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'PDF merge failed: {str(e)}'}
    
    @staticmethod
    def split_pdf(file_path, split_points):
        """Split PDF into multiple files"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return {'success': False, 'message': 'Not a PDF file'}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                # Validate split points
                if not all(0 <= point <= total_pages for point in split_points):
                    return {'success': False, 'message': 'Invalid split points'}
                
                # Create split files
                split_files = []
                start_page = 0
                
                for i, end_page in enumerate(split_points + [total_pages]):
                    if start_page < end_page:
                        writer = PyPDF2.PdfWriter()
                        
                        for page_num in range(start_page, end_page):
                            writer.add_page(pdf_reader.pages[page_num])
                        
                        # Save split file
                        split_filename = f"split_{i+1}_{uuid.uuid4().hex}.pdf"
                        split_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'splits', split_filename)
                        os.makedirs(os.path.dirname(split_path), exist_ok=True)
                        
                        with open(split_path, 'wb') as f:
                            writer.write(f)
                        
                        split_files.append({
                            'filename': split_filename,
                            'path': split_path,
                            'pages': end_page - start_page
                        })
                    
                    start_page = end_page
                
                return {
                    'success': True,
                    'split_files': split_files,
                    'message': f'PDF split into {len(split_files)} files'
                }
                
        except Exception as e:
            return {'success': False, 'message': f'PDF split failed: {str(e)}'}
    
    @staticmethod
    def extract_text_from_pdf(file_path):
        """Extract text from PDF"""
        try:
            if not file_path.lower().endswith('.pdf'):
                return {'success': False, 'message': 'Not a PDF file'}
            
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                
                return {
                    'success': True,
                    'text': text,
                    'pages': len(pdf_reader.pages)
                }
                
        except Exception as e:
            return {'success': False, 'message': f'Text extraction failed: {str(e)}'}
    
    @staticmethod
    def get_storage_usage():
        """Get storage usage statistics"""
        try:
            upload_folder = current_app.config['UPLOAD_FOLDER']
            
            if not os.path.exists(upload_folder):
                return {
                    'total_size': 0,
                    'file_count': 0,
                    'by_type': {}
                }
            
            total_size = 0
            file_count = 0
            by_type = {}
            
            for root, dirs, files in os.walk(upload_folder):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_size = os.path.getsize(file_path)
                    
                    total_size += file_size
                    file_count += 1
                    
                    # Categorize by directory
                    relative_path = os.path.relpath(root, upload_folder)
                    category = relative_path.split(os.sep)[0] if os.sep in relative_path else 'other'
                    
                    if category not in by_type:
                        by_type[category] = {'size': 0, 'count': 0}
                    
                    by_type[category]['size'] += file_size
                    by_type[category]['count'] += 1
            
            return {
                'total_size': total_size,
                'file_count': file_count,
                'by_type': by_type
            }
            
        except Exception as e:
            return {
                'total_size': 0,
                'file_count': 0,
                'by_type': {},
                'error': str(e)
            }
    
    @staticmethod
    def cleanup_temp_files():
        """Clean up temporary files"""
        try:
            temp_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
            
            if not os.path.exists(temp_folder):
                return {'success': True, 'message': 'No temp folder found'}
            
            deleted_count = 0
            current_time = datetime.now()
            
            for file in os.listdir(temp_folder):
                file_path = os.path.join(temp_folder, file)
                
                if os.path.isfile(file_path):
                    # Delete files older than 24 hours
                    file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                    
                    if (current_time - file_time).total_seconds() > 24 * 60 * 60:
                        os.remove(file_path)
                        deleted_count += 1
            
            return {
                'success': True,
                'message': f'Cleaned up {deleted_count} temporary files'
            }
            
        except Exception as e:
            return {'success': False, 'message': f'Cleanup failed: {str(e)}'}


# Create instance for direct use
file_service = FileService()
