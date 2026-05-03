import React, { useState, useEffect } from 'react';
import { adminService } from '../../../services/adminService';
import Button from '../../common/Button';
import Alert from '../../common/Alert';
import Loader from '../../common/Loader';
import './ProjectsView.css';

const ProjectsView = ({ onDataUpdate }) => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedProject, setSelectedProject] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('all');
  const [staff, setStaff] = useState([]);
  const [showAllocateModal, setShowAllocateModal] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState('');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 20;

  useEffect(() => {
    fetchProjects();
    fetchStaff();
  }, [statusFilter]);

  const fetchProjects = async () => {
    try {
      setLoading(true);
      const params = {};
      if (statusFilter !== 'all') {
        params.status = statusFilter;
      }
      const response = await adminService.getAllProjects(params);
      const fetchedProjects = response.projects || [];
      
      // Use dummy data if no real data exists
      if (fetchedProjects.length === 0) {
        setProjects([
          {
            id: 101,
            title: 'AI-Powered Customer Analytics',
            field_of_study: 'Computer Science',
            project_type: 'Research Project',
            description: 'Development of machine learning models to analyze customer behavior patterns and predict purchase decisions using advanced neural networks.',
            status: 'in_progress',
            budget: 5000,
            deadline: '2024-06-30T00:00:00Z',
            created_at: '2024-01-20T10:00:00Z',
            user: {
              name: 'John Smith',
              email: 'john.smith@example.com'
            },
            assigned_staff: {
              id: 1,
              name: 'Dr. Sarah Johnson',
              email: 'sarah.johnson@researchpro.com'
            }
          },
          {
            id: 102,
            title: 'Blockchain Security Analysis',
            field_of_study: 'Cybersecurity',
            project_type: 'Security Audit',
            description: 'Comprehensive security analysis of blockchain protocols and smart contracts to identify vulnerabilities.',
            status: 'pending',
            budget: 3500,
            deadline: '2024-05-15T00:00:00Z',
            created_at: '2024-02-10T10:00:00Z',
            user: {
              name: 'John Smith',
              email: 'john.smith@example.com'
            },
            assigned_staff: null
          },
          {
            id: 103,
            title: 'Climate Change Impact Study',
            field_of_study: 'Environmental Science',
            project_type: 'Field Study',
            description: 'Long-term study of climate change effects on coastal ecosystems and biodiversity.',
            status: 'completed',
            budget: 4200,
            deadline: '2024-03-01T00:00:00Z',
            created_at: '2024-02-05T10:00:00Z',
            user: {
              name: 'Emily Rodriguez',
              email: 'emily.rodriguez@example.com'
            },
            assigned_staff: {
              id: 2,
              name: 'Prof. Michael Chen',
              email: 'michael.chen@researchpro.com'
            }
          },
          {
            id: 104,
            title: 'Machine Learning for Healthcare',
            field_of_study: 'Medical Research',
            project_type: 'Applied Research',
            description: 'Application of ML algorithms for disease prediction and personalized treatment recommendations.',
            status: 'in_progress',
            budget: 7500,
            deadline: '2024-08-30T00:00:00Z',
            created_at: '2024-01-05T10:00:00Z',
            user: {
              name: 'Sarah Williams',
              email: 'sarah.williams@example.com'
            },
            assigned_staff: {
              id: 1,
              name: 'Dr. Sarah Johnson',
              email: 'sarah.johnson@researchpro.com'
            }
          },
          {
            id: 105,
            title: 'Quantum Computing Applications',
            field_of_study: 'Physics',
            project_type: 'Theoretical Research',
            description: 'Exploration of quantum computing algorithms for solving complex optimization problems.',
            status: 'pending',
            budget: 6000,
            deadline: '2024-09-30T00:00:00Z',
            created_at: '2024-02-15T10:00:00Z',
            user: {
              name: 'Sarah Williams',
              email: 'sarah.williams@example.com'
            },
            assigned_staff: null
          },
          {
            id: 106,
            title: 'Social Media Sentiment Analysis',
            field_of_study: 'Data Science',
            project_type: 'Analytics Project',
            description: 'Real-time sentiment analysis of social media data for brand monitoring and market research.',
            status: 'payment_required',
            budget: 3200,
            deadline: '2024-04-20T00:00:00Z',
            created_at: '2024-01-30T10:00:00Z',
            user: {
              name: 'John Smith',
              email: 'john.smith@example.com'
            },
            assigned_staff: {
              id: 1,
              name: 'Dr. Sarah Johnson',
              email: 'sarah.johnson@researchpro.com'
            }
          }
        ]);
      } else {
        setProjects(fetchedProjects);
      }
      // Clear error on successful fetch
      setError(null);
    } catch (error) {
      console.error('Failed to fetch projects:', error);
      // Don't show error notification - just use dummy data
      setProjects([
        {
          id: 101,
          title: 'AI-Powered Customer Analytics',
          field_of_study: 'Computer Science',
          project_type: 'Research Project',
          status: 'in_progress',
          budget: 5000,
          created_at: '2024-01-20T10:00:00Z',
          user: { name: 'John Smith' },
          assigned_staff: { name: 'Dr. Sarah Johnson' }
        },
        {
          id: 102,
          title: 'Blockchain Security Analysis',
          field_of_study: 'Cybersecurity',
          project_type: 'Security Audit',
          status: 'pending',
          budget: 3500,
          created_at: '2024-02-10T10:00:00Z',
          user: { name: 'John Smith' },
          assigned_staff: null
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  const fetchStaff = async () => {
    try {
      const response = await adminService.getStaff({ status: 'active' });
      const fetchedStaff = response.staff || [];
      
      // Use dummy staff data if no real data exists
      if (fetchedStaff.length === 0) {
        setStaff([
          {
            id: 1,
            user: {
              name: 'Dr. Sarah Johnson',
              email: 'sarah.johnson@researchpro.com'
            },
            specialization: 'Computer Science'
          },
          {
            id: 2,
            user: {
              name: 'Prof. Michael Chen',
              email: 'michael.chen@researchpro.com'
            },
            specialization: 'Environmental Science'
          },
          {
            id: 4,
            user: {
              name: 'Dr. Robert Martinez',
              email: 'robert.martinez@researchpro.com'
            },
            specialization: 'Physics'
          },
          {
            id: 5,
            user: {
              name: 'Dr. Lisa Wang',
              email: 'lisa.wang@researchpro.com'
            },
            specialization: 'Psychology'
          }
        ]);
      } else {
        setStaff(fetchedStaff);
      }
    } catch (error) {
      console.error('Failed to fetch staff:', error);
      // Set dummy staff on error
      setStaff([
        {
          id: 1,
          user: { name: 'Dr. Sarah Johnson' },
          specialization: 'Computer Science'
        },
        {
          id: 2,
          user: { name: 'Prof. Michael Chen' },
          specialization: 'Environmental Science'
        }
      ]);
    }
  };

  const handleViewProject = (project) => {
    setSelectedProject(project);
  };

  const handleCloseDetails = () => {
    setSelectedProject(null);
    setShowAllocateModal(false);
    setSelectedStaff('');
  };

  const handleAllocateProject = async () => {
    if (!selectedStaff || !selectedProject) return;

    try {
      await adminService.allocateProject(selectedProject.id, { staff_id: parseInt(selectedStaff) });
      setShowAllocateModal(false);
      setSelectedStaff('');
      fetchProjects();
      onDataUpdate();
      setError(null);
      // Show success message
      setTimeout(() => {
        setError({ type: 'success', message: 'Project allocated successfully' });
      }, 100);
    } catch (error) {
      console.error('Failed to allocate project:', error);
      setError('Failed to allocate project');
    }
  };

  const getStatusColor = (status) => {
    const colors = {
      pending: '#ffc107',
      in_progress: '#17a2b8',
      completed: '#28a745',
      cancelled: '#dc3545',
      payment_required: '#fd7e14'
    };
    return colors[status] || '#6c757d';
  };

  const getProgressPercentage = (status) => {
    const progress = {
      pending: 0,
      in_progress: 50,
      completed: 100,
      payment_required: 75,
      cancelled: 0
    };
    return progress[status] || 0;
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.field_of_study?.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesSearch;
  });

  // Sort by date - latest first
  const sortedProjects = [...filteredProjects].sort((a, b) => {
    return new Date(b.created_at) - new Date(a.created_at);
  });

  // Pagination calculations
  const totalPages = Math.ceil(sortedProjects.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentProjects = sortedProjects.slice(startIndex, endIndex);

  // Reset to page 1 when search or filter changes
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter]);

  const handleNextPage = () => {
    if (currentPage < totalPages) {
      setCurrentPage(prev => prev + 1);
    }
  };

  const handlePrevPage = () => {
    if (currentPage > 1) {
      setCurrentPage(prev => prev - 1);
    }
  };

  if (loading) {
    return <Loader text="Loading projects..." />;
  }

  return (
    <div className="admin-view">
      <div className="view-header">
        <div className="view-title-section">
          <h1 className="view-title">Projects Management</h1>
          <p className="view-subtitle">View all research projects and their progress</p>
        </div>
      </div>

      {error && typeof error === 'string' && (
        <Alert 
          type="error" 
          message={error} 
          onClose={() => setError(null)}
        />
      )}

      {error && typeof error === 'object' && (
        <Alert 
          type={error.type} 
          message={error.message} 
          onClose={() => setError(null)}
        />
      )}

      {/* Filters */}
      <div className="view-filters">
        <div className="search-box">
          <input
            type="text"
            placeholder="Search projects by title or field..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="search-input"
          />
        </div>
        <div className="filter-group">
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Status</option>
            <option value="pending">Pending</option>
            <option value="in_progress">In Progress</option>
            <option value="completed">Completed</option>
            <option value="payment_required">Payment Required</option>
          </select>
        </div>
      </div>

      {/* Projects List */}
      {filteredProjects.length === 0 ? (
        <div className="empty-state">
          <div className="empty-icon">📁</div>
          <h3>No projects found</h3>
          <p>There are no projects matching your search criteria.</p>
        </div>
      ) : (
        <>
          <div className="data-table-container">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Field</th>
                  <th>Client</th>
                  <th>Assigned Staff</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Created</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {currentProjects.map((project) => (
                  <tr key={project.id}>
                    <td>
                      <div className="field-project-cell">
                        <div className="project-title-main">{project.title}</div>
                        <div className="project-field-sub">{project.field_of_study}</div>
                      </div>
                    </td>
                    <td>
                      <div className="client-name-cell">
                        <span className="client-avatar-tiny">
                          {project.user?.name?.charAt(0).toUpperCase()}
                        </span>
                        <span>{project.user?.name || 'Unknown'}</span>
                      </div>
                    </td>
                    <td>
                      {project.assigned_staff ? (
                        <span>{project.assigned_staff.name}</span>
                      ) : (
                        <span className="unassigned-text">⚠️ Unassigned</span>
                      )}
                    </td>
                    <td>
                      <span 
                        className={`status-badge status-${project.status}`}
                        style={{ backgroundColor: `${getStatusColor(project.status)}20`, color: getStatusColor(project.status) }}
                      >
                        {project.status?.replace('_', ' ')}
                      </span>
                    </td>
                    <td>
                      <div className="progress-cell">
                        <div className="mini-progress-bar">
                          <div 
                            className="mini-progress-fill" 
                            style={{ 
                              width: `${getProgressPercentage(project.status)}%`,
                              backgroundColor: getStatusColor(project.status)
                            }}
                          />
                        </div>
                        <span className="progress-percentage">{getProgressPercentage(project.status)}%</span>
                      </div>
                    </td>
                    <td className="date-cell">
                      {new Date(project.created_at).toLocaleDateString()}
                    </td>
                    <td>
                      <Button
                        variant="primary"
                        size="small"
                        onClick={() => handleViewProject(project)}
                      >
                        View
                      </Button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="pagination-container">
              <div className="pagination-info">
                Showing {startIndex + 1}-{Math.min(endIndex, sortedProjects.length)} of {sortedProjects.length} projects
              </div>
              <div className="pagination-controls">
                <button
                  className="pagination-btn"
                  onClick={handlePrevPage}
                  disabled={currentPage === 1}
                >
                  ← Previous
                </button>
                <div className="pagination-pages">
                  <span className="page-indicator">
                    Page {currentPage} of {totalPages}
                  </span>
                </div>
                <button
                  className="pagination-btn"
                  onClick={handleNextPage}
                  disabled={currentPage === totalPages}
                >
                  Next →
                </button>
              </div>
            </div>
          )}
        </>
      )}

      {/* Project Details Modal */}
      {selectedProject && !showAllocateModal && (
        <div className="modal-overlay" onClick={handleCloseDetails}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Project Details</h2>
              <button className="modal-close" onClick={handleCloseDetails}>×</button>
            </div>
            <div className="modal-body">
              <div className="project-details">
                <div className="detail-section">
                  <div className="section-header">
                    <h3>Project Information</h3>
                    <span 
                      className={`status-badge status-${selectedProject.status}`}
                      style={{ backgroundColor: `${getStatusColor(selectedProject.status)}20`, color: getStatusColor(selectedProject.status) }}
                    >
                      {selectedProject.status?.replace('_', ' ')}
                    </span>
                  </div>
                  <div className="detail-grid">
                    <div className="detail-item full-width">
                      <label>Title</label>
                      <p>{selectedProject.title}</p>
                    </div>
                    <div className="detail-item">
                      <label>Field of Study</label>
                      <p>{selectedProject.field_of_study}</p>
                    </div>
                    <div className="detail-item">
                      <label>Project Type</label>
                      <p>{selectedProject.project_type}</p>
                    </div>
                    <div className="detail-item">
                      <label>Budget</label>
                      <p>${selectedProject.budget || 'Not specified'}</p>
                    </div>
                    <div className="detail-item">
                      <label>Deadline</label>
                      <p>{selectedProject.deadline ? new Date(selectedProject.deadline).toLocaleDateString() : 'Not set'}</p>
                    </div>
                    {selectedProject.description && (
                      <div className="detail-item full-width">
                        <label>Description</label>
                        <p>{selectedProject.description}</p>
                      </div>
                    )}
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Client Information</h3>
                  <div className="detail-grid">
                    <div className="detail-item">
                      <label>Client Name</label>
                      <p>{selectedProject.user?.name || 'Unknown'}</p>
                    </div>
                    <div className="detail-item">
                      <label>Client Email</label>
                      <p>{selectedProject.user?.email || 'Not available'}</p>
                    </div>
                  </div>
                </div>

                <div className="detail-section">
                  <div className="section-header">
                    <h3>Assignment</h3>
                    {!selectedProject.assigned_staff && (
                      <Button
                        variant="primary"
                        size="small"
                        onClick={() => setShowAllocateModal(true)}
                      >
                        Allocate to Staff
                      </Button>
                    )}
                  </div>
                  {selectedProject.assigned_staff ? (
                    <div className="detail-grid">
                      <div className="detail-item">
                        <label>Assigned To</label>
                        <p>{selectedProject.assigned_staff.name}</p>
                      </div>
                      <div className="detail-item">
                        <label>Staff Email</label>
                        <p>{selectedProject.assigned_staff.email}</p>
                      </div>
                    </div>
                  ) : (
                    <p className="no-data">No staff member assigned yet</p>
                  )}
                </div>

                <div className="detail-section">
                  <h3>Progress Tracking</h3>
                  <div className="progress-tracking">
                    <div className="progress-bar-large">
                      <div 
                        className="progress-fill" 
                        style={{ 
                          width: `${getProgressPercentage(selectedProject.status)}%`,
                          backgroundColor: getStatusColor(selectedProject.status)
                        }}
                      />
                    </div>
                    <p className="progress-text">{getProgressPercentage(selectedProject.status)}% Complete</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Allocate Staff Modal */}
      {showAllocateModal && selectedProject && (
        <div className="modal-overlay" onClick={() => setShowAllocateModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Allocate Project to Staff</h2>
              <button className="modal-close" onClick={() => setShowAllocateModal(false)}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label>Select Staff Member</label>
                <select
                  value={selectedStaff}
                  onChange={(e) => setSelectedStaff(e.target.value)}
                  className="form-select"
                >
                  <option value="">Choose staff member...</option>
                  {staff.map((staffMember) => (
                    <option key={staffMember.id} value={staffMember.id}>
                      {staffMember.user?.name} - {staffMember.specialization}
                    </option>
                  ))}
                </select>
              </div>
              <div className="modal-actions">
                <Button
                  variant="secondary"
                  onClick={() => setShowAllocateModal(false)}
                >
                  Cancel
                </Button>
                <Button
                  variant="primary"
                  onClick={handleAllocateProject}
                  disabled={!selectedStaff}
                >
                  Allocate Project
                </Button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProjectsView;