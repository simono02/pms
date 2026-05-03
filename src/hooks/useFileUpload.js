import { useState } from 'react';
import fileService from '../services/fileService';

export const useFileUpload = () => {
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState(null);

  const uploadFile = async (file, type = 'projects') => {
    try {
      setUploading(true);
      setUploadProgress(0);
      setError(null);

      const response = await fileService.uploadFile(file, type);
      
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const uploadFileWithProgress = async (file, type = 'projects', onProgress) => {
    try {
      setUploading(true);
      setUploadProgress(0);
      setError(null);

      const formData = new FormData();
      formData.append('file', file);
      formData.append('type', type);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/files/upload`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`,
        },
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Upload failed');
      }

      const reader = response.body.getReader();
      const contentLength = +response.headers.get('Content-Length');
      let receivedLength = 0;
      let chunks = [];

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) break;
        
        chunks.push(value);
        receivedLength += value.length;
        
        const progress = Math.round((receivedLength / contentLength) * 100);
        setUploadProgress(progress);
        
        if (onProgress) {
          onProgress(progress);
        }
      }

      const result = new Uint8Array(receivedLength);
      let position = 0;
      for (const chunk of chunks) {
        result.set(chunk, position);
        position += chunk.length;
      }

      const responseData = JSON.parse(new TextDecoder('utf-8').decode(result));
      
      return responseData;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setUploading(false);
      setUploadProgress(0);
    }
  };

  const downloadFile = async (fileId, filename) => {
    try {
      setError(null);
      const response = await fileService.downloadFile(fileId);
      
      const url = window.URL.createObjectURL(new Blob([response]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', filename || 'download');
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
      
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  const getFilePreview = async (fileId, pages = 2) => {
    try {
      setError(null);
      const response = await fileService.getFilePreview(fileId, pages);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  const deleteFile = async (fileId) => {
    try {
      setError(null);
      const response = await fileService.deleteFile(fileId);
      return response;
    } catch (error) {
      setError(error.message);
      throw error;
    }
  };

  const validateFile = (file, maxSize = 10 * 1024 * 1024, allowedTypes = ['application/pdf']) => {
    const errors = [];
    
    if (file.size > maxSize) {
      errors.push(`File size must be less than ${maxSize / 1024 / 1024}MB`);
    }
    
    if (!allowedTypes.includes(file.type)) {
      errors.push(`File type must be one of: ${allowedTypes.join(', ')}`);
    }
    
    return errors;
  };

  const clearError = () => setError(null);

  return {
    uploading,
    uploadProgress,
    error,
    uploadFile,
    uploadFileWithProgress,
    downloadFile,
    getFilePreview,
    deleteFile,
    validateFile,
    clearError
  };
};

export default useFileUpload;
