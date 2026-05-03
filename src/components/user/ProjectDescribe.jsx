import React, { useState } from 'react';
import { projectService } from '../../services/projectService';
import Input from '../common/Input';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Modal from '../common/Modal';
import './ProjectDescribe.css';

const ProjectDescribe = ({ isOpen, onClose, projectId, onSuccess }) => {
  const [formData, setFormData] = useState({
    objectives: '',
    methodology: '',
    expectedOutcomes: '',
    timeline: '',
    budget: '',
    resources: ''
  });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.objectives) {
      newErrors.objectives = 'Project objectives are required';
    }
    
    if (!formData.methodology) {
      newErrors.methodology = 'Methodology is required';
    }
    
    if (!formData.expectedOutcomes) {
      newErrors.expectedOutcomes = 'Expected outcomes are required';
    }
    
    if (!formData.timeline) {
      newErrors.timeline = 'Timeline is required';
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
      await projectService.describeProject(projectId, formData);
      setAlert({ type: 'success', message: 'Project description saved successfully!' });
      setTimeout(() => {
        onSuccess();
      }, 1000);
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to save project description.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    if (!loading) {
      setFormData({
        objectives: '',
        methodology: '',
        expectedOutcomes: '',
        timeline: '',
        budget: '',
        resources: ''
      });
      setErrors({});
      setAlert(null);
      onClose();
    }
  };

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={handleClose}
      title="Describe Your Project"
      size="large"
    >
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}
      
      <form onSubmit={handleSubmit} className="project-describe-form">
        <div className="form-group">
          <label className="input-label">Project Objectives *</label>
          <textarea
            name="objectives"
            value={formData.objectives}
            onChange={(e) => handleChange('objectives', e.target.value)}
            placeholder="Describe the main objectives of your project..."
            className={`textarea-field ${errors.objectives ? 'input-error' : ''}`}
            rows="4"
            required
          />
          {errors.objectives && (
            <span className="input-error-message">{errors.objectives}</span>
          )}
        </div>
        
        <div className="form-group">
          <label className="input-label">Methodology *</label>
          <textarea
            name="methodology"
            value={formData.methodology}
            onChange={(e) => handleChange('methodology', e.target.value)}
            placeholder="Describe the research methodology you plan to use..."
            className={`textarea-field ${errors.methodology ? 'input-error' : ''}`}
            rows="4"
            required
          />
          {errors.methodology && (
            <span className="input-error-message">{errors.methodology}</span>
          )}
        </div>
        
        <div className="form-group">
          <label className="input-label">Expected Outcomes *</label>
          <textarea
            name="expectedOutcomes"
            value={formData.expectedOutcomes}
            onChange={(e) => handleChange('expectedOutcomes', e.target.value)}
            placeholder="What do you expect to achieve with this project?"
            className={`textarea-field ${errors.expectedOutcomes ? 'input-error' : ''}`}
            rows="4"
            required
          />
          {errors.expectedOutcomes && (
            <span className="input-error-message">{errors.expectedOutcomes}</span>
          )}
        </div>
        
        <div className="form-group">
          <label className="input-label">Timeline *</label>
          <input
            type="text"
            name="timeline"
            value={formData.timeline}
            onChange={(e) => handleChange('timeline', e.target.value)}
            placeholder="e.g., 3 months, 6 weeks, etc."
            className={`input-field ${errors.timeline ? 'input-error' : ''}`}
            required
          />
          {errors.timeline && (
            <span className="input-error-message">{errors.timeline}</span>
          )}
        </div>
        
        <div className="form-group">
          <label className="input-label">Budget (Optional)</label>
          <input
            type="text"
            name="budget"
            value={formData.budget}
            onChange={(e) => handleChange('budget', e.target.value)}
            placeholder="e.g., $5000, £3000, etc."
            className="input-field"
          />
        </div>
        
        <div className="form-group">
          <label className="input-label">Resources Needed (Optional)</label>
          <textarea
            name="resources"
            value={formData.resources}
            onChange={(e) => handleChange('resources', e.target.value)}
            placeholder="Describe any specific resources, equipment, or support needed..."
            className="textarea-field"
            rows="3"
          />
        </div>
        
        <div className="form-actions">
          <Button
            type="button"
            variant="secondary"
            onClick={handleClose}
            disabled={loading}
          >
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            loading={loading}
            disabled={loading}
          >
            Save Description
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default ProjectDescribe;
