import React, { useState, useEffect } from 'react';
import { adminService } from '../../../services/adminService';
import Button from '../../common/Button';
import Alert from '../../common/Alert';
import Loader from '../../common/Loader';
import './StaffView.css';

const EMPTY_FORM = {
  name: '',
  email: '',
  id_number: '',
  phone: '',
  specialization: '',
  experience_years: 0,
  qualification: '',
  bio: '',
  rate_per_page: '',
  rate_per_chapter: '',
  skills: '',
};

/* ── Inline alert banner used for page-level messages ── */
const PageAlert = ({ alert, onClose }) => {
  if (!alert) return null;
  const isSuccess = alert.type === 'success';
  return (
    <div className={`sv-alert sv-alert--${alert.type}`} role="alert">
      <span className="sv-alert__icon">{isSuccess ? '✓' : '!'}</span>
      <span className="sv-alert__message">{alert.message}</span>
      <button className="sv-alert__close" onClick={onClose} aria-label="Dismiss">×</button>
    </div>
  );
};

const StaffView = ({ onDataUpdate }) => {
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [alert, setAlert] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [selectedStaff, setSelectedStaff] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [formData, setFormData] = useState(EMPTY_FORM);

  useEffect(() => {
    fetchStaff();
  }, []);

  /* Auto-dismiss success alerts after 5 s */
  useEffect(() => {
    if (alert?.type === 'success') {
      const t = setTimeout(() => setAlert(null), 5000);
      return () => clearTimeout(t);
    }
  }, [alert]);

  const fetchStaff = async () => {
    try {
      setLoading(true);
      const response = await adminService.getAllStaff();
      const fetchedStaff = response.staff || [];

      if (fetchedStaff.length === 0) {
        setStaff([
          {
            id: 1,
            user: { name: 'Dr. Sarah Johnson', email: 'sarah.johnson@researchpro.com', phone: '+254 700 111 222' },
            id_number: 'STF001',
            specialization: 'Computer Science',
            experience_years: 12,
            qualification: 'PhD in Computer Science',
            bio: 'Specialized in AI, Machine Learning, and Data Science.',
            rate_per_page: 5.00,
            rate_per_chapter: 80.00,
            rating: 4.9,
            availability: true,
            password_set: true,
            skills: ['Python', 'Machine Learning', 'Deep Learning', 'Data Analysis'],
            projects: [
              { id: 101, title: 'AI-Powered Customer Analytics', field_of_study: 'Computer Science', status: 'in_progress', created_at: '2024-01-20T10:00:00Z', user: { name: 'John Smith' } },
            ],
          },
          {
            id: 2,
            user: { name: 'Prof. Michael Chen', email: 'michael.chen@researchpro.com', phone: '+254 700 333 444' },
            id_number: 'STF002',
            specialization: 'Environmental Science',
            experience_years: 15,
            qualification: 'PhD in Environmental Studies',
            bio: 'Expert in climate science and sustainability research.',
            rate_per_page: 6.00,
            rate_per_chapter: 100.00,
            rating: 5.0,
            availability: true,
            password_set: true,
            skills: ['Climate Analysis', 'GIS', 'Statistical Modeling'],
            projects: [],
          },
          {
            id: 3,
            user: { name: 'Dr. Amanda Foster', email: 'amanda.foster@researchpro.com', phone: null },
            id_number: 'STF003',
            specialization: 'Biotechnology',
            experience_years: 8,
            qualification: 'PhD in Molecular Biology',
            bio: 'Focused on genetic research and biomedical applications.',
            rate_per_page: 4.50,
            rate_per_chapter: 70.00,
            rating: 4.7,
            availability: false,
            password_set: false,
            skills: ['Genetic Analysis', 'Lab Techniques', 'Research Design'],
            projects: [],
          },
        ]);
      } else {
        setStaff(fetchedStaff);
      }
    } catch (err) {
      console.error('Failed to fetch staff:', err);
      setStaff([]);
    } finally {
      setLoading(false);
    }
  };

  const handleViewStaff = async (staffId) => {
    try {
      const response = await adminService.getStaffMember(staffId);
      setSelectedStaff(response.staff);
    } catch (err) {
      console.error('Failed to fetch staff details:', err);
      const fallback = staff.find(s => s.id === staffId);
      if (fallback) setSelectedStaff(fallback);
    }
  };

  const handleCloseModal = () => {
    setShowAddModal(false);
    setSelectedStaff(null);
    setFormData(EMPTY_FORM);
    setFormError(null);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleAddStaff = async (e) => {
    e.preventDefault();
    setSubmitting(true);
    setFormError(null);

    try {
      const staffData = {
        name:             formData.name.trim(),
        email:            formData.email.trim().toLowerCase(),
        id_number:        formData.id_number.trim(),
        phone:            formData.phone.trim(),
        specialization:   formData.specialization.trim(),
        experience_years: parseInt(formData.experience_years, 10) || 0,
        qualification:    formData.qualification.trim(),
        bio:              formData.bio.trim(),
        rate_per_page:    parseFloat(formData.rate_per_page) || 0,
        rate_per_chapter: parseFloat(formData.rate_per_chapter) || 0,
        skills: formData.skills
          .split(',')
          .map(s => s.trim())
          .filter(Boolean),
      };

      await adminService.addStaff(staffData);

      // 1. Close modal
      handleCloseModal();

      // 2. Reload the staff list so the new member appears immediately
      await fetchStaff();

      // 3. Notify parent dashboard
      if (onDataUpdate) onDataUpdate();

      // 4. Show success banner (after fetchStaff so loading state is gone)
      setAlert({
        type: 'success',
        message: `${staffData.name} has been added successfully. A setup email has been sent to ${staffData.email}.`,
      });

    } catch (err) {
      console.error('Failed to add staff:', err);
      // Error stays inside the modal, not on the page
      setFormError(
        err.response?.data?.error ||
        err.message ||
        'Failed to add staff member. Please try again.'
      );
    } finally {
      setSubmitting(false);
    }
  };

  const filteredStaff = staff.filter(member =>
    member.user?.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    member.user?.email?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    member.specialization?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) return <Loader text="Loading staff..." />;

  return (
    <div className="admin-view staff-view">

      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="staff-view-header">
        <div className="staff-header-content">
          <div className="staff-header-left">
            <div className="staff-icon-wrapper">
              <span className="staff-main-icon">👨‍💼</span>
            </div>
            <div>
              <h1 className="staff-view-title">Staff Members</h1>
              <p className="staff-view-subtitle">
                {filteredStaff.length} {filteredStaff.length === 1 ? 'member' : 'members'} in your team
              </p>
            </div>
          </div>
          <button className="add-staff-button" onClick={() => setShowAddModal(true)}>
            <span className="add-icon">+</span>
            <span>Add Staff</span>
          </button>
        </div>
      </div>

      {/* ── Page-level Alert ───────────────────────────────────────── */}
      <div className="staff-alert-wrapper" aria-live="polite">
        <PageAlert alert={alert} onClose={() => setAlert(null)} />
      </div>

      {/* ── Search ─────────────────────────────────────────────────── */}
      <div className="staff-search-section">
        <div className="search-bar-wrapper">
          <span className="search-icon">🔍</span>
          <input
            type="text"
            placeholder="Search by name, email, or specialization..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="staff-search-input"
          />
        </div>
      </div>

      {/* ── Staff Grid ─────────────────────────────────────────────── */}
      {filteredStaff.length === 0 ? (
        <div className="staff-empty-state">
          <div className="empty-illustration">
            <span className="empty-icon-large">👨‍💼</span>
            <div className="empty-icon-ring"></div>
          </div>
          <h3 className="empty-title">No Staff Members Yet</h3>
          <p className="empty-description">Start building your team by adding your first staff member</p>
          <button className="add-staff-button" onClick={() => setShowAddModal(true)}>
            <span className="add-icon">+</span>
            <span>Add First Staff Member</span>
          </button>
        </div>
      ) : (
        <div className="staff-list-grid">
          {filteredStaff.map((member) => (
            <div key={member.id} className="staff-member-card">

              <div className="availability-indicator">
                <span className={`availability-dot ${member.availability ? 'available' : 'unavailable'}`} />
              </div>

              {!member.password_set && (
                <div className="pending-setup-badge" title="Awaiting account setup">⏳</div>
              )}

              <div className="staff-member-avatar">
                <span className="avatar-text">{member.user?.name?.charAt(0).toUpperCase()}</span>
                <div className="avatar-ring"></div>
              </div>

              <div className="staff-member-info">
                <h3 className="staff-member-name">{member.user?.name}</h3>
                <p className="staff-member-role">{member.specialization}</p>
              </div>

              <div className="staff-member-stats">
                <div className="stat-item">
                  <span className="stat-icon">⭐</span>
                  <span className="stat-value">{member.rating || 'N/A'}</span>
                </div>
                <div className="stat-item">
                  <span className="stat-icon">📚</span>
                  <span className="stat-value">{member.experience_years}y</span>
                </div>
                {member.rate_per_page && (
                  <div className="stat-item">
                    <span className="stat-icon">📄</span>
                    <span className="stat-value">${member.rate_per_page}/pg</span>
                  </div>
                )}
              </div>

              <div className="staff-member-contact">
                <span className="contact-icon">📧</span>
                <span className="contact-email">{member.user?.email}</span>
              </div>

              <button className="view-details-button" onClick={() => handleViewStaff(member.id)}>
                View Full Profile
              </button>
            </div>
          ))}
        </div>
      )}

      {/* ── Add Staff Modal ─────────────────────────────────────────── */}
      {showAddModal && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Add New Staff Member</h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>
            <div className="modal-body">

              <div className="setup-email-notice">
                <span className="notice-icon">📧</span>
                <p>
                  An account setup email will be sent automatically.
                  The staff member will create their own password when they verify their email.
                </p>
              </div>

              {/* Error lives inside the modal */}
              {formError && (
                <div className="sv-alert sv-alert--error sv-alert--modal" role="alert">
                  <span className="sv-alert__icon">!</span>
                  <span className="sv-alert__message">{formError}</span>
                  <button className="sv-alert__close" onClick={() => setFormError(null)} aria-label="Dismiss">×</button>
                </div>
              )}

              <form onSubmit={handleAddStaff}>
                <div className="form-grid">

                  <div className="form-group">
                    <label>Full Name <span className="required">*</span></label>
                    <input type="text" name="name" value={formData.name} onChange={handleInputChange} required placeholder="e.g., Dr. Sarah Johnson" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>Email Address <span className="required">*</span></label>
                    <input type="email" name="email" value={formData.email} onChange={handleInputChange} required placeholder="staff@example.com" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>Phone Number</label>
                    <input type="tel" name="phone" value={formData.phone} onChange={handleInputChange} placeholder="e.g., +254 700 000 000" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>ID / Staff Number <span className="required">*</span></label>
                    <input type="text" name="id_number" value={formData.id_number} onChange={handleInputChange} required placeholder="e.g., STF001 or National ID" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>Specialization <span className="required">*</span></label>
                    <input type="text" name="specialization" value={formData.specialization} onChange={handleInputChange} required placeholder="e.g., Computer Science" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>Years of Experience</label>
                    <input type="number" name="experience_years" value={formData.experience_years} onChange={handleInputChange} min="0" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>Rate Per Page ($)</label>
                    <input type="number" name="rate_per_page" value={formData.rate_per_page} onChange={handleInputChange} min="0" step="0.01" placeholder="0.00" className="form-input" />
                  </div>

                  <div className="form-group">
                    <label>Rate Per Chapter ($)</label>
                    <input type="number" name="rate_per_chapter" value={formData.rate_per_chapter} onChange={handleInputChange} min="0" step="0.01" placeholder="0.00" className="form-input" />
                  </div>

                  <div className="form-group full-width">
                    <label>Qualification</label>
                    <input type="text" name="qualification" value={formData.qualification} onChange={handleInputChange} placeholder="e.g., PhD in Computer Science" className="form-input" />
                  </div>

                  <div className="form-group full-width">
                    <label>Skills <span className="field-hint">(comma-separated)</span></label>
                    <input type="text" name="skills" value={formData.skills} onChange={handleInputChange} placeholder="e.g., Python, Machine Learning, Data Analysis" className="form-input" />
                  </div>

                  <div className="form-group full-width">
                    <label>Bio</label>
                    <textarea name="bio" value={formData.bio} onChange={handleInputChange} rows="3" placeholder="Brief professional background..." className="form-textarea" />
                  </div>

                </div>

                <div className="modal-actions">
                  <Button type="button" variant="secondary" onClick={handleCloseModal}>
                    Cancel
                  </Button>
                  <Button type="submit" variant="primary" disabled={submitting}>
                    {submitting ? 'Creating...' : 'Add Staff Member'}
                  </Button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* ── Staff Details Modal ─────────────────────────────────────── */}
      {selectedStaff && (
        <div className="modal-overlay" onClick={handleCloseModal}>
          <div className="modal-content modal-large" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Staff Member Details</h2>
              <button className="modal-close" onClick={handleCloseModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="staff-details-view">

                <div className="detail-section">
                  <h3>Personal Information</h3>
                  <div className="detail-grid">
                    <div className="detail-item"><label>Name</label><p>{selectedStaff.user?.name}</p></div>
                    <div className="detail-item"><label>Email</label><p>{selectedStaff.user?.email}</p></div>
                    <div className="detail-item"><label>Phone</label><p>{selectedStaff.user?.phone || 'Not set'}</p></div>
                    <div className="detail-item"><label>ID / Staff Number</label><p>{selectedStaff.id_number || 'Not set'}</p></div>
                    <div className="detail-item"><label>Specialization</label><p>{selectedStaff.specialization}</p></div>
                    <div className="detail-item"><label>Experience</label><p>{selectedStaff.experience_years} years</p></div>
                    <div className="detail-item"><label>Qualification</label><p>{selectedStaff.qualification || 'Not specified'}</p></div>
                    <div className="detail-item"><label>Rate Per Page</label><p>{selectedStaff.rate_per_page ? `$${selectedStaff.rate_per_page}` : 'Not set'}</p></div>
                    <div className="detail-item"><label>Rate Per Chapter</label><p>{selectedStaff.rate_per_chapter ? `$${selectedStaff.rate_per_chapter}` : 'Not set'}</p></div>
                    <div className="detail-item"><label>Rating</label><p>⭐ {selectedStaff.rating || 'N/A'}</p></div>
                    <div className="detail-item">
                      <label>Availability</label>
                      <p><span className={`status-badge ${selectedStaff.availability ? 'status-active' : 'status-inactive'}`}>{selectedStaff.availability ? 'Available' : 'Unavailable'}</span></p>
                    </div>
                    <div className="detail-item">
                      <label>Account Status</label>
                      <p><span className={`status-badge ${selectedStaff.password_set ? 'status-active' : 'status-pending'}`}>{selectedStaff.password_set ? 'Active' : 'Pending Setup'}</span></p>
                    </div>
                    {selectedStaff.bio && (
                      <div className="detail-item full-width"><label>Bio</label><p>{selectedStaff.bio}</p></div>
                    )}
                    {selectedStaff.skills && selectedStaff.skills.length > 0 && (
                      <div className="detail-item full-width">
                        <label>Skills</label>
                        <div className="skills-list">
                          {selectedStaff.skills.map((skill, index) => (
                            <span key={index} className="skill-tag">{skill}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </div>

                <div className="detail-section">
                  <h3>Assigned Projects ({selectedStaff.projects?.length || 0})</h3>
                  {selectedStaff.projects && selectedStaff.projects.length > 0 ? (
                    <div className="projects-list">
                      {selectedStaff.projects.map((project) => (
                        <div key={project.id} className="project-card">
                          <div className="project-header">
                            <h4>{project.title}</h4>
                            <span className={`status-badge status-${project.status}`}>{project.status}</span>
                          </div>
                          <p className="project-field">{project.field_of_study}</p>
                          <div className="project-meta">
                            <span>📅 {new Date(project.created_at).toLocaleDateString()}</span>
                            {project.user && <span>👤 {project.user.name}</span>}
                          </div>
                        </div>
                      ))}
                    </div>
                  ) : (
                    <p className="no-data">No projects assigned yet</p>
                  )}
                </div>

              </div>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default StaffView;