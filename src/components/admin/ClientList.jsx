import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import { formatDateString } from '../../utils/dateUtils';
import Button from '../common/Button';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import Input from '../common/Input';
import './ClientList.css';

const ClientList = ({ onDataUpdate }) => {
  const [clients, setClients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [alert, setAlert] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterStatus, setFilterStatus] = useState('all');

  useEffect(() => {
    fetchClients();
  }, []);

  const fetchClients = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAllClients();
      setClients(data);
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
  };

  const handleStatusToggle = async (clientId, currentStatus) => {
    try {
      const newStatus = currentStatus === 'active' ? 'inactive' : 'active';
      await adminService.updateClientStatus(clientId, newStatus);
      setAlert({ 
        type: 'success', 
        message: `Client ${newStatus === 'active' ? 'activated' : 'deactivated'} successfully!` 
      });
      fetchClients();
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to update client status.' 
      });
    }
  };

  const handleDeleteClient = async (clientId) => {
    if (!window.confirm('Are you sure you want to delete this client? This action cannot be undone.')) {
      return;
    }

    try {
      await adminService.deleteClient(clientId);
      setAlert({ type: 'success', message: 'Client deleted successfully!' });
      fetchClients();
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: error.message || 'Failed to delete client.' 
      });
    }
  };

  const filteredClients = clients.filter(client => {
    const matchesSearch = client.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         client.email.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesFilter = filterStatus === 'all' || client.status === filterStatus;
    return matchesSearch && matchesFilter;
  });

  if (loading) {
    return <Loader text="Loading clients..." />;
  }

  if (error) {
    return (
      <div className="client-list-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchClients} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  return (
    <div className="client-list">
      <div className="client-list-header">
        <h2>Clients Management</h2>
        <div className="client-stats">
          <span>Total: {clients.length}</span>
          <span>Active: {clients.filter(c => c.status === 'active').length}</span>
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

      <div className="client-filters">
        <Input
          type="text"
          placeholder="Search by name or email..."
          value={searchTerm}
          onChange={handleSearch}
          className="search-input"
        />
        
        <select
          value={filterStatus}
          onChange={(e) => handleFilterChange(e.target.value)}
          className="filter-select"
        >
          <option value="all">All Status</option>
          <option value="active">Active</option>
          <option value="inactive">Inactive</option>
        </select>
      </div>

      <div className="client-table-container">
        <table className="client-table">
          <thead>
            <tr>
              <th>Name</th>
              <th>Email</th>
              <th>Projects</th>
              <th>Joined Date</th>
              <th>Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {filteredClients.map((client) => (
              <tr key={client.id}>
                <td className="client-name">{client.name}</td>
                <td className="client-email">{client.email}</td>
                <td className="client-projects">{client.project_count || 0}</td>
                <td className="client-date">{formatDateString(client.created_at)}</td>
                <td className="client-status">
                  <span className={`status-badge ${client.status}`}>
                    {client.status}
                  </span>
                </td>
                <td className="client-actions">
                  <Button
                    variant={client.status === 'active' ? 'secondary' : 'primary'}
                    size="small"
                    onClick={() => handleStatusToggle(client.id, client.status)}
                  >
                    {client.status === 'active' ? 'Deactivate' : 'Activate'}
                  </Button>
                  <Button
                    variant="danger"
                    size="small"
                    onClick={() => handleDeleteClient(client.id)}
                  >
                    Delete
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {filteredClients.length === 0 && (
        <div className="no-clients">
          <p>No clients found matching your criteria.</p>
        </div>
      )}
    </div>
  );
};

export default ClientList;
