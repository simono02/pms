import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { projectService } from '../../services/projectService';
import { has24HoursPassed } from '../../utils/dateUtils';
import Input from '../common/Input';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import './ProjectEdit.css';

const ProjectEdit = ({ projectId, onSuccess, onCancel }) => {
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [formData, setFormData] = useState({
    title: '',
    researchField: ''
  });
  const [errors, setErrors] = useState({});
  const [alert, setAlert] = useState(null);
  const [loading, setLoading] = useState(false);
  const [fetchLoading, setFetchLoading] = useState(true);

  useEffect(() => {
    fetchProject();
  }, [projectId]);

  const fetchProject = async () => {
    try {
      setFetchLoading(true);
      const data = await projectService.getProject(projectId);
      
      if (has24HoursPassed(data.created_at)) {
        setAlert({ 
          type: 'error', 
          message: 'This project cannot be edited as 24 hours have passed since creation.' 
        });
        return;
      }
      
      if (data.status !== 'pending') {
        setAlert({ 
          type: 'error', 
          message: 'This project cannot be edited as it is no longer in pending status.' 
        });
        return;
      }
      
      setProject(data);
      setFormData({
        title: data.title,
        researchField: data.research_field
      });
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to load project details.' 
      });
    } finally {
      setFetchLoading(false);
    }
  };

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
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
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    setAlert(null);
    
    try {
      await projectService.updateProject(projectId, {
        title: formData.title,
        research_field: formData.researchField
      });
      
      setAlert({ type: 'success', message: 'Project updated successfully!' });
      setTimeout(() => {
        onSuccess();
      }, 1000);
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to update project.' 
      });
    } finally {
      setLoading(false);
    }
  };

  if (fetchLoading) {
    return <Loader text="Loading project..." />;
  }

  if (!project) {
    return (
      <div className="project-edit-error">
        <Alert type="error" message="Project not found or cannot be edited." />
        <Button onClick={onCancel}>
          Back to Project
        </Button>
      </div>
    );
  }

  return (
    <div className="project-edit">
      <div className="project-edit-header">
        <h2>Edit Project</h2>
        <Button variant="secondary" onClick={onCancel}>
          Cancel
        </Button>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}

      <div className="edit-reminder">
        <Alert 
          type="info" 
          message="You can only edit project title and research field within 24 hours of creation." 
        />
      </div>

      <form onSubmit={handleSubmit} className="project-edit-form">
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
        
        <div className="form-actions">
          <Button
            type="button"
            variant="secondary"
            onClick={onCancel}
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
            Update Project
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ProjectEdit;
