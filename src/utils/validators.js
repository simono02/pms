export const validators = {
  email: (email) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  password: (password) => {
    if (!password || password.length < 6) {
      return { valid: false, message: 'Password must be at least 6 characters long' };
    }
    
    if (!/(?=.*[a-z])/.test(password)) {
      return { valid: false, message: 'Password must contain at least one lowercase letter' };
    }
    
    if (!/(?=.*[A-Z])/.test(password)) {
      return { valid: false, message: 'Password must contain at least one uppercase letter' };
    }
    
    if (!/(?=.*\d)/.test(password)) {
      return { valid: false, message: 'Password must contain at least one number' };
    }
    
    if (!/(?=.*[@$!%*?&])/.test(password)) {
      return { valid: false, message: 'Password must contain at least one special character' };
    }
    
    return { valid: true };
  },

  name: (name) => {
    if (!name || name.trim().length < 2) {
      return { valid: false, message: 'Name must be at least 2 characters long' };
    }
    
    if (!/^[a-zA-Z\s'-]+$/.test(name)) {
      return { valid: false, message: 'Name can only contain letters, spaces, hyphens, and apostrophes' };
    }
    
    return { valid: true };
  },

  phone: (phone) => {
    const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
    if (!phoneRegex.test(phone)) {
      return { valid: false, message: 'Please enter a valid phone number' };
    }
    
    if (phone.replace(/\D/g, '').length < 10) {
      return { valid: false, message: 'Phone number must be at least 10 digits' };
    }
    
    return { valid: true };
  },

  url: (url) => {
    try {
      new URL(url);
      return { valid: true };
    } catch {
      return { valid: false, message: 'Please enter a valid URL' };
    }
  },

  required: (value) => {
    if (!value || value.toString().trim() === '') {
      return { valid: false, message: 'This field is required' };
    }
    return { valid: true };
  },

  minLength: (min) => (value) => {
    if (value && value.length < min) {
      return { valid: false, message: `Must be at least ${min} characters long` };
    }
    return { valid: true };
  },

  maxLength: (max) => (value) => {
    if (value && value.length > max) {
      return { valid: false, message: `Must be no more than ${max} characters long` };
    }
    return { valid: true };
  },

  numeric: (value) => {
    if (value && !/^\d+$/.test(value)) {
      return { valid: false, message: 'Must contain only numbers' };
    }
    return { valid: true };
  },

  decimal: (value) => {
    if (value && !/^\d*\.?\d+$/.test(value)) {
      return { valid: false, message: 'Must be a valid decimal number' };
    }
    return { valid: true };
  },

  positive: (value) => {
    const num = parseFloat(value);
    if (isNaN(num) || num <= 0) {
      return { valid: false, message: 'Must be a positive number' };
    }
    return { valid: true };
  },

  range: (min, max) => (value) => {
    const num = parseFloat(value);
    if (isNaN(num) || num < min || num > max) {
      return { valid: false, message: `Must be between ${min} and ${max}` };
    }
    return { valid: true };
  },

  file: {
    pdf: (file) => {
      if (file && file.type !== 'application/pdf') {
        return { valid: false, message: 'File must be a PDF' };
      }
      return { valid: true };
    },

    maxSize: (maxSizeMB) => (file) => {
      if (file && file.size > maxSizeMB * 1024 * 1024) {
        return { valid: false, message: `File size must be less than ${maxSizeMB}MB` };
      }
      return { valid: true };
    },

    image: (file) => {
      const validTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
      if (file && !validTypes.includes(file.type)) {
        return { valid: false, message: 'File must be an image (JPEG, PNG, GIF, or WebP)' };
      }
      return { valid: true };
    }
  },

  date: {
    past: (date) => {
      const inputDate = new Date(date);
      const now = new Date();
      if (inputDate >= now) {
        return { valid: false, message: 'Date must be in the past' };
      }
      return { valid: true };
    },

    future: (date) => {
      const inputDate = new Date(date);
      const now = new Date();
      if (inputDate <= now) {
        return { valid: false, message: 'Date must be in the future' };
      }
      return { valid: true };
    },

    minAge: (minAge) => (date) => {
      const birthDate = new Date(date);
      const now = new Date();
      const age = now.getFullYear() - birthDate.getFullYear();
      const monthDiff = now.getMonth() - birthDate.getMonth();
      
      if (monthDiff < 0 || (monthDiff === 0 && now.getDate() < birthDate.getDate())) {
        age - 1;
      }
      
      if (age < minAge) {
        return { valid: false, message: `Must be at least ${minAge} years old` };
      }
      return { valid: true };
    }
  },

  projectTitle: (title) => {
    if (!title || title.trim().length < 3) {
      return { valid: false, message: 'Project title must be at least 3 characters long' };
    }
    
    if (title.trim().length > 200) {
      return { valid: false, message: 'Project title must be no more than 200 characters' };
    }
    
    return { valid: true };
  },

  researchField: (field) => {
    const validFields = [
      'computer-science',
      'engineering',
      'medicine',
      'business',
      'education',
      'social-sciences',
      'natural-sciences',
      'other'
    ];
    
    if (!field) {
      return { valid: false, message: 'Research field is required' };
    }
    
    if (!validFields.includes(field)) {
      return { valid: false, message: 'Invalid research field' };
    }
    
    return { valid: true };
  },

  cardNumber: (number) => {
    const cleaned = number.replace(/\s/g, '');
    
    if (!/^\d{16}$/.test(cleaned)) {
      return { valid: false, message: 'Card number must be 16 digits' };
    }
    
    let sum = 0;
    let isEven = false;
    
    for (let i = cleaned.length - 1; i >= 0; i--) {
      let digit = parseInt(cleaned[i]);
      
      if (isEven) {
        digit *= 2;
        if (digit > 9) {
          digit -= 9;
        }
      }
      
      sum += digit;
      isEven = !isEven;
    }
    
    if (sum % 10 !== 0) {
      return { valid: false, message: 'Invalid card number' };
    }
    
    return { valid: true };
  },

  expiryDate: (expiry) => {
    if (!/^\d{2}\/\d{2}$/.test(expiry)) {
      return { valid: false, message: 'Expiry date must be in MM/YY format' };
    }
    
    const [month, year] = expiry.split('/').map(Number);
    
    if (month < 1 || month > 12) {
      return { valid: false, message: 'Invalid month' };
    }
    
    const now = new Date();
    const currentYear = now.getFullYear() % 100;
    const currentMonth = now.getMonth() + 1;
    
    if (year < currentYear || (year === currentYear && month < currentMonth)) {
      return { valid: false, message: 'Card has expired' };
    }
    
    return { valid: true };
  },

  cvv: (cvv) => {
    if (!/^\d{3,4}$/.test(cvv)) {
      return { valid: false, message: 'CVV must be 3 or 4 digits' };
    }
    return { valid: true };
  }
};

export const validateField = (value, rules) => {
  for (const rule of rules) {
    const result = rule(value);
    if (!result.valid) {
      return result;
    }
  }
  return { valid: true };
};

export const validateForm = (formData, validationRules) => {
  const errors = {};
  let isValid = true;

  for (const [fieldName, rules] of Object.entries(validationRules)) {
    const result = validateField(formData[fieldName], rules);
    if (!result.valid) {
      errors[fieldName] = result.message;
      isValid = false;
    }
  }

  return { isValid, errors };
};

export default validators;
