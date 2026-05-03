import os
import uuid
import hashlib
from datetime import datetime
from werkzeug.utils import secure_filename

class FileUtils:
    @staticmethod
    def get_file_extension(filename):
        """Get file extension"""
        if not filename:
            return ""
        
        return filename.lower().split('.')[-1] if '.' in filename else ''
    
    @staticmethod
    def get_file_name(filename):
        """Get file name without extension"""
        if not filename:
            return ""
        
        return os.path.splitext(filename)[0]
    
    @staticmethod
    def format_file_size(size_bytes):
        """Format file size in human readable format"""
        try:
            size = int(size_bytes)
            if size == 0:
                return "0 B"
            
            size_names = ["B", "KB", "MB", "GB", "TB"]
            i = 0
            while size >= 1024 and i < len(size_names) - 1:
                size /= 1024.0
                i += 1
            
            return f"{size:.1f} {size_names[i]}"
        except (ValueError, TypeError):
            return "0 B"
    
    @staticmethod
    def validate_file_type(filename, allowed_types=None):
        """Validate file type"""
        if not filename:
            return False, "Filename is required"
        
        extension = FileUtils.get_file_extension(filename)
        
        if allowed_types is None:
            allowed_types = ['pdf']
        
        return extension in allowed_types, f"File type .{extension} not allowed"
    
    @staticmethod
    def validate_file_size(file_size, min_size=0, max_size=None):
        """Validate file size"""
        if max_size is None:
            max_size = 16 * 1024 * 1024  # 16MB default
        
        if file_size < min_size:
            return False, f"File size must be at least {min_size} bytes"
        
        if file_size > max_size:
            return False, f"File size must be no more than {max_size} bytes"
        
        return True, None
    
    @staticmethod
    def generate_unique_filename(filename):
        """Generate unique filename"""
        secure_name = secure_filename(filename)
        unique_id = uuid.uuid4().hex
        name, ext = os.path.splitext(secure_name)
        return f"{name}_{unique_id}{ext}"
    
    @staticmethod
    def sanitize_filename(filename):
        """Sanitize filename"""
        if not filename:
            return ""
        
        # Remove dangerous characters
        dangerous_chars = ['../', '..\\', '/', '\\', '|', ';', '<', '>', '"', "'", '`', '$', '(', ')', '{', '}', '%', '!']
        
        for char in dangerous_chars:
            filename = filename.replace(char, '_')
        
        # Remove consecutive underscores
        filename = filename.replace(' ', '_')
        filename = filename.replace('-', '_')
        
        # Remove multiple underscores
        while '__' in filename:
            filename = filename.replace('__', '_')
        
        # Remove leading/trailing underscores
        filename = filename.strip('_')
        
        return filename
    
    @staticmethod
    def is_safe_filename(filename):
        """Check if filename is safe"""
        if not filename:
            return False
        
        dangerous_patterns = ['../', '..\\', '/', '\\', '|', ';', '<', '>', '"', "'", '`', '$', '(', ')', '{', '}', '%', '!']
        
        for pattern in dangerous_patterns:
            if pattern in filename:
                return False
        
        return True
    
    @staticmethod
    def create_file_path(base_path, filename, create_dirs=True):
        """Create full file path"""
        if not base_path or not filename:
            return None
        
        # Sanitize filename
        safe_filename = FileUtils.sanitize_filename(filename)
        
        # Create full path
        full_path = os.path.join(base_path, safe_filename)
        
        # Create directories if needed
        if create_dirs:
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        return full_path
    
    @staticmethod
    def save_file(file, directory, filename=None):
        """Save file to directory"""
        if not file:
            return None, "No file provided"
        
        if filename is None:
            filename = file.filename
        
        # Generate unique filename
        unique_filename = FileUtils.generate_unique_filename(filename)
        
        # Create full path
        full_path = os.path.join(directory, unique_filename)
        
        # Create directory if it doesn't exist
        os.makedirs(directory, exist_ok=True)
        
        # Save file
        file.save(full_path)
        
        return full_path, unique_filename
    
    @staticmethod
    def delete_file(file_path):
        """Delete file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True, "File deleted successfully"
            else:
                return False, "File not found"
        except Exception as e:
            return False, f"Error deleting file: {str(e)}"
    
    @staticmethod
    def copy_file(src_path, dest_path):
        """Copy file"""
        try:
            import shutil
            shutil.copy2(src_path, dest_path)
            return True, "File copied successfully"
        except Exception as e:
            return False, f"Error copying file: {str(e)}"
    
    @staticmethod
    def move_file(src_path, dest_path):
        """Move file"""
        try:
            import shutil
            shutil.move(src_path, dest_path)
            return True, "File moved successfully"
        except Exception as e:
            return False, f"Error moving file: {str(e)}"
    
    @staticmethod
    def get_file_info(file_path):
        """Get file information"""
        try:
            if not os.path.exists(file_path):
                return None
            
            stat = os.stat(file_path)
            
            return {
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'size_formatted': FileUtils.format_file_size(stat.st_size),
                'extension': FileUtils.get_file_extension(file_path),
                'created_at': datetime.fromtimestamp(stat.st_ctime),
                'modified_at': datetime.fromtimestamp(stat.st_mtime),
                'readable': os.access(file_path, os.R_OK),
                'writable': os.access(file_path, os.W_OK),
                'executable': os.access(file_path, os.X_OK)
            }
        except Exception:
            return None
    
    @staticmethod
    def get_file_hash(file_path, algorithm='md5'):
        """Get file hash"""
        try:
            if not os.path.exists(file_path):
                return None
            
            hash_obj = hashlib.md5()
            
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_obj.update(chunk)
            
            return hash_obj.hexdigest()
        except Exception:
            return None
    
    @staticmethod
    def compress_image(file_path, quality=85):
        """Compress image file"""
        try:
            from PIL import Image
            
            if not os.path.exists(file_path):
                return None, "File not found"
            
            # Check if file is an image
            try:
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Create compressed filename
                    name, ext = os.path.splitext(file_path)
                    compressed_path = f"{name}_compressed.jpg"
                    
                    # Save compressed image
                    img.save(compressed_path, 'JPEG', quality=quality, optimize=True)
                    
                    return compressed_path, "Image compressed successfully"
            except Exception as e:
                return None, f"Error processing image: {str(e)}"
        except ImportError:
            return None, "PIL library not available"
        except Exception as e:
            return None, f"Error compressing image: {str(e)}"
    
    @staticmethod
    def create_thumbnail(file_path, size=(150, 150)):
        """Create thumbnail"""
        try:
            from PIL import Image
            
            if not os.path.exists(file_path):
                return None, "File not found"
            
            # Check if file is an image
            try:
                with Image.open(file_path) as img:
                    # Convert to RGB if necessary
                    if img.mode in ('RGBA', 'LA', 'P'):
                        img = img.convert('RGB')
                    
                    # Create thumbnail
                    img.thumbnail(size, Image.Resampling.LANCZOS)
                    
                    # Create thumbnail filename
                    name, ext = os.path.splitext(file_path)
                    thumb_path = f"{name}_thumb.jpg"
                    
                    # Save thumbnail
                    img.save(thumb_path, 'JPEG', quality=85)
                    
                    return thumb_path, "Thumbnail created successfully"
            except Exception as e:
                return None, f"Error processing image: {str(e)}"
        except ImportError:
            return None, "PIL library not available"
        except Exception as e:
            return None, f"Error creating thumbnail: {str(e)}"
    
    @staticmethod
    def get_image_dimensions(file_path):
        """Get image dimensions"""
        try:
            from PIL import Image
            
            if not os.path.exists(file_path):
                return None
            
            with Image.open(file_path) as img:
                return {
                    'width': img.width,
                    'height': img.height,
                    'mode': img.mode,
                    'format': img.format
                }
        except ImportError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def extract_metadata(file_path):
        """Extract file metadata"""
        try:
            import PyPDF2
            
            if not os.path.exists(file_path):
                return None
            
            if not file_path.lower().endswith('.pdf'):
                return None
            
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
        except ImportError:
            return None
        except Exception:
            return None
    
    @staticmethod
    def merge_pdfs(file_paths, output_path):
        """Merge multiple PDF files"""
        try:
            import PyPDF2
            
            merger = PyPDF2.PdfMerger()
            
            for file_path in file_paths:
                if os.path.exists(file_path):
                    merger.append(file_path)
            
            # Create output directory if needed
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            merger.write(output_path)
            merger.close()
            
            return True, "PDFs merged successfully"
        except ImportError:
            return False, "PyPDF2 library not available"
        except Exception as e:
            return False, f"Error merging PDFs: {str(e)}"
    
    @staticmethod
    def split_pdf(file_path, page_ranges, output_dir):
        """Split PDF into multiple files"""
        try:
            import PyPDF2
            
            if not os.path.exists(file_path):
                return False, "Source file not found"
            
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
        except ImportError:
            return False, "PyPDF2 library not available"
        except Exception as e:
            return False, f"Error splitting PDF: {str(e)}"
    
    @staticmethod
    def get_storage_usage(directory):
        """Get storage usage statistics"""
        try:
            if not os.path.exists(directory):
                return {
                    'total_size': 0,
                    'file_count': 0,
                    'directory_count': 0
                }
            
            total_size = 0
            file_count = 0
            directory_count = 0
            
            for root, dirs, files in os.walk(directory):
                directory_count += len(dirs)
                
                for file in files:
                    file_path = os.path.join(root, file)
                    if os.path.isfile(file_path):
                        file_count += 1
                        total_size += os.path.getsize(file_path)
            
            return {
                'total_size': total_size,
                'total_size_formatted': FileUtils.format_file_size(total_size),
                'file_count': file_count,
                'directory_count': directory_count
            }
        except Exception:
            return {
                'total_size': 0,
                'file_count': 0,
                'directory_count': 0
            }
    
    @staticmethod
    def cleanup_temp_files(temp_dir, max_age_hours=24):
        """Clean up temporary files older than specified hours"""
        try:
            if not os.path.exists(temp_dir):
                return True, "Temp directory does not exist"
            
            current_time = datetime.now()
            cutoff_time = current_time - timedelta(hours=max_age_hours)
            
            deleted_count = 0
            
            for root, dirs, files in os.walk(temp_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    if os.path.isfile(file_path):
                        file_time = datetime.fromtimestamp(os.path.getmtime(file_path))
                        
                        if file_time < cutoff_time:
                            os.remove(file_path)
                            deleted_count += 1
            
            return True, f"Cleaned up {deleted_count} temporary files"
        except Exception as e:
            return False, f"Error cleaning up temp files: {str(e)}"

# Create instance
file_utils = FileUtils()
