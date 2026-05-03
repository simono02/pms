import api from './api';

const projectService = {
  createProject: async (projectData) => {
    const response = await api.post('/projects', projectData);
    return response;
  },

  getProjects: async () => {
    const response = await api.get('/projects');
    return response;
  },

  getProject: async (projectId) => {
    const response = await api.get(`/projects/${projectId}`);
    return response;
  },

  updateProject: async (projectId, projectData) => {
    const response = await api.put(`/projects/${projectId}`, projectData);
    return response;
  },

  deleteProject: async (projectId) => {
    const response = await api.delete(`/projects/${projectId}`);
    return response;
  },

  describeProject: async (projectId, descriptionData) => {
    const response = await api.post(`/projects/${projectId}/describe`, descriptionData);
    return response;
  },

  updateDescription: async (projectId, descriptionData) => {
    const response = await api.put(`/projects/${projectId}/description`, descriptionData);
    return response;
  },

  getProjectPreview: async (projectId) => {
    const response = await api.get(`/projects/${projectId}/preview`);
    return response;
  },

  getDownloadLink: async (projectId) => {
    const response = await api.get(`/projects/${projectId}/download`);
    return response;
  },

  getProjectStatus: async (projectId) => {
    const response = await api.get(`/projects/${projectId}/status`);
    return response;
  },

  getProjectHistory: async (projectId) => {
    const response = await api.get(`/projects/${projectId}/history`);
    return response;
  },

  getProjectsByStatus: async (status) => {
    const response = await api.get(`/projects?status=${status}`);
    return response;
  },

  getProjectsByField: async (field) => {
    const response = await api.get(`/projects?field=${field}`);
    return response;
  },

  searchProjects: async (query) => {
    const response = await api.get(`/projects/search?q=${encodeURIComponent(query)}`);
    return response;
  },

  duplicateProject: async (projectId) => {
    const response = await api.post(`/projects/${projectId}/duplicate`);
    return response;
  },

  archiveProject: async (projectId) => {
    const response = await api.put(`/projects/${projectId}/archive`);
    return response;
  },

  restoreProject: async (projectId) => {
    const response = await api.put(`/projects/${projectId}/restore`);
    return response;
  },

  getArchivedProjects: async () => {
    const response = await api.get('/projects/archived');
    return response;
  },

  getProjectStats: async () => {
    const response = await api.get('/projects/stats');
    return response;
  }
};

export { projectService };
export default projectService;
