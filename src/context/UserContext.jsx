import React, { createContext, useContext, useReducer, useEffect } from 'react';
import userService from '../services/userService';

const UserContext = createContext();

const userReducer = (state, action) => {
  switch (action.type) {
    case 'SET_PROFILE':
      return {
        ...state,
        profile: action.payload,
        loading: false,
        error: null
      };
    
    case 'UPDATE_PROFILE':
      return {
        ...state,
        profile: { ...state.profile, ...action.payload },
        loading: false,
        error: null
      };
    
    case 'SET_PROJECTS':
      return {
        ...state,
        projects: action.payload,
        loading: false,
        error: null
      };
    
    case 'ADD_PROJECT':
      return {
        ...state,
        projects: [action.payload, ...state.projects],
        loading: false,
        error: null
      };
    
    case 'UPDATE_PROJECT':
      return {
        ...state,
        projects: state.projects.map(project =>
          project.id === action.payload.id ? action.payload : project
        ),
        loading: false,
        error: null
      };
    
    case 'REMOVE_PROJECT':
      return {
        ...state,
        projects: state.projects.filter(project => project.id !== action.payload),
        loading: false,
        error: null
      };
    
    case 'SET_NOTIFICATIONS':
      return {
        ...state,
        notifications: action.payload,
        loading: false,
        error: null
      };
    
    case 'ADD_NOTIFICATION':
      return {
        ...state,
        notifications: [action.payload, ...state.notifications],
        unreadCount: state.unreadCount + 1
      };
    
    case 'MARK_NOTIFICATION_READ':
      return {
        ...state,
        notifications: state.notifications.map(notification =>
          notification.id === action.payload
            ? { ...notification, read: true }
            : notification
        ),
        unreadCount: Math.max(0, state.unreadCount - 1)
      };
    
    case 'REMOVE_NOTIFICATION':
      return {
        ...state,
        notifications: state.notifications.filter(
          notification => notification.id !== action.payload
        ),
        unreadCount: Math.max(0, state.unreadCount - 1)
      };
    
    case 'SET_SETTINGS':
      return {
        ...state,
        settings: action.payload,
        loading: false,
        error: null
      };
    
    case 'UPDATE_SETTINGS':
      return {
        ...state,
        settings: { ...state.settings, ...action.payload },
        loading: false,
        error: null
      };
    
    case 'SET_LOADING':
      return {
        ...state,
        loading: action.payload
      };
    
    case 'SET_ERROR':
      return {
        ...state,
        error: action.payload,
        loading: false
      };
    
    case 'CLEAR_ERROR':
      return {
        ...state,
        error: null
      };
    
    default:
      return state;
  }
};

const initialState = {
  profile: null,
  projects: [],
  notifications: [],
  settings: {},
  unreadCount: 0,
  loading: false,
  error: null
};

export const UserProvider = ({ children }) => {
  const [state, dispatch] = useReducer(userReducer, initialState);

  const fetchProfile = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const profile = await userService.getProfile();
      dispatch({ type: 'SET_PROFILE', payload: profile });
      return profile;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateProfile = async (profileData) => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const updatedProfile = await userService.updateProfile(profileData);
      dispatch({ type: 'UPDATE_PROFILE', payload: updatedProfile });
      return updatedProfile;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const fetchProjects = async () => {
    try {
      dispatch({ type: 'SET_LOADING', payload: true });
      const projects = await userService.getProjects();
      dispatch({ type: 'SET_PROJECTS', payload: projects });
      return projects;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const addProject = (project) => {
    dispatch({ type: 'ADD_PROJECT', payload: project });
  };

  const updateProject = (project) => {
    dispatch({ type: 'UPDATE_PROJECT', payload: project });
  };

  const removeProject = (projectId) => {
    dispatch({ type: 'REMOVE_PROJECT', payload: projectId });
  };

  const fetchNotifications = async () => {
    try {
      const notifications = await userService.getNotifications();
      const unreadCount = notifications.filter(n => !n.read).length;
      dispatch({ type: 'SET_NOTIFICATIONS', payload: notifications });
      dispatch({ type: 'SET_UNREAD_COUNT', payload: unreadCount });
      return notifications;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const markNotificationAsRead = async (notificationId) => {
    try {
      await userService.markNotificationAsRead(notificationId);
      dispatch({ type: 'MARK_NOTIFICATION_READ', payload: notificationId });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const deleteNotification = async (notificationId) => {
    try {
      await userService.deleteNotification(notificationId);
      dispatch({ type: 'REMOVE_NOTIFICATION', payload: notificationId });
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const fetchSettings = async () => {
    try {
      const settings = await userService.getSettings();
      dispatch({ type: 'SET_SETTINGS', payload: settings });
      return settings;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const updateSettings = async (settingsData) => {
    try {
      const updatedSettings = await userService.updateSettings(settingsData);
      dispatch({ type: 'UPDATE_SETTINGS', payload: updatedSettings });
      return updatedSettings;
    } catch (error) {
      dispatch({ type: 'SET_ERROR', payload: error.message });
      throw error;
    }
  };

  const clearError = () => {
    dispatch({ type: 'CLEAR_ERROR' });
  };

  const value = {
    ...state,
    fetchProfile,
    updateProfile,
    fetchProjects,
    addProject,
    updateProject,
    removeProject,
    fetchNotifications,
    markNotificationAsRead,
    deleteNotification,
    fetchSettings,
    updateSettings,
    clearError
  };

  return (
    <UserContext.Provider value={value}>
      {children}
    </UserContext.Provider>
  );
};

export const useUser = () => {
  const context = useContext(UserContext);
  if (!context) {
    throw new Error('useUser must be used within a UserProvider');
  }
  return context;
};

export default UserContext;
