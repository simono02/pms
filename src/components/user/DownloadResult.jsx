import React, { useState, useEffect } from 'react';
import { projectService } from '../../services/projectService';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import Button from '../common/Button';
import './DownloadResult.css';

const DownloadResult = ({ projectId }) => {
  const [downloadUrl, setDownloadUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [downloading, setDownloading] = useState(false);

  useEffect(() => {
    fetchDownloadLink();
  }, [projectId]);

  const fetchDownloadLink = async () => {
    try {
      setLoading(true);
      const response = await projectService.getDownloadLink(projectId);
      setDownloadUrl(response.download_url);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = async () => {
    if (!downloadUrl) return;
    
    try {
      setDownloading(true);
      
      const link = document.createElement('a');
      link.href = downloadUrl;
      link.download = `project-${projectId}-result.pdf`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      
      setAlert({ type: 'success', message: 'Download started!' });
    } catch (error) {
      setAlert({ 
        type: 'error', 
        message: 'Failed to start download. Please try again.' 
      });
    } finally {
      setDownloading(false);
    }
  };

  if (loading) {
    return <Loader text="Preparing download..." />;
  }

  if (error) {
    return (
      <div className="download-result-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchDownloadLink} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  if (!downloadUrl) {
    return (
      <div className="download-result-unavailable">
        <Alert type="info" message="Download not available for this project." />
      </div>
    );
  }

  return (
    <div className="download-result">
      <div className="download-header">
        <h3>Download Your Result</h3>
        <p>Your completed project is ready for download.</p>
      </div>
      
      <div className="download-content">
        <div className="download-info">
          <Alert 
            type="success" 
            message="Payment verified! You can now download the complete project result." 
          />
        </div>
        
        <div className="download-actions">
          <Button
            onClick={handleDownload}
            variant="primary"
            size="large"
            loading={downloading}
            disabled={downloading}
            className="download-button"
          >
            {downloading ? 'Downloading...' : 'Download PDF'}
          </Button>
        </div>
        
        <div className="download-terms">
          <Alert 
            type="info" 
            message="This download is for personal use only. Redistribution is prohibited." 
          />
        </div>
      </div>
    </div>
  );
};

export default DownloadResult;
