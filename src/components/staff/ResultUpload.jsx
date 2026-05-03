import React, { useState } from 'react';
import { useFileUpload } from '../../hooks/useFileUpload';
import { staffService } from '../../services/staffService';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Modal from '../common/Modal';
import './ResultUpload.css';

const ResultUpload = ({ isOpen, onClose, projectId, onSuccess }) => {
  const [file, setFile] = useState(null);
  const [description, setDescription] = useState('');
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const { uploadFile, uploading, uploadProgress } = useFileUpload();

  const handleFileChange = (selectedFile) => {
    setFile(selectedFile);
    if (errors.file) {
      setErrors(prev => ({ ...prev, file: '' }));
    }
  };

  const handleDescriptionChange = (value) => {
    setDescription(value);
    if (errors.description) {
      setErrors(prev => ({ ...prev, description: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!file) {
      newErrors.file = 'Please select a PDF file';
    } else if (file.type !== 'application/pdf') {
      newErrors.file = 'Only PDF files are allowed';
    } else if (file.size > 20 * 1024 * 1024) {
      newErrors.file = 'File size must be less than 20MB';
    }
    
    if (!description.trim()) {
      newErrors.description = 'Please provide a description of the work completed';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    setAlert(null);
    
    try {
      const uploadedFile = await uploadFile(file, 'results');
      
      await staffService.uploadResult(projectId, {
        file_path: uploadedFile.file_path,
        original_filename: file.name,
        description: description.trim()
      });
      
      setAlert({ type: 'success', message: 'Result uploaded successfully!' });
      setTimeout(() => {
        onSuccess();
      }, 1000);
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Upload failed. Please try again.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading && !uploading) {
      setFile(null);
      setDescription('');
      setErrors({});
      setAlert(null);
      onClose();
    }
  };

  if (!isOpen) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      title="Upload Project Result"
      size="large"
    >
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}
      
      <form onSubmit={handleSubmit} className="result-upload-form">
        <div className="form-group">
          <label className="input-label">Result PDF File *</label>
          <input
            type="file"
            accept=".pdf"
            onChange={(e) => handleFileChange(e.target.files[0])}
            className={`file-input ${errors.file ? 'input-error' : ''}`}
            required
          />
          {errors.file && (
            <span className="input-error-message">{errors.file}</span>
          )}
          {file && (
            <div className="file-info">
              <span>Selected: {file.name}</span>
              <span>({(file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
          )}
        </div>
        
        <div className="form-group">
          <label className="input-label">Work Description *</label>
          <textarea
            value={description}
            onChange={(e) => handleDescriptionChange(e.target.value)}
            placeholder="Describe the work completed, methodology used, and key findings..."
            className={`textarea-field ${errors.description ? 'input-error' : ''}`}
            rows="6"
            required
          />
          {errors.description && (
            <span className="input-error-message">{errors.description}</span>
          )}
        </div>
        
        {uploading && (
          <div className="upload-progress">
            <div className="progress-bar">
              <div 
                className="progress-fill" 
                style={{ width: `${uploadProgress}%` }}
              ></div>
            </div>
            <span>Uploading... {uploadProgress}%</span>
          </div>
        )}
        
        <div className="upload-guidelines">
          <Alert 
            type="info" 
            message="Please ensure the uploaded PDF contains the complete research results, analysis, and conclusions." 
          />
        </div>
        
        <div className="form-actions">
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={loading || uploading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={loading || uploading}
            disabled={loading || uploading}
          >
            Upload Result
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default ResultUpload;
