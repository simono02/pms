import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import Input from '../common/Input';
import Modal from '../common/Modal';
import './StaffManagement.css';

const StaffManagement = ({ onDataUpdate }) => {
  const [staff, setStaff] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showAddModal, setShowAddModal] = useState(false);
  const [editingStaff, setEditingStaff] = useState(null);

  useEffect(() => {
    fetchStaff();
  }, []);

  const fetchStaff = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAllStaff();
      setStaff(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = (value) => {
    setSearchTerm(value);
  };

  const handleAddStaff = () => {
    setEditingStaff(null);
    setShowAddModal(true);
  };

  const handleEditStaff = (staffMember) => {
    setEditingStaff(staffMember);
    setShowAddModal(true);
  };

  const handleStatusToggle = async (staffId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await adminService.updateStaffStatus(staffId, newStatus);
      setAlert({ 
        type: 'success', 
        message: `Staff member ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully!` 
      });
      fetchStaff();
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to update staff status.' 
      });
    }
  };

  const handleDeleteStaff = async (staffId) => {
    if (!window.confirm('Are you sure you want to delete this staff member? This action cannot be undone.')) {
      return;
    }

    try {
      await adminService.deleteStaff(staffId);
      setAlert({ type: 'success', message: 'Staff member deleted successfully!' });
      fetchStaff();
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to delete staff member.' 
      });
    }
  };

  const handleModalClose = () => {
    setShowAddModal(false);
    setEditingStaff(null);
  };

  const handleStaffSaved = () => {
    setShowAddModal(false);
    setEditingStaff(null);
    setAlert({ type: 'success', message: 'Staff member saved successfully!' });
    fetchStaff();
  };

  const filteredStaff = staff.filter(member => 
    member.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    member.email.toLowerCase().includes(searchTerm.toLowerCase())
  );

  if (loading) {
    return <Loader text="Loading staff members..." />;
  }

  if (error) {
    return (
      <div className="staff-management-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchStaff} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="staff-management">
      <div className="staff-header">
        <h2>Staff Management</h2>
        <Button variant="primary" onClick={handleAddStaff}>
          Add Staff Member
        </Button>
      </div>

      {alert && (
        <Alert 
          type={alert.type} 
          message={alert.message} 
          onClose={() => setAlert(null)}
          autoClose
        />
      )}

      <div className="staff-filters">
        <Input
          type="text"
          placeholder="Search by name or email..."
          value={searchTerm}
          onChange={handleSearch}
          className="search-input"
        />
      </div>

      <div className="staff-table-container">
        <table className="staff-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Specialization</th>
              <th>Assigned Projects</th>
              <th>Joined Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredStaff.map((member) => (
              <tr key={member.id}>
                <td className="staff-name">{member.name}</td>
                <td className="staff-email">{member.email}</td>
                <td className="staff-specialization">{member.specialization || 'General'}</td>
                <td className="staff-projects">{member.assigned_projects || 0}</td>
                <td className="staff-date">{formatDateString(member.created_at)}</td>
                <td className="staff-status">
                  <span className={`status-badge ${member.status}`}>
                    {member.status}
                  </span>
                </td>
                <td className="staff-actions">
                  <Button
                    variant="secondary"
                    size="small"
                    onClick={() => handleEditStaff(member)}
                  >
                    Edit
                  </Button>
                  <Button
                    variant={member.status === 'active' ? 'secondary' : 'primary'}
                    size="small"
                    onClick={() => handleStatusToggle(member.id, member.status)}
                  >
                    {member.status === 'active' ? 'Deactivate' : 'Activate'}
                  </Button>
                  <Button
                    variant="danger"
                    size="small"
                    onClick={() => handleDeleteStaff(member.id)}
                  >
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredStaff.length === 0 && (
        <div className="no-staff">
          <p>No staff members found matching your criteria.</p>
        </div>
      )}

      {showAddModal && (
        <StaffForm
          isOpen={showAddModal}
          onClose={handleModalClose}
          staffMember={editingStaff}
          onSuccess={handleStaffSaved}
        />
      )}
    </div>
  );
};

const StaffForm = ({ isOpen, onClose, staffMember, onSuccess }) => {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    specialization: '',
    status: 'active'
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (staffMember) {
      setFormData({
        name: staffMember.name,
        email: staffMember.email,
        password: '',
        specialization: staffMember.specialization || '',
        status: staffMember.status
      });
    }
  }, [staffMember]);

  const handleChange = (name, value) => {
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.name) {
      newErrors.name = 'Name is required';
    }
    
    if (!formData.email) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Email is invalid';
    }
    
    if (!staffMember && !formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password && formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;
    
    setLoading(true);
    
    try {
      if (staffMember) {
        await adminService.updateStaff(staffMember.id, formData);
      } else {
        await adminService.addStaff(formData);
      }
      onSuccess();
    } catch (error) {
      setErrors({ submit: error.message });
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <Modal 
      isOpen={isOpen} 
      onClose={onClose}
      title={staffMember ? 'Edit Staff Member' : 'Add Staff Member'}
      size="medium"
    >
      {errors.submit && (
        <Alert type="error" message={errors.submit} />
      )}
      
      <form onSubmit={handleSubmit} className="staff-form">
        <Input
          label="Name"
          type="text"
          name="name"
          value={formData.name}
          onChange={(value) => handleChange('name', value)}
          placeholder="Enter staff member name"
          error={errors.name}
          required
        />
        
        <Input
          label="Email"
          type="email"
          name="email"
          value={formData.email}
          onChange={(value) => handleChange('email', value)}
          placeholder="Enter email address"
          error={errors.email}
          required
        />
        
        <Input
          label={staffMember ? "New Password (leave blank to keep current)" : "Password"}
          type="password"
          name="password"
          value={formData.password}
          onChange={(value) => handleChange('password', value)}
          placeholder={staffMember ? "Enter new password" : "Enter password"}
          error={errors.password}
          required={!staffMember}
        />
        
        <div className="form-group">
          <label className="input-label">Specialization</label>
          <select
            name="specialization"
            value={formData.specialization}
            onChange={(e) => handleChange('specialization', e.target.value)}
            className="input-field"
          >
            <option value="">Select specialization</option>
            <option value="computer-science">Computer Science</option>
            <option value="engineering">Engineering</option>
            <option value="medicine">Medicine</option>
            <option value="business">Business</option>
            <option value="education">Education</option>
            <option value="social-sciences">Social Sciences</option>
            <option value="natural-sciences">Natural Sciences</option>
            <option value="general">General</option>
          </select>
        </div>
        
        <div className="form-group">
          <label className="input-label">Status</label>
          <select
            name="status"
            value={formData.status}
            onChange={(e) => handleChange('status', e.target.value)}
            className="input-field"
          >
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
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
            {staffMember ? 'Update Staff' : 'Add Staff'}
          </Button>
        </div>
      </form>
    </Modal>
  );
};

export default StaffManagement;
