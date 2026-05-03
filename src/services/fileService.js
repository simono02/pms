import api from './api';

const fileService = {
  uploadFile: async (file, type = 'projects') => {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('type', type);
    
    const response = await api.post('/files/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        const progress = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        return progress;
      },
    });
    return response;
  },

  downloadFile: async (fileId) => {
    const response = await api.get(`/files/download/${fileId}`, {
      responseType: 'blob'
    });
    return response;
  },

  getFile: async (fileId) => {
    const response = await api.get(`/files/${fileId}`);
    return response;
  },

  deleteFile: async (fileId) => {
    const response = await api.delete(`/files/${fileId}`);
    return response;
  },

  getFiles: async (type = 'projects') => {
    const response = await api.get(`/files?type=${type}`);
    return response;
  },

  getFilePreview: async (fileId, pages = 2) => {
    const response = await api.get(`/files/${fileId}/preview?pages=${pages}`);
    return response;
  },

  generateThumbnail: async (fileId) => {
    const response = await api.post(`/files/${fileId}/thumbnail`);
    return response;
  },

  compressFile: async (fileId, quality = 0.8) => {
    const response = await api.post(`/files/${fileId}/compress`, { quality });
    return response;
  },

  convertToPDF: async (fileId) => {
    const response = await api.post(`/files/${fileId}/convert-pdf`);
    return response;
  },

  mergeFiles: async (fileIds, outputName) => {
    const response = await api.post('/files/merge', { 
      file_ids: fileIds, 
      output_name: outputName 
    });
    return response;
  },

  splitFile: async (fileId, splitPoints) => {
    const response = await api.post(`/files/${fileId}/split`, { split_points: splitPoints });
    return response;
  },

  extractPages: async (fileId, pages) => {
    const response = await api.post(`/files/${fileId}/extract-pages`, { pages });
    return response;
  },

  rotateFile: async (fileId, degrees) => {
    const response = await api.post(`/files/${fileId}/rotate`, { degrees });
    return response;
  },

  addWatermark: async (fileId, watermarkData) => {
    const response = await api.post(`/files/${fileId}/watermark`, watermarkData);
    return response;
  },

  signFile: async (fileId, signatureData) => {
    const response = await api.post(`/files/${fileId}/sign`, signatureData);
    return response;
  },

  validateFile: async (fileId) => {
    const response = await api.get(`/files/${fileId}/validate`);
    return response;
  },

  getFileMetadata: async (fileId) => {
    const response = await api.get(`/files/${fileId}/metadata`);
    return response;
  },

  searchFiles: async (query, filters = {}) => {
    const params = new URLSearchParams({ q: query, ...filters });
    const response = await api.get(`/files/search?${params}`);
    return response;
  },

  shareFile: async (fileId, shareData) => {
    const response = await api.post(`/files/${fileId}/share`, shareData);
    return response;
  },

  getSharedFile: async (shareToken) => {
    const response = await api.get(`/files/shared/${shareToken}`);
    return response;
  },

  revokeShare: async (fileId, shareId) => {
    const response = await api.delete(`/files/${fileId}/share/${shareId}`);
    return response;
  },

  getStorageUsage: async () => {
    const response = await api.get('/files/storage-usage');
    return response;
  },

  cleanupFiles: async () => {
    const response = await api.post('/files/cleanup');
    return response;
  }
};

export default fileService;
