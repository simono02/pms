import React, { useState } from 'react';
import { useFileUpload } from '../../hooks/useFileUpload';
import { projectService } from '../../services/projectService';
import Input from '../common/Input';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Modal from '../common/Modal';
import './ProjectUpload.css';

const ProjectUpload = ({ isOpen, onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    title: '',
    researchField: '',
    file: null
  });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  
  const { uploadFile, uploading, uploadProgress } = useFileUpload();

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const handleFileChange = (file) => {
    setFormData(prev => ({ ...prev, file }));
    if (errors.file) {
      setErrors(prev => ({ ...prev, file: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title) {
      newErrors.title = 'Project title is required';
    }
    
    if (!formData.researchField) {
      newErrors.researchField = 'Research field is required';
    }
    
    if (!formData.file) {
      newErrors.file = 'Please select a PDF file';
    } else if (formData.file.type !== 'application/pdf') {
      newErrors.file = 'Only PDF files are allowed';
    } else if (formData.file.size > 10 * 1024 * 1024) {
      newErrors.file = 'File size must be less than 10MB';
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
      const uploadedFile = await uploadFile(formData.file, 'projects');
      
      await projectService.createProject({
        title: formData.title,
        research_field: formData.researchField,
        file_path: uploadedFile.file_path,
        original_filename: formData.file.name
      });
      
      setAlert({ type: 'success', message: 'Project uploaded successfully!' });
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
      setFormData({ title: '', researchField: '', file: null });
      setErrors({});
      setAlert(null);
      onClose();
    }
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      title="Upload New Project"
      size="large"
    >
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}
      
      <form onSubmit={handleSubmit} className="project-upload-form">
        <Input
          label="Project Title"
          type="text"
          name="title"
          value={formData.title}
          onChange={(value) => handleChange('title', value)}
          placeholder="Enter project title"
          error={errors.title}
          required
        />
        
        <div className="form-group">
          <label className="input-label">Research Field</label>
          <select
            name="researchField"
            value={formData.researchField}
            onChange={(e) => handleChange('researchField', e.target.value)}
            className={`input-field ${errors.researchField ? 'input-error' : ''}`}
            required
          >
            <option value="">Select research field</option>
            <option value="computer-science">Computer Science</option>
            <option value="engineering">Engineering</option>
            <option value="medicine">Medicine</option>
            <option value="business">Business</option>
            <option value="education">Education</option>
            <option value="social-sciences">Social Sciences</option>
            <option value="natural-sciences">Natural Sciences</option>
            <option value="other">Other</option>
          </select>
          {errors.researchField && (
            <span className="input-error-message">{errors.researchField}</span>
          )}
        </div>
        
        <div className="form-group">
          <label className="input-label">PDF File</label>
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
          {formData.file && (
            <div className="file-info">
              <span>Selected: {formData.file.name}</span>
              <span>({(formData.file.size / 1024 / 1024).toFixed(2)} MB)</span>
            </div>
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
            Upload Project
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default ProjectUpload;
