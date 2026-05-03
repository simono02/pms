from flask import Blueprint, request, jsonify, send_file, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.utils import secure_filename
from app import db, limiter
from app.models.project import Project
from app.models.user import User
import os
import uuid
from datetime import datetime
import PyPDF2
import io

bp = Blueprint('files', __name__, url_prefix='/api/files')

ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/upload', methods=['POST'])
@jwt_required()
@limiter.limit("10 per minute")
def upload_file():
    """Upload file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'error': 'No selected file'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'File type not allowed. Only PDF files are allowed.'}), 400
        
        if file.content_length > MAX_FILE_SIZE:
            return jsonify({'error': 'File too large. Maximum size is 16MB.'}), 400
        
        # Get file type from request
        file_type = request.form.get('type', 'projects')
        
        # Generate unique filename
        filename = secure_filename(file.filename)
        unique_filename = f"{uuid.uuid4().hex}_{filename}"
        
        # Create upload directory if it doesn't exist
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], file_type)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Save file
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        return jsonify({
            'message': 'File uploaded successfully',
            'file_path': file_path,
            'original_filename': file.filename,
            'unique_filename': unique_filename,
            'file_size': file_size,
            'file_type': file_type
        }), 201
        
    except Exception as e:
        return jsonify({'error': 'File upload failed', 'details': str(e)}), 500

@bp.route('/download/<int:file_id>', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Download file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement file lookup from database
        # For now, we'll assume the file_id is a path
        file_path = file_id
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if user has permission to download this file
        # This would typically involve checking if the file belongs to the user's projects
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
        
    except Exception as e:
        return jsonify({'error': 'Download failed', 'details': str(e)}), 500

@bp.route('/<int:file_id>', methods=['GET'])
@jwt_required()
def get_file(file_id):
    """Get file information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement file lookup from database
        file_path = file_id
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        file_size = os.path.getsize(file_path)
        file_name = os.path.basename(file_path)
        file_extension = file_name.rsplit('.', 1)[1].lower() if '.' in file_name else ''
        
        return jsonify({
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_extension': file_extension,
            'file_type': 'application/pdf' if file_extension == 'pdf' else 'unknown',
            'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
            'modified_at': datetime.fromtimestamp(os.path.getmtime(file_path)).isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': 'Failed to get file info', 'details': str(e)}), 500

@bp.route('/<int:file_id>/preview', methods=['GET'])
@jwt_required()
def get_file_preview(file_id):
    """Get file preview (first few pages)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement file lookup from database
        file_path = file_id
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Check if file is PDF
        if not file_path.lower().endswith('.pdf'):
            return jsonify({'error': 'Preview only available for PDF files'}), 400
        
        # Get number of pages to preview
        pages = request.args.get('pages', 2, type=int)
        
        try:
            # Open PDF file
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                total_pages = len(pdf_reader.pages)
                
                if total_pages == 0:
                    return jsonify({'error': 'PDF file is empty'}), 400
                
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
                
                return jsonify({
                    'preview_url': f'/api/files/preview/{preview_filename}',
                    'total_pages': total_pages,
                    'preview_pages': min(pages, total_pages),
                    'message': f'Preview generated with {min(pages, total_pages)} pages'
                })
                
        except Exception as e:
            return jsonify({'error': 'Failed to generate preview', 'details': str(e)}), 500
        
    except Exception as e:
        return jsonify({'error': 'Preview generation failed', 'details': str(e)}), 500

@bp.route('/preview/<string:filename>', methods=['GET'])
def serve_preview(filename):
    """Serve preview file"""
    try:
        preview_path = os.path.join(current_app.config['UPLOAD_FOLDER'], 'previews', filename)
        
        if not os.path.exists(preview_path):
            return jsonify({'error': 'Preview not found'}), 404
        
        return send_file(
            preview_path,
            mimetype='application/pdf',
            as_attachment=False,
            download_name=f'preview_{filename}'
        )
        
    except Exception as e:
        return jsonify({'error': 'Failed to serve preview', 'details': str(e)}), 500

@bp.route('/<int:file_id>/thumbnail', methods=['GET'])
@jwt_required()
def get_file_thumbnail(file_id):
    """Generate thumbnail for file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement file lookup from database
        file_path = file_id
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # For PDF files, we could generate a thumbnail of the first page
        if not file_path.lower().endswith('.pdf'):
            return jsonify({'error': 'Thumbnail generation only available for PDF files'}), 400
        
        try:
            # Open PDF and get first page
            with open(file_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                if len(pdf_reader.pages) == 0:
                    return jsonify({'error': 'PDF file is empty'}), 400
                
                # Convert first page to image
                page = pdf_reader.pages[0]
                
                # TODO: Implement PDF to image conversion
                # This would require additional libraries like pdf2image
                
                return jsonify({
                    'message': 'Thumbnail generation not implemented',
                    'note': 'Would require additional libraries like pdf2image'
                }), 501
                
        except Exception as e:
            return jsonify({'error': 'Failed to generate thumbnail', 'details': str(e)}), 500
        
    except Exception as e:
        return jsonify({'error': 'Thumbnail generation failed', 'details': str(e)}), 500

@bp.route('/<int:file_id>/metadata', methods=['GET'])
@jwt_required()
def get_file_metadata(file_id):
    """Get file metadata"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement file lookup from database
        file_path = file_id
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Get file metadata
        stat = os.stat(file_path)
        file_size = stat.st_size
        created_at = datetime.fromtimestamp(stat.st_ctime)
        modified_at = datetime.fromtimestamp(stat.st_mtime)
        
        file_name = os.path.basename(file_path)
        file_extension = file_name.rsplit('.', 1)[1].lower() if '.' in file_name else ''
        
        metadata = {
            'file_id': file_id,
            'file_name': file_name,
            'file_size': file_size,
            'file_extension': file_extension,
            'mime_type': 'application/pdf' if file_extension == 'pdf' else 'application/octet-stream',
            'created_at': created_at.isoformat(),
            'modified_at': modified_at.isoformat(),
            'readable': os.access(file_path, os.R_OK),
            'writable': os.access(file_path, os.W_OK)
        }
        
        # Add PDF-specific metadata
        if file_extension == 'pdf':
            try:
                with open(file_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    metadata['pdf_metadata'] = {
                        'pages': len(pdf_reader.pages),
                        'title': pdf_reader.metadata.get('/Title', ''),
                        'author': pdf_reader.metadata.get('/Author', ''),
                        'subject': pdf_reader.metadata.get('/Subject', ''),
                        'creator': pdf_reader.metadata.get('/Creator', ''),
                        'producer': pdf_reader.metadata.get('/Producer', ''),
                        'creation_date': pdf_reader.metadata.get('/CreationDate', ''),
                        'modification_date': pdf_reader.metadata.get('/ModDate', '')
                    }
            except:
                metadata['pdf_metadata'] = {'error': 'Could not read PDF metadata'}
        
        return jsonify({'metadata': metadata}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get file metadata', 'details': str(e)}), 500

@bp.route('/<int:file_id>/validate', methods=['GET'])
@jwt_required()
def validate_file(file_id):
    """Validate file integrity"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement file lookup from database
        file_path = file_id
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found'}), 404
        
        # Basic validation
        file_size = os.path.getsize(file_path)
        
        validation_result = {
            'file_id': file_id,
            'exists': True,
            'size': file_size,
            'size_valid': file_size <= MAX_FILE_SIZE,
            'readable': os.access(file_path, os.R_OK),
            'extension_valid': file_path.lower().endswith('.pdf'),
            'corrupted': False
        }
        
        # Additional validation for PDF files
        if file_path.lower().endswith('.pdf'):
            try:
                with open(file_path, 'rb') as file:
                    PyPDF2.PdfReader(file)
                    validation_result['pdf_valid'] = True
                    validation_result['pages'] = len(file.pages)
            except:
                validation_result['corrupted'] = True
                validation_result['pdf_valid'] = False
        
        return jsonify({'validation': validation_result}), 200
        
    except Exception as e:
        return jsonify({'error': 'File validation failed', 'details': str(e)}), 500

@bp.route('/search', methods=['GET'])
@jwt_required()
def search_files():
    """Search files"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_user_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        query = request.args.get('q', '')
        file_type = request.args.get('type', '')
        
        if not query:
            return jsonify({'error': 'Search query is required'}), 400
        
        # TODO: Implement file search logic
        # This would search through the database for files matching the query
        
        return jsonify({
            'query': query,
            'file_type': file_type,
            'results': [],
            'total': 0
        }), 200
        
    except Exception as e:
        return jsonify({'error': 'Search failed', 'details': str(e)}), 500

@bp.route('/storage-usage', methods=['GET'])
@jwt_required()
def get_storage_usage():
    """Get storage usage statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_user_id(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # TODO: Implement storage usage calculation
        # This would calculate total storage used by the user
        
        usage = {
            'total_used': 0,
            'total_available': 100 * 1024 * 1024 * 1024,  # 100GB
            'used_percentage': 0,
            'by_type': {
                'projects': 0,
                'results': 0,
                'other': 0
            }
        }
        
        return jsonify({'usage': usage}), 200
        
    except Exception as e:
        return jsonify({'error': 'Failed to get storage usage', 'details': str(e)}), 500

@bp.route('/cleanup', methods=['POST'])
@jwt_required()
@limiter.limit("1 per hour")
def cleanup_files():
    """Clean up unused files"""
    try:
        current_user_id = get_jwt_identity()
        user = User.find_by_user_id(current_user_id)
        
        if not user or not user.is_admin():
            return jsonify({'error': 'Admin access required'}), 403
        
        # TODO: Implement file cleanup logic
        # This would remove orphaned files and temporary files
        
        return jsonify({'message': 'File cleanup completed'}), 200
        
    except Exception as e:
        return jsonify({'error': 'File cleanup failed', 'details': str(e)}), 500
