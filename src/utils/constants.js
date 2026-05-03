export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    VERIFY_EMAIL: '/auth/verify-email',
    FORGOT_PASSWORD: '/auth/forgot-password',
    RESET_PASSWORD: '/auth/reset-password',
    CHANGE_PASSWORD: '/auth/change-password'
  },
  USER: {
    PROFILE: '/user/profile',
    PROJECTS: '/user/projects',
    NOTIFICATIONS: '/user/notifications',
    SETTINGS: '/user/settings',
    AVATAR: '/user/avatar'
  },
  PROJECTS: {
    BASE: '/projects',
    BY_ID: (id) => `/projects/${id}`,
    DESCRIBE: (id) => `/projects/${id}/describe`,
    PREVIEW: (id) => `/projects/${id}/preview`,
    DOWNLOAD: (id) => `/projects/${id}/download`,
    STATUS: (id) => `/projects/${id}/status`,
    HISTORY: (id) => `/projects/${id}/history`,
    SEARCH: '/projects/search',
    ARCHIVED: '/projects/archived',
    STATS: '/projects/stats'
  },
  STAFF: {
    PROFILE: '/staff/profile',
    PROJECTS: '/staff/projects',
    NOTIFICATIONS: '/staff/notifications',
    DASHBOARD: '/staff/dashboard',
    PERFORMANCE: '/staff/performance',
    AVAILABLE_PROJECTS: '/staff/available-projects',
    WORKLOAD: '/staff/workload',
    SKILLS: '/staff/skills',
    REVIEWS: '/staff/reviews',
    EARNINGS: '/staff/earnings'
  },
  ADMIN: {
    DASHBOARD: '/admin/dashboard',
    CLIENTS: '/admin/clients',
    STAFF: '/admin/staff',
    PROJECTS: '/admin/projects',
    PAYMENTS: '/admin/payments',
    ANALYTICS: '/admin/analytics',
    LOGS: '/admin/logs',
    SETTINGS: '/admin/settings',
    HEALTH: '/admin/health',
    BACKUP: '/admin/backup'
  },
  PAYMENTS: {
    PROCESS: (id) => `/payments/process/${id}`,
    VERIFY: (id) => `/payments/verify/${id}`,
    STATUS: (id) => `/payments/status/${id}`,
    HISTORY: '/payments/history',
    METHODS: '/payments/methods',
    INVOICES: '/payments/invoices',
    DISCOUNTS: '/payments/discounts',
    SUBSCRIPTIONS: '/payments/subscriptions',
    STATS: '/payments/stats'
  },
  FILES: {
    UPLOAD: '/files/upload',
    DOWNLOAD: (id) => `/files/download/${id}`,
    BY_ID: (id) => `/files/${id}`,
    PREVIEW: (id) => `/files/${id}/preview`,
    THUMBNAIL: (id) => `/files/${id}/thumbnail`,
    COMPRESS: (id) => `/files/${id}/compress`,
    CONVERT_PDF: (id) => `/files/${id}/convert-pdf`,
    MERGE: '/files/merge',
    SPLIT: (id) => `/files/${id}/split`,
    VALIDATE: (id) => `/files/${id}/validate`,
    METADATA: (id) => `/files/${id}/metadata`,
    SEARCH: '/files/search',
    STORAGE_USAGE: '/files/storage-usage'
  }
};

export const USER_ROLES = {
  USER: 'user',
  STAFF: 'staff',
  ADMIN: 'admin'
};

export const PROJECT_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  PAYMENT_REQUIRED: 'payment_required',
  CANCELLED: 'cancelled',
  ARCHIVED: 'archived'
};

export const PAYMENT_STATUS = {
  PENDING: 'pending',
  PROCESSING: 'processing',
  COMPLETED: 'completed',
  FAILED: 'failed',
  REFUNDED: 'refunded',
  CANCELLED: 'cancelled'
};

export const NOTIFICATION_TYPES = {
  PROJECT_ASSIGNED: 'project_assigned',
  PROJECT_COMPLETED: 'project_completed',
  PAYMENT_RECEIVED: 'payment_received',
  SYSTEM_UPDATE: 'system_update',
  MESSAGE: 'message',
  REMINDER: 'reminder'
};

export const RESEARCH_FIELDS = {
  COMPUTER_SCIENCE: 'computer-science',
  ENGINEERING: 'engineering',
  MEDICINE: 'medicine',
  BUSINESS: 'business',
  EDUCATION: 'education',
  SOCIAL_SCIENCES: 'social-sciences',
  NATURAL_SCIENCES: 'natural-sciences',
  OTHER: 'other'
};

export const FILE_TYPES = {
  PDF: 'application/pdf',
  DOC: 'application/msword',
  DOCX: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  XLS: 'application/vnd.ms-excel',
  XLSX: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  PPT: 'application/vnd.ms-powerpoint',
  PPTX: 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
  TXT: 'text/plain',
  JPEG: 'image/jpeg',
  PNG: 'image/png',
  GIF: 'image/gif',
  WEBP: 'image/webp',
  SVG: 'image/svg+xml',
  ZIP: 'application/zip',
  RAR: 'application/x-rar-compressed'
};

export const MAX_FILE_SIZES = {
  PROJECT_PDF: 10 * 1024 * 1024, // 10MB
  RESULT_PDF: 20 * 1024 * 1024, // 20MB
  AVATAR: 2 * 1024 * 1024, // 2MB
  GENERAL: 5 * 1024 * 1024 // 5MB
};

export const DATE_FORMATS = {
  SHORT: 'MM/dd/yyyy',
  MEDIUM: 'MMM dd, yyyy',
  LONG: 'MMMM dd, yyyy',
  FULL: 'EEEE, MMMM dd, yyyy',
  TIME_ONLY: 'h:mm a',
  DATE_TIME: 'MMM dd, yyyy h:mm a',
  ISO: 'yyyy-MM-dd\'T\'HH:mm:ss'
};

export const THEME_OPTIONS = {
  LIGHT: 'light',
  DARK: 'dark',
  AUTO: 'auto'
};

export const FONT_SIZES = {
  SMALL: 'small',
  MEDIUM: 'medium',
  LARGE: 'large',
  EXTRA_LARGE: 'extra-large'
};

export const LANGUAGES = {
  EN: 'en',
  ES: 'es',
  FR: 'fr',
  DE: 'de',
  IT: 'it',
  PT: 'pt',
  RU: 'ru',
  ZH: 'zh',
  JA: 'ja',
  KO: 'ko'
};

export const PAGINATION = {
  DEFAULT_PAGE_SIZE: 10,
  MAX_PAGE_SIZE: 100,
  PAGE_SIZES: [10, 25, 50, 100]
};

export const SORT_OPTIONS = {
  DATE_CREATED: 'created_at',
  DATE_UPDATED: 'updated_at',
  NAME: 'name',
  STATUS: 'status',
  PRIORITY: 'priority'
};

export const SORT_DIRECTIONS = {
  ASC: 'asc',
  DESC: 'desc'
};

export const FILTER_OPERATORS = {
  EQUALS: 'eq',
  NOT_EQUALS: 'ne',
  GREATER_THAN: 'gt',
  GREATER_THAN_OR_EQUAL: 'gte',
  LESS_THAN: 'lt',
  LESS_THAN_OR_EQUAL: 'lte',
  CONTAINS: 'contains',
  STARTS_WITH: 'starts_with',
  ENDS_WITH: 'ends_with',
  IN: 'in',
  NOT_IN: 'not_in'
};

export const VALIDATION_RULES = {
  NAME_MIN_LENGTH: 2,
  NAME_MAX_LENGTH: 100,
  PASSWORD_MIN_LENGTH: 6,
  PASSWORD_MAX_LENGTH: 128,
  TITLE_MIN_LENGTH: 3,
  TITLE_MAX_LENGTH: 200,
  DESCRIPTION_MIN_LENGTH: 10,
  DESCRIPTION_MAX_LENGTH: 2000,
  EMAIL_MAX_LENGTH: 254,
  PHONE_MIN_LENGTH: 10,
  PHONE_MAX_LENGTH: 20
};

export const ANIMATION_DURATIONS = {
  FAST: 150,
  NORMAL: 300,
  SLOW: 500
};

