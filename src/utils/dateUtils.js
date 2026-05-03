export const dateUtils = {
  formatDate: (date, options = {}) => {
    const defaultOptions = {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
      return new Intl.DateTimeFormat('en-US', config).format(new Date(date));
    } catch (error) {
      console.error('Date formatting error:', error);
      return 'Invalid Date';
    }
  },

  formatDateString: (dateString) => {
    if (!dateString) return '';
    
    try {
      const date = new Date(dateString);
      return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
      });
    } catch (error) {
      console.error('Date string formatting error:', error);
      return 'Invalid Date';
    }
  },

  formatDateTime: (date, options = {}) => {
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
      return new Intl.DateTimeFormat('en-US', config).format(new Date(date));
    } catch (error) {
      console.error('DateTime formatting error:', error);
      return 'Invalid Date';
    }
  },

  formatTime: (date, options = {}) => {
    const defaultOptions = {
      hour: '2-digit',
      minute: '2-digit'
    };
    
    const config = { ...defaultOptions, ...options };
    
    try {
      return new Intl.DateTimeFormat('en-US', config).format(new Date(date));
    } catch (error) {
      console.error('Time formatting error:', error);
      return 'Invalid Time';
    }
  },

  formatRelativeTime: (date) => {
    if (!date) return '';
    
    try {
      const now = new Date();
      const past = new Date(date);
      const diffInSeconds = Math.floor((now - past) / 1000);
      
      if (diffInSeconds < 60) return 'just now';
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
      if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days ago`;
      if (diffInSeconds < 31536000) return `${Math.floor(diffInSeconds / 2592000)} months ago`;
      return `${Math.floor(diffInSeconds / 31536000)} years ago`;
    } catch (error) {
      console.error('Relative time formatting error:', error);
      return 'Invalid Date';
    }
  },

  formatTimeAgo: (date) => {
    return dateUtils.formatRelativeTime(date);
  },

  formatTimeRemaining: (date) => {
    if (!date) return '';
    
    try {
      const now = new Date();
      const future = new Date(date);
      const diffInSeconds = Math.floor((future - now) / 1000);
      
      if (diffInSeconds < 0) return 'Expired';
      if (diffInSeconds < 60) return `${diffInSeconds} seconds remaining`;
      if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes remaining`;
      if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours remaining`;
      if (diffInSeconds < 2592000) return `${Math.floor(diffInSeconds / 86400)} days remaining`;
      return `${Math.floor(diffInSeconds / 2592000)} months remaining`;
    } catch (error) {
      console.error('Time remaining formatting error:', error);
      return 'Invalid Date';
    }
  },

  has24HoursPassed: (date) => {
    if (!date) return false;
    
    try {
      const created = new Date(date);
      const now = new Date();
      const diffInHours = (now - created) / (1000 * 60 * 60);
      return diffInHours >= 24;
    } catch (error) {
      console.error('24 hours check error:', error);
      return false;
    }
  },

  isWithin24Hours: (date) => {
    return !dateUtils.has24HoursPassed(date);
  },

  addDays: (date, days) => {
    const result = new Date(date);
    result.setDate(result.getDate() + days);
    return result;
  },

  subtractDays: (date, days) => {
    const result = new Date(date);
    result.setDate(result.getDate() - days);
    return result;
  },

  addHours: (date, hours) => {
    const result = new Date(date);
    result.setHours(result.getHours() + hours);
    return result;
  },

  subtractHours: (date, hours) => {
    const result = new Date(date);
    result.setHours(result.getHours() - hours);
    return result;
  },

  getDaysDifference: (date1, date2) => {
    const oneDay = 24 * 60 * 60 * 1000;
    const firstDate = new Date(date1);
    const secondDate = new Date(date2);
    
    return Math.round(Math.abs((firstDate - secondDate) / oneDay));
  },

  getHoursDifference: (date1, date2) => {
    const oneHour = 60 * 60 * 1000;
    const firstDate = new Date(date1);
    const secondDate = new Date(date2);
    
    return Math.round(Math.abs((firstDate - secondDate) / oneHour));
  },

  isToday: (date) => {
    const today = new Date();
    const checkDate = new Date(date);
    
    return today.getDate() === checkDate.getDate() &&
           today.getMonth() === checkDate.getMonth() &&
           today.getFullYear() === checkDate.getFullYear();
  },

  isYesterday: (date) => {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const checkDate = new Date(date);
    
    return yesterday.getDate() === checkDate.getDate() &&
           yesterday.getMonth() === checkDate.getMonth() &&
           yesterday.getFullYear() === checkDate.getFullYear();
  },

  isTomorrow: (date) => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const checkDate = new Date(date);
    
    return tomorrow.getDate() === checkDate.getDate() &&
           tomorrow.getMonth() === checkDate.getMonth() &&
           tomorrow.getFullYear() === checkDate.getFullYear();
  },

  isThisWeek: (date) => {
    const now = new Date();
    const checkDate = new Date(date);
    const weekStart = new Date(now.setDate(now.getDate() - now.getDay()));
    const weekEnd = new Date(now.setDate(now.getDate() - now.getDay() + 6));
    
    return checkDate >= weekStart && checkDate <= weekEnd;
  },

  isThisMonth: (date) => {
    const now = new Date();
    const checkDate = new Date(date);
    
    return now.getMonth() === checkDate.getMonth() &&
           now.getFullYear() === checkDate.getFullYear();
  },

  isThisYear: (date) => {
    const now = new Date();
    const checkDate = new Date(date);
    
    return now.getFullYear() === checkDate.getFullYear();
  },

  getStartOfDay: (date) => {
    const result = new Date(date);
    result.setHours(0, 0, 0, 0);
    return result;
  },

  getEndOfDay: (date) => {
    const result = new Date(date);
    result.setHours(23, 59, 59, 999);
    return result;
  },

  getStartOfWeek: (date) => {
    const result = new Date(date);
    const day = result.getDay();
    const diff = result.getDate() - day;
    return new Date(result.setDate(diff));
  },

  getEndOfWeek: (date) => {
    const result = new Date(date);
    const day = result.getDay();
    const diff = result.getDate() - day + 6;
    return new Date(result.setDate(diff));
  },

  getStartOfMonth: (date) => {
    return new Date(date.getFullYear(), date.getMonth(), 1);
  },

  getEndOfMonth: (date) => {
    return new Date(date.getFullYear(), date.getMonth() + 1, 0);
  },

  isValidDate: (date) => {
    try {
      const d = new Date(date);
      return d instanceof Date && !isNaN(d);
    } catch {
      return false;
    }
  },

  parseDate: (dateString) => {
    try {
      const date = new Date(dateString);
      if (dateUtils.isValidDate(date)) {
        return date;
      }
      return null;
    } catch {
      return null;
    }
  },

  toISOString: (date) => {
    try {
      return new Date(date).toISOString();
    } catch {
      return null;
    }
  },

  formatDuration: (milliseconds) => {
    const seconds = Math.floor(milliseconds / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (days > 0) return `${days}d ${hours % 24}h`;
    if (hours > 0) return `${hours}h ${minutes % 60}m`;
    if (minutes > 0) return `${minutes}m ${seconds % 60}s`;
    return `${seconds}s`;
  },

  getWeekNumber: (date) => {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
  },

  getQuarter: (date) => {
    const month = new Date(date).getMonth();
    return Math.floor(month / 3) + 1;
  },

  getAge: (birthDate) => {
    const today = new Date();
    const birth = new Date(birthDate);
    let age = today.getFullYear() - birth.getFullYear();
    const monthDiff = today.getMonth() - birth.getMonth();
    
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birth.getDate())) {
      age--;
    }
    
    return age;
  }
};

export const formatDateString = dateUtils.formatDateString;
export const has24HoursPassed = dateUtils.has24HoursPassed;
export default dateUtils;
