export const fileUtils = {
  getFileExtension: (filename) => {
    if (!filename) return '';
    return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
  },

  getFileName: (filepath) => {
    if (!filepath) return '';
    return filepath.split('\\').pop().split('/').pop();
  },

  getFileNameWithoutExtension: (filename) => {
    if (!filename) return '';
    const name = fileUtils.getFileName(filename);
    const extension = fileUtils.getFileExtension(name);
    return name.replace(`.${extension}`, '');
  },

  formatFileSize: (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  },

  isValidFileType: (file, allowedTypes) => {
    if (!file || !allowedTypes) return false;
    return allowedTypes.includes(file.type);
  },

  isValidFileSize: (file, maxSizeMB) => {
    if (!file || !maxSizeMB) return false;
    const maxSizeBytes = maxSizeMB * 1024 * 1024;
    return file.size <= maxSizeBytes;
  },

  isPDF: (file) => {
    return file && file.type === 'application/pdf';
  },

  isImage: (file) => {
    const imageTypes = [
      'image/jpeg',
      'image/png',
      'image/gif',
      'image/webp',
      'image/svg+xml'
    ];
    return file && imageTypes.includes(file.type);
  },

  isDocument: (file) => {
    const documentTypes = [
      'application/pdf',
      'application/msword',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
      'application/vnd.ms-excel',
      'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
      'application/vnd.ms-powerpoint',
      'application/vnd.openxmlformats-officedocument.presentationml.presentation',
      'text/plain'
    ];
    return file && documentTypes.includes(file.type);
  },

  generateUniqueFileName: (originalName) => {
    const timestamp = Date.now();
    const randomString = Math.random().toString(36).substring(2, 8);
    const extension = fileUtils.getFileExtension(originalName);
    const nameWithoutExt = fileUtils.getFileNameWithoutExtension(originalName);
    
    return `${nameWithoutExt}_${timestamp}_${randomString}.${extension}`;
  },

  sanitizeFileName: (filename) => {
    if (!filename) return '';
    
    return filename
      .replace(/[^a-zA-Z0-9.-]/g, '_')
      .replace(/_{2,}/g, '_')
      .replace(/^_+|_+$/g, '');
  },

  createFilePreview: (file) => {
    return new Promise((resolve, reject) => {
      if (!file) {
        reject(new Error('No file provided'));
        return;
      }

      if (fileUtils.isImage(file)) {
        const reader = new FileReader();
        reader.onload = (e) => resolve(e.target.result);
        reader.onerror = (e) => reject(e);
        reader.readAsDataURL(file);
      } else {
        resolve(null);
      }
    });
  },

  downloadFile: (url, filename) => {
    const link = document.createElement('a');
    link.href = url;
    link.download = filename || 'download';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  },

  downloadBlob: (blob, filename) => {
    const url = window.URL.createObjectURL(blob);
    fileUtils.downloadFile(url, filename);
    window.URL.revokeObjectURL(url);
  },

  readFileAsText: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsText(file);
    });
  },

  readFileAsDataURL: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsDataURL(file);
    });
  },

  readFileAsArrayBuffer: (file) => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload = (e) => resolve(e.target.result);
      reader.onerror = (e) => reject(e);
      reader.readAsArrayBuffer(file);
    });
  },

  compressImage: (file, quality = 0.7, maxWidth = 1920, maxHeight = 1080) => {
    return new Promise((resolve) => {
      if (!fileUtils.isImage(file)) {
        resolve(file);
        return;
      }

      const canvas = document.createElement('canvas');
      const ctx = canvas.getContext('2d');
      const img = new Image();

      img.onload = () => {
        let { width, height } = img;

        if (width > maxWidth) {
          height = (maxWidth / width) * height;
          width = maxWidth;
        }

        if (height > maxHeight) {
          width = (maxHeight / height) * width;
          height = maxHeight;
        }

        canvas.width = width;
        canvas.height = height;

        ctx.drawImage(img, 0, 0, width, height);

        canvas.toBlob(
          (blob) => {
            const compressedFile = new File([blob], file.name, {
              type: file.type,
              lastModified: Date.now()
            });
            resolve(compressedFile);
          },
          file.type,
          quality
        );
      };

      img.src = URL.createObjectURL(file);
    });
  },

  validateFile: (file, rules = {}) => {
    const errors = [];
    const {
      maxSizeMB = 10,
      allowedTypes = [],
      requiredExtensions = [],
      minSizeMB = 0
    } = rules;

    if (!file) {
      errors.push('No file provided');
      return { valid: false, errors };
    }

    if (file.size < minSizeMB * 1024 * 1024) {
      errors.push(`File size must be at least ${minSizeMB}MB`);
    }

    if (file.size > maxSizeMB * 1024 * 1024) {
      errors.push(`File size must be less than ${maxSizeMB}MB`);
    }

    if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
      errors.push(`File type must be one of: ${allowedTypes.join(', ')}`);
    }

    if (requiredExtensions.length > 0) {
      const extension = fileUtils.getFileExtension(file.name).toLowerCase();
      if (!requiredExtensions.includes(extension)) {
        errors.push(`File extension must be one of: ${requiredExtensions.join(', ')}`);
      }
    }

    return {
      valid: errors.length === 0,
      errors
    };
  },

  getFileIcon: (filename) => {
    if (!filename) return 'file';
    
    const extension = fileUtils.getFileExtension(filename).toLowerCase();
    
    const iconMap = {
      pdf: 'file-pdf',
      doc: 'file-word',
      docx: 'file-word',
      xls: 'file-excel',
      xlsx: 'file-excel',
      ppt: 'file-powerpoint',
      pptx: 'file-powerpoint',
      txt: 'file-text',
      jpg: 'file-image',
      jpeg: 'file-image',
      png: 'file-image',
      gif: 'file-image',
      svg: 'file-image',
      zip: 'file-archive',
      rar: 'file-archive',
      '7z': 'file-archive'
    };
    
    return iconMap[extension] || 'file';
  },

  formatFilePermissions: (permissions) => {
    if (!permissions) return '';
    
    const { readable, writable, executable } = permissions;
    let result = '';
    
    result += readable ? 'r' : '-';
    result += writable ? 'w' : '-';
    result += executable ? 'x' : '-';
    
    return result;
  },

  createFormData: (data, fileKey = 'file') => {
    const formData = new FormData();
    
    for (const [key, value] of Object.entries(data)) {
      if (value instanceof File) {
        formData.append(key, value);
      } else if (Array.isArray(value)) {
        value.forEach((item, index) => {
          formData.append(`${key}[${index}]`, item);
        });
      } else if (typeof value === 'object' && value !== null) {
        formData.append(key, JSON.stringify(value));
      } else {
        formData.append(key, value);
      }
    }
    
    return formData;
  },

  extractFileMetadata: async (file) => {
    const metadata = {
      name: file.name,
      size: file.size,
      type: file.type,
      lastModified: file.lastModified,
      extension: fileUtils.getFileExtension(file.name)
    };

    if (fileUtils.isImage(file)) {
      try {
        const dimensions = await fileUtils.getImageDimensions(file);
        metadata.width = dimensions.width;
        metadata.height = dimensions.height;
        metadata.aspectRatio = dimensions.width / dimensions.height;
      } catch (error) {
        console.warn('Could not extract image dimensions:', error);
      }
    }

    return metadata;
  },

  getImageDimensions: (file) => {
    return new Promise((resolve, reject) => {
      const img = new Image();
      img.onload = () => {
        resolve({
          width: img.width,
          height: img.height
        });
      };
      img.onerror = reject;
      img.src = URL.createObjectURL(file);
    });
  },

  calculateFileHash: async (file) => {
    const buffer = await fileUtils.readFileAsArrayBuffer(file);
    const hashBuffer = await crypto.subtle.digest('SHA-256', buffer);
    const hashArray = Array.from(new Uint8Array(hashBuffer));
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join('');
    return hashHex;
  }
};

export default fileUtils;
