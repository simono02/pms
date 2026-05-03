import React, { createContext, useContext, useReducer, useEffect } from 'react';

const ThemeContext = createContext();

const themeReducer = (state, action) => {
  switch (action.type) {
    case 'TOGGLE_THEME':
      return {
        ...state,
        theme: state.theme === 'light' ? 'dark' : 'light'
      };
    
    case 'SET_THEME':
      return {
        ...state,
        theme: action.payload
      };
    
    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        sidebarCollapsed: !state.sidebarCollapsed
      };
    
    case 'SET_SIDEBAR_COLLAPSED':
      return {
        ...state,
        sidebarCollapsed: action.payload
      };
    
    case 'SET_PRIMARY_COLOR':
      return {
        ...state,
        primaryColor: action.payload
      };
    
    case 'SET_FONT_SIZE':
      return {
        ...state,
        fontSize: action.payload
      };
    
    case 'SET_LANGUAGE':
      return {
        ...state,
        language: action.payload
      };
    
    case 'SET_NOTIFICATIONS_ENABLED':
      return {
        ...state,
        notificationsEnabled: action.payload
      };
    
    case 'SET_AUTO_SAVE':
      return {
        ...state,
        autoSave: action.payload
      };
    
    case 'LOAD_SETTINGS':
      return {
        ...state,
        ...action.payload
      };
    
    default:
      return state;
  }
};

const initialState = {
  theme: 'light',
  sidebarCollapsed: false,
  primaryColor: '#007bff',
  fontSize: 'medium',
  language: 'en',
  notificationsEnabled: true,
  autoSave: true
};

const THEME_STORAGE_KEY = 'app_theme_settings';

export const ThemeProvider = ({ children }) => {
  const [state, dispatch] = useReducer(themeReducer, initialState);

  useEffect(() => {
    loadThemeSettings();
  }, []);

  useEffect(() => {
    saveThemeSettings();
    applyThemeToDOM();
  }, [state.theme, state.primaryColor, state.fontSize]);

  const loadThemeSettings = () => {
    try {
      const savedSettings = localStorage.getItem(THEME_STORAGE_KEY);
      if (savedSettings) {
        const settings = JSON.parse(savedSettings);
        dispatch({ type: 'LOAD_SETTINGS', payload: settings });
      }
    } catch (error) {
      console.error('Failed to load theme settings:', error);
    }
  };

  const saveThemeSettings = () => {
    try {
      const settings = {
        theme: state.theme,
        sidebarCollapsed: state.sidebarCollapsed,
        primaryColor: state.primaryColor,
        fontSize: state.fontSize,
        language: state.language,
        notificationsEnabled: state.notificationsEnabled,
        autoSave: state.autoSave
      };
      localStorage.setItem(THEME_STORAGE_KEY, JSON.stringify(settings));
    } catch (error) {
      console.error('Failed to save theme settings:', error);
    }
  };

  const applyThemeToDOM = () => {
    const root = document.documentElement;
    
    root.setAttribute('data-theme', state.theme);
    root.style.setProperty('--primary-color', state.primaryColor);
    
    const fontSizeMap = {
      small: '14px',
      medium: '16px',
      large: '18px',
      extraLarge: '20px'
    };
    
    root.style.setProperty('--font-size', fontSizeMap[state.fontSize] || '16px');
    
    if (state.theme === 'dark') {
      root.classList.add('dark-theme');
    } else {
      root.classList.remove('dark-theme');
    }
  };

  const toggleTheme = () => {
    dispatch({ type: 'TOGGLE_THEME' });
  };

  const setTheme = (theme) => {
    dispatch({ type: 'SET_THEME', payload: theme });
  };

  const toggleSidebar = () => {
    dispatch({ type: 'TOGGLE_SIDEBAR' });
  };

  const setSidebarCollapsed = (collapsed) => {
    dispatch({ type: 'SET_SIDEBAR_COLLAPSED', payload: collapsed });
  };

  const setPrimaryColor = (color) => {
    dispatch({ type: 'SET_PRIMARY_COLOR', payload: color });
  };

  const setFontSize = (size) => {
    dispatch({ type: 'SET_FONT_SIZE', payload: size });
  };

  const setLanguage = (language) => {
    dispatch({ type: 'SET_LANGUAGE', payload: language });
  };

  const setNotificationsEnabled = (enabled) => {
    dispatch({ type: 'SET_NOTIFICATIONS_ENABLED', payload: enabled });
  };

  const setAutoSave = (autoSave) => {
    dispatch({ type: 'SET_AUTO_SAVE', payload: autoSave });
  };

  const resetTheme = () => {
    dispatch({ type: 'LOAD_SETTINGS', payload: initialState });
  };

  const value = {
    ...state,
    toggleTheme,
    setTheme,
    toggleSidebar,
    setSidebarCollapsed,
    setPrimaryColor,
    setFontSize,
    setLanguage,
    setNotificationsEnabled,
    setAutoSave,
    resetTheme
  };

  return (
    <ThemeContext.Provider value={value}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

export default ThemeContext;