export const BREAKPOINTS = {
  XS: 0,
  SM: 576,
  MD: 768,
  LG: 992,
  XL: 1200,
  XXL: 1400
};

export const COLORS = {
  PRIMARY: '#007bff',
  SECONDARY: '#6c757d',
  SUCCESS: '#28a745',
  DANGER: '#dc3545',
  WARNING: '#ffc107',
  INFO: '#17a2b8',
  LIGHT: '#f8f9fa',
  DARK: '#343a40'
};

export const STATUS_COLORS = {
  [PROJECT_STATUS.PENDING]: '#ffc107',
  [PROJECT_STATUS.IN_PROGRESS]: '#17a2b8',
  [PROJECT_STATUS.COMPLETED]: '#28a745',
  [PROJECT_STATUS.PAYMENT_REQUIRED]: '#dc3545',
  [PROJECT_STATUS.CANCELLED]: '#6c757d',
  [PROJECT_STATUS.ARCHIVED]: '#343a40'
};

export const PAYMENT_METHODS = {
  CREDIT_CARD: 'credit_card',
  DEBIT_CARD: 'debit_card',
  PAYPAL: 'paypal',
  STRIPE: 'stripe',
  BANK_TRANSFER: 'bank_transfer'
};

export const EXPORT_FORMATS = {
  CSV: 'csv',
  EXCEL: 'excel',
  PDF: 'pdf',
  JSON: 'json'
};

export const TIME_RANGES = {
  TODAY: 'today',
  WEEK: 'week',
  MONTH: 'month',
  QUARTER: 'quarter',
  YEAR: 'year',
  ALL_TIME: 'all'
};

export const CHART_TYPES = {
  LINE: 'line',
  BAR: 'bar',
  PIE: 'pie',
  DOUGHNUT: 'doughnut',
  AREA: 'area',
  SCATTER: 'scatter'
};

export const ERROR_CODES = {
  VALIDATION_ERROR: 'VALIDATION_ERROR',
  AUTHENTICATION_ERROR: 'AUTHENTICATION_ERROR',
  AUTHORIZATION_ERROR: 'AUTHORIZATION_ERROR',
  NOT_FOUND: 'NOT_FOUND',
  SERVER_ERROR: 'SERVER_ERROR',
  NETWORK_ERROR: 'NETWORK_ERROR',
  TIMEOUT_ERROR: 'TIMEOUT_ERROR'
};

export const LOCAL_STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  THEME: 'theme',
  SETTINGS: 'settings',
  LANGUAGE: 'language',
  SIDEBAR_COLLAPSED: 'sidebar_collapsed'
};

export const SESSION_STORAGE_KEYS = {
  REDIRECT_URL: 'redirect_url',
  FORM_DATA: 'form_data',
  TEMP_UPLOADS: 'temp_uploads'
};

export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^\+?[\d\s\-\(\)]+$/,
  PASSWORD: /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{6,}$/,
  URL: /^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$/,
  CARD_NUMBER: /^\d{16}$/,
  CVV: /^\d{3,4}$/,
  EXPIRY_DATE: /^(0[1-9]|1[0-2])\/\d{2}$/
};

export default {
  API_ENDPOINTS,
  USER_ROLES,
  PROJECT_STATUS,
  PAYMENT_STATUS,
  NOTIFICATION_TYPES,
  RESEARCH_FIELDS,
  FILE_TYPES,
  MAX_FILE_SIZES,
  DATE_FORMATS,
  THEME_OPTIONS,
  FONT_SIZES,
  LANGUAGES,
  PAGINATION,
  SORT_OPTIONS,
  SORT_DIRECTIONS,
  FILTER_OPERATORS,
  VALIDATION_RULES,
  ANIMATION_DURATIONS,
  BREAKPOINTS,
  COLORS,
  STATUS_COLORS,
  PAYMENT_METHODS,
  EXPORT_FORMATS,
  TIME_RANGES,
  CHART_TYPES,
  ERROR_CODES,
  LOCAL_STORAGE_KEYS,
  SESSION_STORAGE_KEYS,
  REGEX_PATTERNS
};
