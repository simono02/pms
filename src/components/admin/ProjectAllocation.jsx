import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import Input from '../common/Input';
import Modal from '../common/Modal';
import './ProjectAllocation.css';

const ProjectAllocation = ({ onDataUpdate }) => {
  const [projects, setProjects] = useState([]);
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('unassigned');
  const [showAllocationModal, setShowAllocationModal] = useState(false);
  const [selectedProject, setSelectedProject] = useState(null);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [projectsData, staffData] = await Promise.all([
        adminService.getUnassignedProjects(),
        adminService.getAllStaff()
      ]);
      setProjects(projectsData);
      setStaff(staffData.filter(s => s.status === 'active'));
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
  };

  const handleFilterChange = (value) => {
    setFilterStatus(value);
    if (value === 'all') {
      fetchAllProjects();
    } else {
      fetchData();
    }
  };

  const fetchAllProjects = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAllProjects();
      setProjects(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleAllocateProject = (project) => {
    setSelectedProject(project);
    setShowAllocationModal(true);
  };

  const handleReallocateProject = (project) => {
    setSelectedProject(project);
    setShowAllocationModal(true);
  };

  const handleAllocationSuccess = () => {
    setShowAllocationModal(false);
    setSelectedProject(null);
    setAlert({ type: 'success', message: 'Project allocated successfully!' });
    fetchData();
  };

  const handleUnallocateProject = async (projectId) => {
    if (!window.confirm('Are you sure you want to unallocate this project?')) {
      return;
    }

    try {
      await adminService.unallocateProject(projectId);
      setAlert({ type: 'success', message: 'Project unallocated successfully!' });
      fetchData();
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to unallocate project.' 
      });
    }
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

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.user.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || 
                         (filterStatus === 'unassigned' && !project.assigned_staff) ||
                         (filterStatus === 'assigned' && project.assigned_staff);
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return <Loader text="Loading projects..." />;
  }

  if (error) {
    return (
      <div className="project-allocation-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchData} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="project-allocation">
      <div className="allocation-header">
        <h2>Project Allocation</h2>
        <div className="allocation-stats">
          <span>Total: {projects.length}</span>
          <span>Unassigned: {projects.filter(p => !p.assigned_staff).length}</span>
          <span>Assigned: {projects.filter(p => p.assigned_staff).length}</span>
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

      <div className="allocation-filters">
        <Input
          type="text"
          placeholder="Search by project title or client name..."
          value={searchTerm}
          onChange={handleSearch}
          className="search-input"
        />
        
        <select
          value={filterStatus}
          onChange={(e) => handleFilterChange(e.target.value)}
          className="filter-select"
        >
          <option value="unassigned">Unassigned</option>
          <option value="assigned">Assigned</option>
          <option value="all">All Projects</option>
        </select>
      </div>

      <div className="allocation-table-container">
        <table className="allocation-table">
          <thead>
            <tr>
              <th>Project Title</th>
              <th>Client</th>
              <th>Research Field</th>
              <th>Assigned Staff</th>
              <th>Status</th>
              <th>Created Date</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredProjects.map((project) => (
              <tr key={project.id}>
                <td className="project-title">{project.title}</td>
                <td className="client-name">{project.user.name}</td>
                <td className="research-field">{project.research_field}</td>
                <td className="assigned-staff">
                  {project.assigned_staff ? (
                    <div className="staff-info">
                      <span>{project.assigned_staff.name}</span>
                      <small>({project.assigned_staff.specialization})</small>
                    </div>
                  ) : (
                    <span className="unassigned">Unassigned</span>
                  )}
                </td>
                <td className="project-status">
                  <span className={`status-badge ${getStatusColor(project.status)}`}>
                    {getStatusText(project.status)}
                  </span>
                </td>
                <td className="created-date">{formatDateString(project.created_at)}</td>
                <td className="project-actions">
                  {!project.assigned_staff ? (
                    <Button
                      variant="primary"
                      size="small"
                      onClick={() => handleAllocateProject(project)}
                    >
                      Allocate
                    </Button>
                  ) : (
                    <>
                      <Button
                        variant="secondary"
                        size="small"
                        onClick={() => handleReallocateProject(project)}
                      >
                        Reallocate
                      </Button>
                      <Button
                        variant="danger"
                        size="small"
                        onClick={() => handleUnallocateProject(project.id)}
                      >
                        Unallocate
                      </Button>
                    </>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredProjects.length === 0 && (
        <div className="no-projects">
          <p>No projects found matching your criteria.</p>
        </div>
      )}

      {showAllocationModal && selectedProject && (
        <AllocationModal
          isOpen={showAllocationModal}
          onClose={() => {
            setShowAllocationModal(false);
            setSelectedProject(null);
          }}
          project={selectedProject}
          staff={staff}
          onSuccess={handleAllocationSuccess}
        />
      )}
    </div>
  );
};

const AllocationModal = ({ isOpen, onClose, project, staff, onSuccess }) => {
  const [selectedStaffId, setSelectedStaffId] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (project.assigned_staff) {
      setSelectedStaffId(project.assigned_staff.id.toString());
    }
  }, [project]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!selectedStaffId) {
      setError('Please select a staff member');
      return;
    }

    setLoading(true);
    setError(null);
    
    try {
      await adminService.allocateProject(project.id, selectedStaffId);
      onSuccess();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose}
      title={project.assigned_staff ? 'Reallocate Project' : 'Allocate Project'}
      size="medium"
    >
      {error && <Alert type="error" message={error} />}
      
      <div className="allocation-modal-content">
        <div className="project-summary">
          <h3>Project Details</h3>
          <p><strong>Title:</strong> {project.title}</p>
          <p><strong>Client:</strong> {project.user.name}</p>
          <p><strong>Research Field:</strong> {project.research_field}</p>
          {project.assigned_staff && (
            <p><strong>Currently Assigned:</strong> {project.assigned_staff.name}</p>
          )}
        </div>

        <form onSubmit={handleSubmit} className="allocation-form">
          <div className="form-group">
            <label className="input-label">Select Staff Member *</label>
            <select
              value={selectedStaffId}
              onChange={(e) => setSelectedStaffId(e.target.value)}
              className="input-field"
              required
            >
              <option value="">Choose a staff member...</option>
              {staff.map((member) => (
                <option key={member.id} value={member.id}>
                  {member.name} - {member.specialization || 'General'} 
                  ({member.assigned_projects || 0} projects)
                </option>
              ))}
            </select>
          </div>

          <div className="form-actions">
            <Button
              type="button"
              variant="secondary"
              onClick={onClose}
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
              {project.assigned_staff ? 'Reallocate Project' : 'Allocate Project'}
            </Button>
          </div>
        </form>
      </div>
    </Modal>
  );
};

export default ProjectAllocation;
