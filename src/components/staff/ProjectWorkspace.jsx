import React, { useState } from 'react';
import { staffService } from '../../services/staffService';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Modal from '../common/Modal';
import ResultUpload from './ResultUpload';
import './ProjectWorkspace.css';

const ProjectWorkspace = ({ project, isOpen, onClose, onProjectUpdate }) => {
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);
  const [showResultUpload, setShowResultUpload] = useState(false);

  const handleStatusUpdate = async (newStatus) => {
    try {
      setLoading(true);
      await staffService.updateProjectStatus(project.id, newStatus);
      setAlert({ type: 'success', message: 'Project status updated successfully!' });
      setTimeout(() => {
        onProjectUpdate();
        onClose();
      }, 1000);
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to update project status.' 
      });
    } finally {
      setLoading(false);
    }
  };

  const handleResultUploadSuccess = () => {
    setShowResultUpload(false);
    setAlert({ type: 'success', message: 'Result uploaded successfully!' });
    setTimeout(() => {
      onProjectUpdate();
      onClose();
    }, 1000);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'in_progress':
        return 'status-in-progress';
      case 'completed':
        return 'status-completed';
      default:
        return 'status-unknown';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':
        return 'Pending';
      case 'in_progress':
        return 'In Progress';
      case 'completed':
        return 'Completed';
      default:
        return 'Unknown';
    }
  };

  if (!isOpen) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose}
      title="Project Workspace"
      size="large"
    >
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
        />
      )}

      <div className="workspace-content">
        <div className="workspace-header-info">
          <div className="project-title-section">
            <h2>{project.title}</h2>
            <span className={`project-status ${getStatusColor(project.status)}`}>
              {getStatusText(project.status)}
            </span>
          </div>
          
          <div className="project-meta">
            <div className="meta-item">
              <label>Client:</label>
              <span>{project.user.name} ({project.user.email})</span>
            </div>
            <div className="meta-item">
              <label>Research Field:</label>
              <span>{project.research_field}</span>
            </div>
            <div className="meta-item">
              <label>Assigned Date:</label>
              <span>{formatDateString(project.assigned_at)}</span>
            </div>
            <div className="meta-item">
              <label>Original File:</label>
              <span>{project.original_filename}</span>
            </div>
          </div>
        </div>

        {project.description && (
          <div className="project-description-section">
            <h3>Project Description</h3>
            <div className="description-grid">
              <div className="description-item">
                <h4>Objectives</h4>
                <p>{project.description.objectives}</p>
              </div>
              
              <div className="description-item">
                <h4>Methodology</h4>
                <p>{project.description.methodology}</p>
              </div>
              
              <div className="description-item">
                <h4>Expected Outcomes</h4>
                <p>{project.description.expected_outcomes}</p>
              </div>
              
              <div className="description-item">
                <h4>Timeline</h4>
                <p>{project.description.timeline}</p>
              </div>
              
              {project.description.budget && (
                <div className="description-item">
                  <h4>Budget</h4>
                  <p>{project.description.budget}</p>
                </div>
              )}
              
              {project.description.resources && (
                <div className="description-item">
                  <h4>Resources Needed</h4>
                  <p>{project.description.resources}</p>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="workspace-actions">
          {project.status === 'pending' && (
            <Button
              variant="primary"
              onClick={() => handleStatusUpdate('in_progress')}
              loading={loading}
              disabled={loading}
            >
              Start Working on Project
            </Button>
          )}
          
          {project.status === 'in_progress' && (
            <Button
              variant="success"
              onClick={() => setShowResultUpload(true)}
            >
              Upload Completed Result
            </Button>
          )}
          
          {project.status === 'completed' && (
            <div className="completed-notice">
              <Alert 
                type="success" 
                message="This project has been completed and the result has been uploaded." 
              />
            </div>
          )}
        </div>
      </div>

      {showResultUpload && (
        <ResultUpload
          isOpen={showResultUpload}
          onClose={() => setShowResultUpload(false)}
          projectId={project.id}
          onSuccess={handleResultUploadSuccess}
        />
      )}
    </Modal>
  );
};

export default ProjectWorkspace;
