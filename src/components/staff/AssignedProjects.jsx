import React, { useState, useEffect } from 'react';
import { staffService } from '../../services/staffService';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import './AssignedProjects.css';

const AssignedProjects = ({ onProjectUpdate }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [showWorkspace, setShowWorkspace] = useState(false);

  useEffect(() => {
    fetchProjects();
  }, []);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const data = await staffService.getAssignedProjects();
      // Safely extract the array regardless of API response shape
      const list = Array.isArray(data)
        ? data
        : Array.isArray(data?.projects)
        ? data.projects
        : Array.isArray(data?.data)
        ? data.data
        : [];
      setProjects(list);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleProjectClick = (project) => {
    setSelectedProject(project);
    setShowWorkspace(true);
  };

  const handleWorkspaceClose = () => {
    setShowWorkspace(false);
    setSelectedProject(null);
    onProjectUpdate?.();
    fetchProjects();
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'pending':      return 'status-pending';
      case 'in_progress':  return 'status-in-progress';
      case 'completed':    return 'status-completed';
      default:             return 'status-unknown';
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 'pending':      return 'Pending';
      case 'in_progress':  return 'In Progress';
      case 'completed':    return 'Completed';
      default:             return 'Unknown';
    }
  };

  if (loading) return <Loader text="Loading assigned projects..." />;

  if (error) {
    return (
      <div className="assigned-projects-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchProjects} variant="primary">Retry</Button>
      </div>
    );
  }

  if (projects.length === 0) {
    return (
      <div className="ap-empty">
        <div className="ap-empty-icon">📋</div>
        <h3>No projects assigned yet</h3>
        <p>You don't have any projects assigned to you. Check back soon.</p>
      </div>
    );
  }

  return (
    <div className="assigned-projects">
      <div className="projects-grid">
        {projects.map((project) => (
          <div key={project.id} className="project-card">
            <div className="project-header">
              <h3 className="project-title">{project.title}</h3>
              <span className={`project-status ${getStatusColor(project.status)}`}>
                {getStatusText(project.status)}
              </span>
            </div>

            <div className="project-details">
              <p className="project-client">
                <strong>Client:</strong> {project.user?.name ?? '—'}
              </p>
              <p className="project-field">
                <strong>Research Field:</strong> {project.research_field ?? '—'}
              </p>
              <p className="project-date">
                <strong>Assigned:</strong> {formatDateString(project.assigned_at)}
              </p>
              {project.description?.objectives && (
                <p className="project-objectives">
                  <strong>Objectives:</strong>{' '}
                  {project.description.objectives.substring(0, 100)}…
                </p>
              )}
            </div>

            <div className="project-actions">
              <Button variant="primary" onClick={() => handleProjectClick(project)}>
                {project.status === 'pending' ? 'Start Work' : 'Continue Work'}
              </Button>
              {project.status === 'completed' && (
                <Button variant="secondary" onClick={() => handleProjectClick(project)}>
                  View Details
                </Button>
              )}
            </div>
          </div>
        ))}
      </div>

      {showWorkspace && selectedProject && (
        <ProjectWorkspace
          project={selectedProject}
          isOpen={showWorkspace}
          onClose={handleWorkspaceClose}
        />
      )}
    </div>
  );
};

/* ─── Project Workspace Modal ─────────────────────────────────────────── */

const ProjectWorkspace = ({ project, isOpen, onClose }) => {
  const [loading, setLoading] = useState(false);
  const [alert, setAlert]     = useState(null);

  const handleStatusUpdate = async (newStatus) => {
    try {
      setLoading(true);
      await staffService.updateProjectStatus(project.id, newStatus);
      setAlert({ type: 'success', message: 'Project status updated!' });
      setTimeout(onClose, 1000);
    } catch (error) {
      setAlert({ type: 'error', message: error.message || 'Failed to update status.' });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="project-workspace-overlay">
      <div className="project-workspace">
        <div className="workspace-header">
          <h2>Project Workspace</h2>
          <Button variant="secondary" onClick={onClose}>Close</Button>
        </div>

        {alert && (
          <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />
        )}

        <div className="workspace-content">
          <div className="project-info">
            <h3>{project.title}</h3>
            <p><strong>Client:</strong> {project.user?.name} ({project.user?.email})</p>
            <p><strong>Research Field:</strong> {project.research_field}</p>
            <p><strong>Status:</strong> {project.status}</p>
          </div>

          {project.description && (
            <div className="project-description">
              <h4>Project Description</h4>
              {[
                ['Objectives',        project.description.objectives],
                ['Methodology',       project.description.methodology],
                ['Expected Outcomes', project.description.expected_outcomes],
                ['Timeline',          project.description.timeline],
                ['Budget',            project.description.budget],
                ['Resources',         project.description.resources],
              ].map(([label, value]) =>
                value ? (
                  <div className="description-section" key={label}>
                    <strong>{label}:</strong>
                    <p>{value}</p>
                  </div>
                ) : null
              )}
            </div>
          )}

          <div className="workspace-actions">
            {project.status === 'pending' && (
              <Button
                variant="primary"
                onClick={() => handleStatusUpdate('in_progress')}
                loading={loading}
              >
                Start Working
              </Button>
            )}
            {project.status === 'in_progress' && (
              <ResultUpload
                projectId={project.id}
                onSuccess={() => {
                  setAlert({ type: 'success', message: 'Result uploaded!' });
                  setTimeout(onClose, 1000);
                }}
              />
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

/* ─── Result Upload ───────────────────────────────────────────────────── */

const ResultUpload = ({ projectId, onSuccess }) => {
  const [file,    setFile]    = useState(null);
  const [loading, setLoading] = useState(false);
  const [error,   setError]   = useState(null);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
    setError(null);
  };

  const handleUpload = async () => {
    if (!file)                          return setError('Please select a file');
    if (file.type !== 'application/pdf') return setError('Only PDF files are allowed');
    try {
      setLoading(true);
      await staffService.uploadResult(projectId, file);
      onSuccess();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="result-upload">
      <h4>Upload Result</h4>
      <input type="file" accept=".pdf" onChange={handleFileChange} className="file-input" />
      {error && <Alert type="error" message={error} />}
      {file && (
        <div className="file-info">
          <p>Selected: {file.name}</p>
          <Button variant="primary" onClick={handleUpload} loading={loading}>
            Upload Result
          </Button>
        </div>
      )}
    </div>
  );
};

export default AssignedProjects;