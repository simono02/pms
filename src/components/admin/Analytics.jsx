import React, { useState, useEffect } from 'react';
import { adminService } from '../../services/adminService';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import './Analytics.css';

const Analytics = () => {
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('month');

  useEffect(() => {
    fetchAnalytics();
  }, [timeRange]);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const data = await adminService.getAnalytics(timeRange);
      setAnalytics(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader text="Loading analytics..." />;
  }

  if (error) {
    return (
      <div className="analytics-error">
        <Alert type="error" message={error} />
        <button onClick={fetchAnalytics} className="retry-button">
          Retry
        </button>
      </div>
    );
  }

  if (!analytics) {
    return <div>No analytics data available</div>;
  }

  return (
    <div className="analytics">
      <div className="analytics-header">
        <h2>System Analytics</h2>
        <div className="time-range-selector">
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
            <option value="year">Last Year</option>
          </select>
        </div>
      </div>

      <div className="analytics-overview">
        <div className="overview-cards">
          <div className="overview-card">
            <h3>Total Revenue</h3>
            <span className="card-value">${analytics.totalRevenue.toFixed(2)}</span>
            <span className="card-change positive">
              +{analytics.revenueGrowth}% from last period
            </span>
          </div>
          
          <div className="overview-card">
            <h3>New Users</h3>
            <span className="card-value">{analytics.newUsers}</span>
            <span className="card-change positive">
              +{analytics.userGrowth}% from last period
            </span>
          </div>
          
          <div className="overview-card">
            <h3>Projects Completed</h3>
            <span className="card-value">{analytics.completedProjects}</span>
            <span className="card-change positive">
              +{analytics.projectGrowth}% from last period
            </span>
          </div>
          
          <div className="overview-card">
            <h3>Active Staff</h3>
            <span className="card-value">{analytics.activeStaff}</span>
            <span className="card-change neutral">
              No change from last period
            </span>
          </div>
        </div>
      </div>

      <div className="analytics-charts">
        <div className="chart-container">
          <h3>Revenue Trend</h3>
          <div className="chart-placeholder">
            <Alert 
              type="info" 
              message="Revenue trend chart would be displayed here using a charting library like Chart.js or Recharts" 
            />
            <div className="mock-chart">
              <div className="chart-bar" style={{ height: '60%' }}></div>
              <div className="chart-bar" style={{ height: '80%' }}></div>
              <div className="chart-bar" style={{ height: '45%' }}></div>
              <div className="chart-bar" style={{ height: '90%' }}></div>
              <div className="chart-bar" style={{ height: '70%' }}></div>
              <div className="chart-bar" style={{ height: '85%' }}></div>
            </div>
          </div>
        </div>

        <div className="chart-container">
          <h3>Project Status Distribution</h3>
          <div className="chart-placeholder">
            <Alert 
              type="info" 
              message="Pie chart showing project status distribution would be displayed here" 
            />
            <div className="mock-pie-chart">
              <div className="pie-segment pending" style={{ '--percentage': '30%' }}></div>
              <div className="pie-segment in-progress" style={{ '--percentage': '40%' }}></div>
              <div className="pie-segment completed" style={{ '--percentage': '30%' }}></div>
            </div>
            <div className="pie-legend">
              <div className="legend-item">
                <span className="legend-color pending"></span>
                <span>Pending (30%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color in-progress"></span>
                <span>In Progress (40%)</span>
              </div>
              <div className="legend-item">
                <span className="legend-color completed"></span>
                <span>Completed (30%)</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="analytics-details">
        <div className="detail-section">
          <h3>Top Research Fields</h3>
          <div className="field-list">
            {analytics.topFields.map((field, index) => (
              <div key={index} className="field-item">
                <span className="field-name">{field.name}</span>
                <span className="field-count">{field.count} projects</span>
              </div>
            ))}
          </div>
        </div>

        <div className="detail-section">
          <h3>Staff Performance</h3>
          <div className="staff-performance">
            {analytics.topStaff.map((staff, index) => (
              <div key={index} className="staff-item">
                <span className="staff-name">{staff.name}</span>
                <span className="staff-projects">{staff.completedProjects} completed</span>
                <span className="staff-rating">⭐ {staff.rating}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="analytics-tables">
        <div className="table-section">
          <h3>Recent Activity</h3>
          <div className="activity-table">
            <table>
              <thead>
                <tr>
                  <th>Date</th>
                  <th>User</th>
                  <th>Action</th>
                  <th>Details</th>
                </tr>
              </thead>
              <tbody>
                {analytics.recentActivity.map((activity, index) => (
                  <tr key={index}>
                    <td>{activity.date}</td>
                    <td>{activity.user}</td>
                    <td>{activity.action}</td>
                    <td>{activity.details}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="analytics-export">
        <h3>Export Reports</h3>
        <div className="export-buttons">
          <button className="export-btn">
            Export as PDF
          </button>
          <button className="export-btn">
            Export as Excel
          </button>
          <button className="export-btn">
            Export as CSV
          </button>
        </div>
      </div>
    </div>
  );
};

export default Analytics;
