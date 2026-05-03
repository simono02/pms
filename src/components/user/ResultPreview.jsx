import React, { useState, useEffect } from 'react';
import { projectService } from '../../services/projectService';
import Alert from '../common/Alert';
import Loader from '../common/Loader';
import Button from '../common/Button';
import './ResultPreview.css';

const ResultPreview = ({ projectId }) => {
  const [previewUrl, setPreviewUrl] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [pageCount, setPageCount] = useState(0);

  useEffect(() => {
    fetchPreview();
  }, [projectId]);

  const fetchPreview = async () => {
    try {
      setLoading(true);
      const response = await projectService.getProjectPreview(projectId);
      setPreviewUrl(response.preview_url);
      setPageCount(response.page_count);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <Loader text="Loading preview..." />;
  }

  if (error) {
    return (
      <div className="result-preview-error">
        <Alert type="error" message={error} />
        <Button onClick={fetchPreview} variant="primary">
          Retry
        </Button>
      </div>
    );
  }

  if (!previewUrl) {
    return (
      <div className="result-preview-unavailable">
        <Alert type="info" message="Preview not available for this project." />
      </div>
    );
  }

  return (
    <div className="result-preview">
      <div className="preview-header">
        <h3>Project Preview</h3>
        <p className="preview-info">
          Showing first 2 pages of {pageCount} total pages
        </p>
      </div>
      
      <div className="preview-container">
        <iframe
          src={previewUrl}
          className="preview-iframe"
          title="Project Preview"
          onLoad={() => setLoading(false)}
          onError={() => setError('Failed to load preview')}
        />
      </div>
      
      <div className="preview-footer">
        <Alert 
          type="info" 
          message="This is a limited preview. Full access requires payment." 
        />
      </div>
    </div>
  );
};

export default ResultPreview;
