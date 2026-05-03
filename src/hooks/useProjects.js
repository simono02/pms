import { useState, useCallback } from 'react';
import projectService from '../services/projectService';

export const useProjects = () => {
  const [projects, setProjects] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fetchProjects = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectService.getProjects();
      setProjects(data);
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  }, []);

  const createProject = useCallback(async (projectData) => {
    try {
      setLoading(true);
      setError(null);
      const newProject = await projectService.createProject(projectData);
      setProjects(prev => [newProject, ...prev]);
      return newProject;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const updateProject = useCallback(async (projectId, projectData) => {
    try {
      setLoading(true);
      setError(null);
      const updatedProject = await projectService.updateProject(projectId, projectData);
      setProjects(prev => 
        prev.map(project => 
          project.id === projectId ? updatedProject : project
        )
      );
      return updatedProject;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const deleteProject = useCallback(async (projectId) => {
    try {
      setLoading(true);
      setError(null);
      await projectService.deleteProject(projectId);
      setProjects(prev => prev.filter(project => project.id !== projectId));
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const getProject = useCallback(async (projectId) => {
    try {
      setLoading(true);
      setError(null);
      const project = await projectService.getProject(projectId);
      return project;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const describeProject = useCallback(async (projectId, descriptionData) => {
    try {
      setLoading(true);
      setError(null);
      const updatedProject = await projectService.describeProject(projectId, descriptionData);
      setProjects(prev => 
        prev.map(project => 
          project.id === projectId ? updatedProject : project
        )
      );
      return updatedProject;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const getProjectsByStatus = useCallback(async (status) => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectService.getProjectsByStatus(status);
      return data;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const searchProjects = useCallback(async (query) => {
    try {
      setLoading(true);
      setError(null);
      const data = await projectService.searchProjects(query);
      return data;
    } catch (error) {
      setError(error.message);
      throw error;
    } finally {
      setLoading(false);
    }
  }, []);

  const clearError = useCallback(() => setError(null), []);

  return {
    projects,
    loading,
    error,
    fetchProjects,
    createProject,
    updateProject,
    deleteProject,
    getProject,
    describeProject,
    getProjectsByStatus,
    searchProjects,
    clearError
  };
};

export default useProjects;