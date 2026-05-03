import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import './ProjectList.css';

const ProjectList = ({ projects, onProjectUpdate }) => {
  const [alert, setAlert] = useState(null);

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

  const canEdit = (project) => {
    const createdAt = new Date(project.created_at);
    const now = new Date();
    const hoursDiff = (now - createdAt) / (1000 * 60 * 60);
    return hoursDiff < 24 && project.status === 'pending';
  };

  if (!projects || projects.length === 0) {
    return (
      <div className="project-list-empty">
        <h3>No projects yet</h3>
        <p>Upload your first project to get started!</p>
      </div>
    );
  }

  return (
    <div className="project-list">
      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
          autoClose
        />
      )}
      
      <div className="project-grid">
        {projects.map((project) => (
          <div key={project.id} className="project-card">
            <div className="project-header">
              <h3 className="project-title">{project.title}</h3>
              <span className={`project-status ${getStatusColor(project.status)}`}>
                {getStatusText(project.status)}
              </span>
            </div>
            
            <div className="project-details">
              <p className="project-field">
                <strong>Research Field:</strong> {project.research_field}
              </p>
              <p className="project-date">
                <strong>Created:</strong> {formatDateString(project.created_at)}
              </p>
              {project.assigned_staff && (
                <p className="project-staff">
                  <strong>Assigned to:</strong> {project.assigned_staff.name}
                </p>
              )}
            </div>
            
            <div className="project-actions">
              <Link to={`/project/${project.id}`}>
                <Button variant="primary" size="small">
                  View Details
                </Button>
              </Link>
              
              {project.status === 'payment_required' && (
                <Link to={`/payment/${project.id}`}>
                  <Button variant="success" size="small">
                    Make Payment
                  </Button>
                </Link>
              )}
              
              {canEdit(project) && (
                <Button 
                  variant="secondary" 
                  size="small"
                  onClick={() => {
                    setAlert({ 
                      type: 'info', 
                      message: 'Edit functionality would open edit modal' 
                    });
                  }}
                >
                  Edit
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ProjectList;
