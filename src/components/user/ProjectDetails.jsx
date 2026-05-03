import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { projectService } from '../../services/projectService';
import { formatDateString, has24HoursPassed } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import ProjectDescribe from './ProjectDescribe';
import './ProjectDetails.css';

const ProjectDetails = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [project, setProject] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);
  const [showDescribe, setShowDescribe] = useState(false);

  useEffect(() => {
    fetchProject();
  }, [id]);

  const fetchProject = async () => {
    try {
      setLoading(true);
      const data = await projectService.getProject(id);
      setProject(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDescribeSuccess = () => {
    setShowDescribe(false);
    setAlert({ type: 'success', message: 'Project description updated!' });
    fetchProject();
  };

  const canEdit = () => {
    if (!project) return false;
    return !has24HoursPassed(project.created_at) && project.status === 'pending';
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':
        return 'status-pending';
      case 'in_progress':
        return 'status-in-progress';
      case 'completed':
        return 'status-completed';
      case 'payment_required':
        return 'status-payment-required';
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
      case 'payment_required':
        return 'Payment Required';
      default:
        return 'Unknown';
    }
  };

  if (loading) {
    return <Loader text="Loading project details..." />;
  }

  if (error) {
    return (
      <div className="project-details-error">
        <Alert type="error" message={error} />
        <Button onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  if (!project) {
    return (
      <div className="project-details-error">
        <Alert type="error" message="Project not found" />
        <Button onClick={() => navigate('/dashboard')}>
          Back to Dashboard
        </Button>
      </div>
    );
  }

  return (
    <div className="project-details">
      <div className="project-details-header">
        <Button 
          variant="secondary" 
          onClick={() => navigate('/dashboard')}
        >
          ← Back to Dashboard
        </Button>
        
        <div className="project-actions">
          {canEdit() && (
            <Button 
              variant="primary"
              onClick={() => setShowDescribe(true)}
            >
              Edit Description
            </Button>
          )}
          
          {project.status === 'payment_required' && (
            <Button 
              variant="success"
              onClick={() => navigate(`/payment/${project.id}`)}
            >
              Make Payment
            </Button>
          )}
        </div>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
          autoClose
        />
      )}

      <div className="project-details-content">
        <div className="project-info-card">
          <div className="project-info-header">
            <h1>{project.title}</h1>
            <span className={`project-status ${getStatusColor(project.status)}`}>
              {getStatusText(project.status)}
            </span>
          </div>
          
          <div className="project-info-grid">
            <div className="info-item">
              <label>Research Field</label>
              <span>{project.research_field}</span>
            </div>
            
            <div className="info-item">
              <label>Created Date</label>
              <span>{formatDateString(project.created_at)}</span>
            </div>
            
            {project.assigned_staff && (
              <div className="info-item">
                <label>Assigned Staff</label>
                <span>{project.assigned_staff.name}</span>
              </div>
            )}
            
            <div className="info-item">
              <label>Original Filename</label>
              <span>{project.original_filename}</span>
            </div>
          </div>
        </div>

        {project.description && (
          <div className="project-description-card">
            <h2>Project Description</h2>
            
            <div className="description-section">
              <h3>Objectives</h3>
              <p>{project.description.objectives}</p>
            </div>
            
            <div className="description-section">
              <h3>Methodology</h3>
              <p>{project.description.methodology}</p>
            </div>
            
            <div className="description-section">
              <h3>Expected Outcomes</h3>
              <p>{project.description.expected_outcomes}</p>
            </div>
            
            <div className="description-section">
              <h3>Timeline</h3>
              <p>{project.description.timeline}</p>
            </div>
            
            {project.description.budget && (
              <div className="description-section">
                <h3>Budget</h3>
                <p>{project.description.budget}</p>
              </div>
            )}
            
            {project.description.resources && (
              <div className="description-section">
                <h3>Resources Needed</h3>
                <p>{project.description.resources}</p>
              </div>
            )}
          </div>
        )}

        {canEdit() && (
          <div className="edit-reminder">
            <Alert 
              type="info" 
              message="You can edit this project description within 24 hours of creation." 
            />
          </div>
        )}
      </div>

      {showDescribe && (
        <ProjectDescribe
          isOpen={showDescribe}
          onClose={() => setShowDescribe(false)}
          projectId={project.id}
          onSuccess={handleDescribeSuccess}
        />
      )}
    </div>
  );
};

export default ProjectDetails;
